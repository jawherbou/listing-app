from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.api.schemas.listings_get import ListingsResponse, ListingFilters
from app.api.schemas.listings_insert import ListingsInsertRequest
from app.api.services.listings import get_listings, upsert_listings
from app.models.database import get_db

router = APIRouter()

@router.get("/listings", response_model=ListingsResponse)
def retrieve_listings(
    page: int = Query(1, ge=1),
    listing_id: Optional[str] = Query(None),
    scan_date_from: Optional[str] = Query(None),
    scan_date_to: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    image_hashes: Optional[List[str]] = Query(None),
    dataset_entities: Optional[str] = Query(None, description="JSON string"),
    property_filters: Optional[str] = Query(None, description="JSON string"),
    db: Session = Depends(get_db),
):
    try:
        import json
        from datetime import datetime

        # parse dates if provided
        scan_date_from_dt = datetime.fromisoformat(scan_date_from) if scan_date_from else None
        scan_date_to_dt = datetime.fromisoformat(scan_date_to) if scan_date_to else None

        # parse JSON filters if provided
        dataset_entities_dict = json.loads(dataset_entities) if dataset_entities else None
        property_filters_dict = json.loads(property_filters) if property_filters else None

        filters = ListingFilters(
            page=page,
            listing_id=listing_id,
            scan_date_from=scan_date_from_dt,
            scan_date_to=scan_date_to_dt,
            is_active=is_active,
            image_hashes=image_hashes,
            dataset_entities=dataset_entities_dict,
            property_filters=property_filters_dict
        )

        result = get_listings(
            db=db,
            filters=filters
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input: {ve}")
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.errors())
    except SQLAlchemyError as db_err:
        raise HTTPException(status_code=500, detail=f"Database error occurred. {str(db_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.put("/upsert")
def upsert_listings_endpoint(
    payload: ListingsInsertRequest,
    db: Session = Depends(get_db)
):
    try:
        upsert_listings(db, payload)
        return {"message": "Listings inserted/updated successfully."}
    except ValidationError as ve:
        db.rollback()
        raise HTTPException(status_code=422, detail=ve.errors())
    except SQLAlchemyError as db_err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during upsert. {str(db_err)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

