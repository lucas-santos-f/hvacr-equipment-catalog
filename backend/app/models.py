from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    manufacturer: Mapped[str] = mapped_column(String(80), index=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    refrigerant: Mapped[str] = mapped_column(String(20), index=True)
    capacity_kw: Mapped[float] = mapped_column(Float, index=True)
    power_input_kw: Mapped[float] = mapped_column(Float)
    voltage: Mapped[str] = mapped_column(String(20))
    sound_pressure_db: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    price_eur: Mapped[float] = mapped_column(Float)

    @property
    def cop(self) -> float:
        if self.power_input_kw <= 0:
            return 0.0
        return round(self.capacity_kw / self.power_input_kw, 2)
