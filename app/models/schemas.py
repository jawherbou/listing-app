from sqlalchemy import (
    CheckConstraint,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Listing(Base):
    __tablename__ = "test_listings"

    listing_id = Column(String, primary_key=True, index=True)
    scan_date = Column(DateTime)
    is_active = Column(Boolean)
    dataset_entity_ids = Column(ARRAY(Integer))
    image_hashes = Column(ARRAY(String))

    # relationships (not FK-based due to array)
    str_properties = relationship("StringPropertyValue", back_populates="listing")
    bool_properties = relationship("BoolPropertyValue", back_populates="listing")


class Property(Base):
    __tablename__ = "test_properties"

    property_id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)

    # type must be either 'string' or 'boolean'
    __table_args__ = (
        CheckConstraint(
            "type IN ('string', 'boolean')", name="check_property_type"
        ),
    )


class StringPropertyValue(Base):
    __tablename__ = "test_property_values_str"

    listing_id = Column(String, ForeignKey("test_listings.listing_id"), primary_key=True)
    property_id = Column(Integer, ForeignKey("test_properties.property_id"), primary_key=True)
    value = Column(String)

    listing = relationship("Listing", back_populates="str_properties")
    property = relationship("Property")


class BoolPropertyValue(Base):
    __tablename__ = "test_property_values_bool"

    listing_id = Column(String, ForeignKey("test_listings.listing_id"), primary_key=True)
    property_id = Column(Integer, ForeignKey("test_properties.property_id"), primary_key=True)
    value = Column(Boolean)

    listing = relationship("Listing", back_populates="bool_properties")
    property = relationship("Property")


class DatasetEntity(Base):
    __tablename__ = "test_dataset_entities"

    entity_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    data = Column(JSON)
