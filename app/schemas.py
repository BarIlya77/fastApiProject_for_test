from pydantic import BaseModel
from typing import List, Optional


class PhoneBase(BaseModel):
    number: str


class PhoneCreate(PhoneBase):
    pass


class Phone(PhoneBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    building_id: int


class Organization(OrganizationBase):
    id: int
    building: "Building"
    phones: List["Phone"] = []
    activities: List["Activity"] = []

    class Config:
        from_attributes = True
