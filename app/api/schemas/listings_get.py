from enum import Enum
from typing import Optional, List, Dict, Union, Any
from pydantic import BaseModel
from datetime import datetime


class PropertyType(str, Enum):
    string = "str"
    boolean = "bool"


class ListingPropertySchema(BaseModel):
    name: str
    type: PropertyType  # 'str' or 'bool'
    value: Union[str, bool]


class DatasetEntitySchema(BaseModel):
    name: str
    data: Dict[str, Any]


class ListingResponseSchema(BaseModel):
    listing_id: str
    scan_date: datetime
    is_active: bool
    dataset_entity_ids: List[int]
    image_hashes: List[str]
    properties: List[ListingPropertySchema]
    entities: List[DatasetEntitySchema]


class ListingsResponse(BaseModel):
    total: int
    listings: List[ListingResponseSchema]


class ListingFilters(BaseModel):
    page: Optional[int] = 1
    listing_id: Optional[str] = None
    scan_date_from: Optional[datetime] = None
    scan_date_to: Optional[datetime] = None
    is_active: Optional[bool] = None
    image_hashes: Optional[List[str]] = None
    dataset_entities: Optional[Dict[str, Any]] = None
    property_filters: Optional[Dict[int, Union[str, bool]]] = None
