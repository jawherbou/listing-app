from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models import schemas as models

def seed_data():
    db: Session = SessionLocal()

    # --- Dataset Entities ---
    dataset_entities = [
        {"entity_id": 1, "name": "entity_one", "data": {"key1": "value1", "key2": 123}},
        {"entity_id": 2, "name": "entity_two", "data": {"key3": True, "key4": None}},
        {"entity_id": 3, "name": "entity_three", "data": {"key5": "another value", "key6": False}},
    ]

    for ent in dataset_entities:
        existing = db.query(models.DatasetEntity).filter_by(entity_id=ent["entity_id"]).first()
        if not existing:
            db.add(models.DatasetEntity(**ent))

    # --- Properties ---
    properties = [
        {"property_id": 123, "name": "some str property", "type": "string"},
        {"property_id": 456, "name": "some bool property", "type": "boolean"},
    ]

    for prop in properties:
        existing = db.query(models.Property).filter_by(property_id=prop["property_id"]).first()
        if not existing:
            db.add(models.Property(**prop))

    # --- Listings ---
    listings = [
        {
            "listing_id": "1111223",
            "scan_date": "2024-10-22 12:00:00",
            "is_active": True,
            "dataset_entity_ids": [1, 2],
            "image_hashes": ["2e32d2", "f54t45r"],
        },
        {
            "listing_id": "1111224",
            "scan_date": "2024-10-23 14:30:00",
            "is_active": False,
            "dataset_entity_ids": [3],
            "image_hashes": ["a1b2c3"],
        },
    ]

    for lst in listings:
        existing = db.query(models.Listing).filter_by(listing_id=lst["listing_id"]).first()
        if not existing:
            db.add(models.Listing(**lst))

    # --- Property Values: String ---
    if not db.query(models.StringPropertyValue).filter_by(listing_id="1111223", property_id=123).first():
        db.add(models.StringPropertyValue(
            listing_id="1111223", property_id=123, value="str value"
        ))

    # --- Property Values: Boolean ---
    if not db.query(models.BoolPropertyValue).filter_by(listing_id="1111223", property_id=456).first():
        db.add(models.BoolPropertyValue(
            listing_id="1111223", property_id=456, value=False
        ))

    db.commit()
    db.close()
    print("Seed data inserted.")


if __name__ == "__main__":
    seed_data()
