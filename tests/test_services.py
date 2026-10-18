import pytest

from vyshkat.domain import Bicycle, ChargingStation, ElectricBicycle, ElectricTransport, Helmet, Scooter
from vyshkat.services import FleetReport, SafetyServiceCenter


def test_empty_fleet_has_zero_counts_energy_and_no_items(fleet):
    assert fleet.inventory() == ()
    assert fleet.beginner_transport() == ()
    assert fleet.report() == FleetReport(0, 0, 0)


def test_accepted_transport_is_inspected_once_then_added(fleet, service_center):
    bicycle = Bicycle("Велосипед", "B-1", 6)
    fleet.add(bicycle)
    assert service_center.inspected == [bicycle]
    assert fleet.inventory() == (bicycle,)
    assert fleet.report().transport_count == 1


def test_fake_rejection_excludes_transport_from_all_reports(fleet, service_center):
    service_center.approved = False
    scooter = Scooter("Самокат", "S-1", 10, daily_energy_kwh=2)
    with pytest.raises(ValueError, match="Техосмотр не пройден"):
        fleet.add(scooter)
    assert service_center.inspected == [scooter]
    assert fleet.inventory() == ()
    assert fleet.beginner_transport() == ()
    assert fleet.report() == FleetReport(0, 0, 0)


def test_rejected_number_can_be_accepted_after_successful_reinspection(fleet, service_center):
    bicycle = Bicycle("Велосипед", "B-1", 6)
    service_center.approved = False
    with pytest.raises(ValueError):
        fleet.add(bicycle)
    service_center.approved = True
    fleet.add(bicycle)
    assert service_center.inspected == [bicycle, bicycle]
    assert fleet.inventory() == (bicycle,)


def test_equipment_does_not_require_transport_inspection(fleet, service_center):
    service_center.approved = False
    helmet = Helmet("Шлем", "H-1")
    station = ChargingStation("Станция", "C-1", 2)
    fleet.add(helmet)
    fleet.add(station)
    assert not service_center.inspected
    assert fleet.inventory() == (helmet, station)
    assert fleet.beginner_transport() == ()
    assert fleet.report() == FleetReport(0, 2, 2)


@pytest.mark.parametrize(
    "first,second",
    [
        (Bicycle("Первый", "ID-1", 6), Scooter("Второй", "ID-1", 9, daily_energy_kwh=5)),
        (Helmet("Первый", "ID-1"), ChargingStation("Второй", "ID-1", 5)),
        (Bicycle("Первый", "ID-1", 6), Helmet("Второй", "ID-1")),
        (Helmet("Первый", "ID-1"), Bicycle("Второй", "ID-1", 6)),
    ],
)
def test_duplicate_cannot_replace_item_or_trigger_inspection(fleet, service_center, first, second):
    fleet.add(first)
    inspected_before = tuple(service_center.inspected)
    report_before = fleet.report()
    with pytest.raises(ValueError, match="уже занят"):
        fleet.add(second)
    assert fleet.inventory() == (first,)
    assert fleet.report() == report_before
    assert tuple(service_center.inspected) == inspected_before


def test_report_counts_categories_and_sums_energy_of_all_consumers(fleet):
    for item in (
        Bicycle("Велосипед", "B-1", 6),
        Scooter("Самокат", "S-1", 8, daily_energy_kwh=0.3),
        ElectricBicycle("Электровелосипед", "E-1", 5, daily_energy_kwh=0.6),
        Helmet("Шлем", "H-1"),
        ChargingStation("Станция", "C-1", 1.2),
    ):
        fleet.add(item)
    report = fleet.report()
    assert (report.transport_count, report.equipment_count, report.total_count) == (3, 2, 5)
    assert report.daily_energy_kwh == pytest.approx(2.1)


def test_beginner_boundary_excludes_five_and_includes_six_and_ten(fleet):
    difficult = Bicycle("Сложный", "B-1", 5)
    boundary = Bicycle("Граничный", "B-2", 6)
    easy = Scooter("Простой", "S-1", 10)
    for item in (difficult, boundary, easy, Helmet("Для новичков", "H-1")):
        fleet.add(item)
    assert fleet.beginner_transport() == (boundary, easy)


def test_new_transport_subtype_works_without_changing_fleet(fleet):
    class ElectricMoped(ElectricTransport):
        pass

    moped = ElectricMoped("Электромопед", "M-1", 8, daily_energy_kwh=4.5)
    fleet.add(moped)
    assert fleet.inventory() == (moped,)
    assert fleet.beginner_transport() == (moped,)
    assert fleet.report() == FleetReport(1, 0, 4.5)


def test_reports_return_immutable_snapshots(fleet):
    bicycle = Bicycle("Велосипед", "B-1", 6)
    fleet.add(bicycle)
    inventory = fleet.inventory()
    beginners = fleet.beginner_transport()
    fleet.add(Scooter("Самокат", "S-1", 8))
    assert inventory == (bicycle,)
    assert beginners == (bicycle,)
    assert fleet.report().total_count == 2


def test_unrelated_objects_cannot_be_added_to_balance(fleet):
    with pytest.raises(TypeError):
        fleet.add(object())
    assert fleet.inventory() == ()


@pytest.mark.parametrize(
    "brakes,frame,passed",
    [(True, True, True), (False, True, False), (True, False, False), (False, False, False)],
)
def test_real_inspection_requires_working_brakes_and_intact_frame(brakes, frame, passed):
    transport = Bicycle("Велосипед", "B-1", 6, brakes, frame)
    assert SafetyServiceCenter().inspect(transport) is passed
