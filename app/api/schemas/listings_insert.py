from enum import Enum
from typing import List, Union, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class PropertyType(str, Enum):
    string = "str"
    boolean = "bool"


class InsertPropertySchema(BaseModel):
    name: str
    type: PropertyType  # 'str' or 'bool'
    value: Union[str, bool]


class InsertEntitySchema(BaseModel):
    name: str
    data: Dict[str, Any]


class InsertListingSchema(BaseModel):
    listing_id: str
    scan_date: datetime
    is_active: bool
    image_hashes: List[str]
    properties: List[InsertPropertySchema]
    entities: List[InsertEntitySchema]


class ListingsInsertRequest(BaseModel):
    listings: List[InsertListingSchema]