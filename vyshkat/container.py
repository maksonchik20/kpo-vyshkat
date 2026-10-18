"""Единственное место, где выбираются реализации и собираются зависимости."""

from dependency_injector import containers, providers

from .cli import ConsoleApplication
from .services import FleetService, SafetyServiceCenter


class Container(containers.DeclarativeContainer):
    service_center = providers.Singleton(SafetyServiceCenter)
    fleet_service = providers.Singleton(FleetService, service_center=service_center)
    application = providers.Factory(ConsoleApplication, fleet_service=fleet_service)
