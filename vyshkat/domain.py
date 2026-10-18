"""Объекты парка и два независимых интерфейса."""

from dataclasses import dataclass
from math import isfinite
from typing import Protocol, runtime_checkable


class InventoryItem(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def inventory_number(self) -> str: ...


@runtime_checkable
class EnergyConsumer(Protocol):
    @property
    def daily_energy_kwh(self) -> float: ...


@dataclass(frozen=True)
class Asset:
    name: str
    inventory_number: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Наименование не должно быть пустым.")
        if not isinstance(self.inventory_number, str) or not self.inventory_number.strip():
            raise ValueError("Инвентарный номер не должен быть пустым.")
        if self.inventory_number != self.inventory_number.strip():
            raise ValueError("Инвентарный номер не должен иметь пробелы по краям.")


@dataclass(frozen=True)
class Transport(Asset):
    beginner_ease: int
    brakes_working: bool = True
    frame_intact: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        if type(self.beginner_ease) is not int or not 1 <= self.beginner_ease <= 10:
            raise ValueError("Простота для новичка должна быть целым числом от 1 до 10.")
        if type(self.brakes_working) is not bool or type(self.frame_intact) is not bool:
            raise ValueError("Признаки исправности должны быть логическими значениями.")


class Bicycle(Transport):
    """Велосипед без электрического привода."""


def validate_energy(value: float) -> None:
    try:
        valid = type(value) in (int, float) and isfinite(value) and value >= 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError("Суточная энергия должна быть конечным неотрицательным числом.")


@dataclass(frozen=True)
class ElectricTransport(Transport):
    daily_energy_kwh: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()
        validate_energy(self.daily_energy_kwh)


class Scooter(ElectricTransport):
    """Электросамокат."""


class ElectricBicycle(ElectricTransport):
    """Велосипед с электрическим приводом."""


class Equipment(Asset):
    """Вещь на балансе, не являющаяся транспортом."""


class Helmet(Equipment):
    """Защитный шлем."""


@dataclass(frozen=True)
class ChargingStation(Equipment):
    daily_energy_kwh: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()
        validate_energy(self.daily_energy_kwh)
