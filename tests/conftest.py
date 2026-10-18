from dataclasses import dataclass, field
from io import StringIO
import sys

import pytest

from vyshkat.cli import ConsoleApplication
from vyshkat.domain import Transport
from vyshkat.services import FleetService, SafetyServiceCenter


@dataclass
class RecordingServiceCenter:
    approved: bool = True
    inspected: list[Transport] = field(default_factory=list)

    def inspect(self, transport: Transport) -> bool:
        self.inspected.append(transport)
        return self.approved


@pytest.fixture
def service_center():
    return RecordingServiceCenter()


@pytest.fixture
def fleet(service_center):
    return FleetService(service_center)


@pytest.fixture
def run_session(monkeypatch, capsys):
    def run(*lines):
        fleet = FleetService(SafetyServiceCenter())
        monkeypatch.setattr(sys, "stdin", StringIO("\n".join(lines) + "\n"))
        ConsoleApplication(fleet).run_interactive()
        return fleet, capsys.readouterr().out

    return run
