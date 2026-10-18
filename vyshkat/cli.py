"""Ввод, вывод и демонстрация всех основных сценариев."""

from __future__ import annotations

from .domain import (
    Bicycle, ChargingStation, ElectricBicycle, ElectricTransport, Equipment,
    Helmet, Scooter, Transport,
)
from .services import FleetService


class ConsoleApplication:
    def __init__(self, fleet_service: FleetService) -> None:
        self._fleet = fleet_service

    def run_interactive(self) -> None:
        print("ВышКат — учёт парка. Данные хранятся до завершения программы.")
        while True:
            try:
                command = input("\n1. Добавить объект\n2. Все отчёты\n0. Выход\nВыберите действие: ").strip()
                if command == "0":
                    print("До свидания!")
                    return
                if command == "1":
                    self._add()
                elif command == "2":
                    self._print_report()
                else:
                    print("Неизвестная команда. Введите 0, 1 или 2.")
            except ValueError as error:
                print(f"Ошибка: {error}")

    def _add(self) -> None:
        numberToType = {"1": Scooter, "2": Bicycle, "3": ElectricBicycle, "4": Helmet, "5": ChargingStation}
        item_type = numberToType.get(input(
            "Вид: 1 — самокат, 2 — велосипед, 3 — электровелосипед, 4 — шлем, 5 — зарядная станция: "
        ).strip())
        if item_type is None:
            raise ValueError("Неизвестный вид объекта.")
        name = input("Наименование: ").strip()
        number = input("Инвентарный номер: ").strip()
        fieldToValue = {}
        if issubclass(item_type, Transport):
            fieldToValue["beginner_ease"] = self._read_number("Простота для новичка (1–10): ", int)
            fieldToValue["brakes_working"] = self._read_boolean("Тормоза исправны? (да/нет): ")
            fieldToValue["frame_intact"] = self._read_boolean("Рама цела? (да/нет): ")
        if issubclass(item_type, (ElectricTransport, ChargingStation)):
            fieldToValue["daily_energy_kwh"] = self._read_number("Суточная энергия (кВт·ч): ")
        self._admit(item_type(name, number, **fieldToValue))

    def _admit(self, item: Transport | Equipment) -> None:
        label = f"{item.name} [{item.inventory_number}]"
        try:
            self._fleet.add(item)
            print(f"Принято: {label}.")
        except ValueError as error:
            print(f"Отклонено: {label}. {error}")

    def _print_report(self) -> None:
        report = self._fleet.report()
        print(
            f"Транспорт: {report.transport_count}; вещи: {report.equipment_count}; "
            f"всего: {report.total_count}."
        )
        print(f"Суточное потребление энергии: {report.daily_energy_kwh:.2f} кВт·ч.")
        print("Транспорт для новичков (простота ≥ 6):")
        beginners = self._fleet.beginner_transport()
        if not beginners:
            print("Подходящего транспорта нет.")
        for item in beginners:
            print(f"{item.name} [{item.inventory_number}], простота: {item.beginner_ease}.")
        print("Объекты на балансе:")
        items = self._fleet.inventory()
        if not items:
            print("Баланс пуст.")
        for item in items:
            print(f"{item.name} [{item.inventory_number}]")

    @staticmethod
    def _read_number(prompt: str, convert: type[float] | type[int] = float) -> float | int:
        try:
            return convert(input(prompt).replace(",", "."))
        except ValueError:
            raise ValueError("Ожидалось число в указанном формате.") from None

    @staticmethod
    def _read_boolean(prompt: str) -> bool:
        value = input(prompt).strip().lower()
        if value in ("да", "д", "yes", "y", "1"):
            return True
        if value in ("нет", "н", "no", "n", "0"):
            return False
        raise ValueError("Ответьте «да» или «нет».")

    def run_demo(self) -> None:
        print("ВышКат — демонстрация: пустой парк")
        self._print_report()
        print("\nПриёмка: исправные устройства, отказ техосмотра, вещи, дубликат номера")
        for item in (
            Scooter("Городской самокат", "S-001", 8, daily_energy_kwh=1.2),
            Bicycle("Прогулочный велосипед", "B-001", 6),
            ElectricBicycle("Спортивный электровелосипед", "E-001", 5, daily_energy_kwh=0.8),
            Scooter(
                "Самокат с неисправными тормозами", "S-002", 9,
                brakes_working=False, daily_energy_kwh=1.5,
            ),
            Helmet("Защитный шлем", "H-001"),
            ChargingStation("Зарядная станция", "C-001", 2.0),
            Helmet("Другой шлем", "S-001"),
        ):
            self._admit(item)
        try:
            Bicycle("Некорректный велосипед", "B-002", 11)
        except ValueError as error:
            print(f"Ошибка: {error}")
        print("\nИтоговые отчёты")
        self._print_report()
