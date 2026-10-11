from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Category(StrEnum):
    chiller = "chiller"
    compressor = "compressor"
    heat_exchanger = "heat_exchanger"
    circulator_pump = "circulator_pump"
    fan_coil = "fan_coil"


class EquipmentBase(BaseModel):
    model: str = Field(max_length=80)
    manufacturer: str = Field(max_length=80)
    category: Category
    refrigerant: str = Field(max_length=20)
    capacity_kw: float = Field(gt=0)
    power_input_kw: float = Field(gt=0)
    voltage: str = Field(max_length=20)
    sound_pressure_db: float = Field(ge=0)
    weight_kg: float = Field(gt=0)
    price_eur: float = Field(ge=0)


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentRead(EquipmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cop: float


class EquipmentPage(BaseModel):
    items: list[EquipmentRead]
    total: int
    limit: int
    offset: int


class ComparisonRow(BaseModel):
    field: str
    values: dict[str, float | str | None]
    best: str | None


class Comparison(BaseModel):
    models: list[str]
    rows: list[ComparisonRow]
