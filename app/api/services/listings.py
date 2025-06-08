from typing import Dict, Any
from sqlalchemy.orm import Session
from app.api.schemas.listings_insert import ListingsInsertRequest
from app.models.schemas import (
    Listing,
    StringPropertyValue,
    BoolPropertyValue,
    DatasetEntity,
    Property,
)
from app.api.schemas.listings_get import ListingsResponse, ListingFilters
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import any_, cast, or_


def get_listings(
    db: Session,
    filters: ListingFilters
) -> Dict[str, Any]:
    query = db.query(Listing)

    # filters on Listings table
    if filters.listing_id:
        query = query.filter(Listing.listing_id == filters.listing_id)

    if filters.scan_date_from:
        query = query.filter(Listing.scan_date >= filters.scan_date_from)

    if filters.scan_date_to:
        query = query.filter(Listing.scan_date <= filters.scan_date_to)

    if filters.is_active is not None:
        query = query.filter(Listing.is_active == filters.is_active)

    if filters.image_hashes:
        # any overlap between image_hashes arrays
        query = query.filter(
            #Listing.image_hashes.overlap(filters.image_hashes)
            or_(*(image_hash == any_(Listing.image_hashes) for image_hash in filters.image_hashes))
        )

    if filters.dataset_entities:
        # step 1: find all entity_ids whose `data` JSON contains the given dataset_entities dict
        matching_entities = db.query(DatasetEntity.entity_id).filter(
            cast(DatasetEntity.data, JSONB).op('@>')(filters.dataset_entities)
        ).all()
        matching_entity_ids = [e[0] for e in matching_entities]

        if matching_entity_ids:
            # step 2: filter listings whose dataset_entity_ids array overlaps with these matching entity_ids
            query = query.filter(Listing.dataset_entity_ids.overlap(matching_entity_ids))
        else:
            # if no entities match, return early with empty result
            return ListingsResponse(listings=[], total=0)

    if filters.property_filters:
        listing_ids_sets = []

        for prop_id, expected_value in filters.property_filters.items():
            if isinstance(expected_value, str):
                subquery = db.query(StringPropertyValue.listing_id).filter(
                    StringPropertyValue.property_id == prop_id,
                    StringPropertyValue.value == expected_value
                )
            elif isinstance(expected_value, bool):
                subquery = db.query(BoolPropertyValue.listing_id).filter(
                    BoolPropertyValue.property_id == prop_id,
                    BoolPropertyValue.value == expected_value
                )
            else:
                continue  # skip unsupported types

            listing_ids = {row[0] for row in subquery.all()}
            listing_ids_sets.append(listing_ids)

        # only keep listings that match all property filters
        if listing_ids_sets:
            matching_ids = set.intersection(*listing_ids_sets)
            query = query.filter(Listing.listing_id.in_(matching_ids))


    listings = query.order_by(Listing.listing_id).offset((filters.page - 1) * 100).limit(100).all()
    total_count = query.count()

    results = []

    for listing in listings:
        # collect properties
        properties = []
        # string properties
        str_props = db.query(Property, StringPropertyValue).join(
            StringPropertyValue, Property.property_id == StringPropertyValue.property_id
        ).filter(StringPropertyValue.listing_id == listing.listing_id).all()

        for prop, val in str_props:
            properties.append({
                "name": prop.name,
                "type": "str",
                "value": val.value
            })

        # boolean properties
        bool_props = db.query(Property, BoolPropertyValue).join(
            BoolPropertyValue, Property.property_id == BoolPropertyValue.property_id
        ).filter(BoolPropertyValue.listing_id == listing.listing_id).all()

        for prop, val in bool_props:
            properties.append({
                "name": prop.name,
                "type": "bool",
                "value": val.value
            })

        # dataset entities
        entities = db.query(DatasetEntity).filter(
            DatasetEntity.entity_id.in_(listing.dataset_entity_ids)
        ).all()

        entities_data = [
            {
                "name": entity.name,
                "data": entity.data
            } for entity in entities
        ]

        results.append({
            "listing_id": listing.listing_id,
            "scan_date": listing.scan_date,
            "is_active": listing.is_active,
            "dataset_entity_ids": listing.dataset_entity_ids,
            "image_hashes": listing.image_hashes,
            "properties": properties,
            "entities": entities_data
        })

    return ListingsResponse(listings=results, total=total_count)


def upsert_listings( db: Session, data: ListingsInsertRequest):
    for listing in data.listings:
        # upsert Listing
        existing_listing = db.query(Listing).filter_by(listing_id=listing.listing_id).first()

        # resolve entities first to get their IDs
        entity_ids = []
        for entity in listing.entities:
            entity_obj = db.query(DatasetEntity).filter_by(name=entity.name).first()
            if not entity_obj:
                entity_obj = DatasetEntity(name=entity.name, data=entity.data)
                db.add(entity_obj)
                db.flush()
            else:
                # update data if changed
                if entity_obj.data != entity.data:
                    entity_obj.data = entity.data
            entity_ids.append(entity_obj.entity_id)

        if not existing_listing:
            new_listing = Listing(
                listing_id=listing.listing_id,
                scan_date=listing.scan_date,
                is_active=listing.is_active,
                image_hashes=listing.image_hashes,
                dataset_entity_ids=entity_ids,
            )
            db.add(new_listing)
        else:
            existing_listing.scan_date = listing.scan_date
            existing_listing.is_active = listing.is_active
            existing_listing.image_hashes = listing.image_hashes
            existing_listing.dataset_entity_ids = entity_ids

        db.flush()

        # handle properties
        for prop in listing.properties:
            # upsert property definition
            prop_obj = db.query(Property).filter_by(name=prop.name).first()
            if not prop_obj:
                prop_obj = Property(name=prop.name, type='string' if prop.type == 'str' else 'boolean')
                db.add(prop_obj)
                db.flush()

            # upsert property value
            if prop.type == 'str':
                existing_val = db.query(StringPropertyValue).filter_by(
                    listing_id=listing.listing_id, property_id=prop_obj.property_id
                ).first()
                if not existing_val:
                    db.add(StringPropertyValue(
                        listing_id=listing.listing_id,
                        property_id=prop_obj.property_id,
                        value=prop.value
                    ))
                else:
                    existing_val.value = prop.value
            elif prop.type == 'bool':
                existing_val = db.query(BoolPropertyValue).filter_by(
                    listing_id=listing.listing_id, property_id=prop_obj.property_id
                ).first()
                if not existing_val:
                    db.add(BoolPropertyValue(
                        listing_id=listing.listing_id,
                        property_id=prop_obj.property_id,
                        value=prop.value
                    ))
                else:
                    existing_val.value = prop.value

        db.commit()