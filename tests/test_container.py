from io import StringIO
import sys

from dependency_injector import providers
import pytest

from vyshkat.container import Container
from vyshkat.domain import Bicycle
from vyshkat.services import SafetyServiceCenter


def test_production_container_assembles_application_with_one_fleet(monkeypatch, capsys):
    container = Container()
    assert isinstance(container.service_center(), SafetyServiceCenter)
    fleet = container.fleet_service()
    assert container.fleet_service() is fleet
    fleet.add(Bicycle("Велосипед", "B-1", 6))
    monkeypatch.setattr(sys, "stdin", StringIO("2\n0\n"))
    container.application().run_interactive()
    assert "Транспорт: 1; вещи: 0; всего: 1." in capsys.readouterr().out


def test_container_override_changes_inspection_behavior(service_center):
    container = Container()
    service_center.approved = False
    with container.service_center.override(providers.Object(service_center)):
        fleet = container.fleet_service()
        transport = Bicycle("Исправный велосипед", "B-1", 6)
        with pytest.raises(ValueError, match="Техосмотр не пройден"):
            fleet.add(transport)
        assert service_center.inspected == [transport]
        assert fleet.inventory() == ()


def test_containers_have_independent_fleets():
    first = Container()
    second = Container()
    first.fleet_service().add(Bicycle("Велосипед", "B-1", 6))
    assert second.fleet_service().inventory() == ()
