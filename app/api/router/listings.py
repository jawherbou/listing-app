from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas.listings_get import ListingsResponse, ListingFilters
from app.api.schemas.listings_insert import ListingsInsertRequest
from app.models.database import get_db

router = APIRouter()

@router.get("/listings", response_model=ListingsResponse)
def retrieve_listings(
    filters: ListingFilters = Depends(),
    db: Session = Depends(get_db),
):
    print(filters)
    return {'total': 0, 'listings': []}


@router.post("/upsert")
def upsert_listings_endpoint(
    payload: ListingsInsertRequest,
    db: Session = Depends(get_db)
):
    return {"message": "Listings inserted/updated successfully."}
