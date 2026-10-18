from dataclasses import FrozenInstanceError

import pytest

from vyshkat.domain import (
    Bicycle, ChargingStation, ElectricBicycle, EnergyConsumer, Helmet, Scooter,
)


@pytest.mark.parametrize(
    "name,number",
    [("", "H-1"), (" \t", "H-1"), (None, "H-1"), ("Шлем", ""),
     ("Шлем", " \n"), ("Шлем", None), ("Шлем", " H-1"), ("Шлем", "H-1 ")],
)
def test_inventory_fields_reject_invalid_values(name, number):
    with pytest.raises(ValueError):
        Helmet(name, number)
    with pytest.raises(ValueError):
        Bicycle(name, number, 6)


@pytest.mark.parametrize("ease", [0, 11, -1, 6.5, True, "6"])
def test_beginner_ease_must_be_an_integer_between_one_and_ten(ease):
    with pytest.raises(ValueError):
        Bicycle("Велосипед", "B-1", ease)


@pytest.mark.parametrize("ease", [1, 10])
def test_ease_accepts_both_ends_of_the_scale(ease):
    assert Bicycle("Велосипед", "B-1", ease).beginner_ease == ease


@pytest.mark.parametrize("energy", [-1, float("nan"), float("inf"), -float("inf"), True, "1", None, 10**400])
def test_every_consumer_rejects_invalid_energy(energy):
    for transport_type in (Scooter, ElectricBicycle):
        with pytest.raises(ValueError):
            transport_type("Транспорт", "T-1", 6, daily_energy_kwh=energy)
    with pytest.raises(ValueError):
        ChargingStation("Станция", "C-1", daily_energy_kwh=energy)


@pytest.mark.parametrize("energy", [0, 0.25, 12.5])
def test_every_consumer_accepts_finite_nonnegative_energy(energy):
    items = (
        Scooter("Самокат", "S-1", 6, daily_energy_kwh=energy),
        ElectricBicycle("Электровелосипед", "E-1", 6, daily_energy_kwh=energy),
        ChargingStation("Станция", "C-1", daily_energy_kwh=energy),
    )
    assert all(isinstance(item, EnergyConsumer) for item in items)
    assert all(item.daily_energy_kwh == energy for item in items)


def test_bicycle_and_helmet_do_not_pretend_to_consume_energy():
    assert not isinstance(Bicycle("Велосипед", "B-1", 6), EnergyConsumer)
    assert not isinstance(Helmet("Шлем", "H-1"), EnergyConsumer)


def test_domain_objects_are_immutable_and_number_may_have_internal_spaces():
    bicycle = Bicycle("Велосипед", "B 1", 6)
    with pytest.raises(FrozenInstanceError):
        bicycle.inventory_number = "B 2"
    with pytest.raises(FrozenInstanceError):
        bicycle.beginner_ease = 10
    with pytest.raises(FrozenInstanceError):
        bicycle.brakes_working = False
    assert bicycle.inventory_number == "B 1"


@pytest.mark.parametrize("brakes,frame", [(1, True), (True, "да"), (None, False)])
def test_condition_requires_boolean_values(brakes, frame):
    with pytest.raises(ValueError):
        Bicycle("Велосипед", "B-1", 6, brakes, frame)
