"""Техосмотр, приёмка и отчёты по парку."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .domain import EnergyConsumer, Equipment, InventoryItem, Transport


class ServiceCenter(Protocol):
    def inspect(self, transport: Transport) -> bool: ...


class SafetyServiceCenter:
    def inspect(self, transport: Transport) -> bool:
        return transport.brakes_working and transport.frame_intact


@dataclass(frozen=True)
class FleetReport:
    transport_count: int
    equipment_count: int
    daily_energy_kwh: float

    @property
    def total_count(self) -> int:
        return self.transport_count + self.equipment_count


class FleetService:
    def __init__(self, service_center: ServiceCenter) -> None:
        self._service_center = service_center
        self._inventoryNumberToItem: dict[str, InventoryItem] = {}

    def add(self, item: Transport | Equipment) -> None:
        if not isinstance(item, (Transport, Equipment)):
            raise TypeError("На баланс можно поставить только транспорт или вещь.")
        if item.inventory_number in self._inventoryNumberToItem:
            raise ValueError(f"Инвентарный номер «{item.inventory_number}» уже занят.")
        if isinstance(item, Transport) and not self._service_center.inspect(item):
            raise ValueError("Техосмотр не пройден.")
        self._inventoryNumberToItem[item.inventory_number] = item

    def inventory(self) -> tuple[InventoryItem, ...]:
        return tuple(self._inventoryNumberToItem.values())

    def beginner_transport(self) -> tuple[Transport, ...]:
        return tuple(
            item for item in self.inventory()
            if isinstance(item, Transport) and item.beginner_ease >= 6
        )

    def report(self) -> FleetReport:
        items = self.inventory()
        return FleetReport(
            transport_count=sum(isinstance(item, Transport) for item in items),
            equipment_count=sum(isinstance(item, Equipment) for item in items),
            daily_energy_kwh=sum(
                item.daily_energy_kwh for item in items if isinstance(item, EnergyConsumer)
            ),
        )
