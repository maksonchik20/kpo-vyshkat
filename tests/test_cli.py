from io import StringIO
import runpy
import sys

import pytest

from vyshkat.cli import ConsoleApplication
from vyshkat.main import main
from vyshkat.services import FleetService, SafetyServiceCenter


def test_interactive_session_handles_all_types_rejection_and_reports(run_session):
    fleet, output = run_session(
        "1", "1", "Самокат", "S-1", "8", "да", "да", "1,2",
        "1", "2", "Велосипед", "B-1", "6", "yes", "yes",
        "1", "3", "Электровелосипед", "E-1", "5", "1", "1", "0.8",
        "1", "1", "Сломанный", "S-2", "9", "нет", "да", "10",
        "1", "4", "Шлем", "H-1",
        "1", "5", "Станция", "C-1", "2",
        "1", "4", "Дубликат", "S-1",
        "2", "0",
    )
    assert fleet.report().total_count == 5
    assert fleet.report().daily_energy_kwh == pytest.approx(4)
    assert [item.inventory_number for item in fleet.beginner_transport()] == ["S-1", "B-1"]
    assert "Транспорт: 3; вещи: 2; всего: 5." in output
    assert "4.00 кВт·ч" in output
    assert "Отклонено: Сломанный [S-2]" in output
    assert "Отклонено: Дубликат [S-1]" in output
    assert "Шлем [H-1]" in output
    assert "Станция [C-1]" in output
    assert "До свидания!" in output


def test_empty_reports_and_unknown_command_are_explained(run_session):
    _, output = run_session("99", "2", "0")
    assert "Неизвестная команда" in output
    assert "Транспорт: 0; вещи: 0; всего: 0." in output
    assert "0.00 кВт·ч" in output
    assert "Подходящего транспорта нет." in output
    assert "Баланс пуст." in output


@pytest.mark.parametrize(
    "fields",
    [
        ["1", "9"],
        ["1", "2", "Велосипед", "B-1", "abc"],
        ["1", "2", "Велосипед", "B-1", "6.5"],
        ["1", "5", "Станция", "C-1", "abc"],
        ["1", "5", "Станция", "C-1", "-1"],
        ["1", "5", "Станция", "C-1", "inf"],
        ["1", "5", "Станция", "C-1", "nan"],
        ["1", "4", "", "H-1"],
        ["1", "4", "Шлем", ""],
        ["1", "2", "Велосипед", "B-1", "6", "возможно"],
        ["1", "2", "Велосипед", "B-1", "11", "да", "да"],
    ],
)
def test_invalid_form_returns_to_menu_without_adding_partial_item(run_session, fields):
    fleet, output = run_session(*fields, "2", "0")
    assert fleet.report().total_count == 0
    assert "Ошибка:" in output
    assert "Транспорт: 0; вещи: 0; всего: 0." in output
    assert "До свидания!" in output


@pytest.mark.parametrize("text", ["", "1\n1\nСамокат\n"])
def test_eof_at_menu_or_midway_through_form_exits_cleanly(text, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO(text))
    assert main([]) == 0
    assert "Ввод завершён" in capsys.readouterr().out


def test_input_trims_whitespace_and_accepts_uppercase_boolean_answers(run_session):
    fleet, _ = run_session(" 1 ", "2", " Велосипед ", " B-1 ", "6", "ДА", "Д", "0")
    assert fleet.inventory()[0].name == "Велосипед"
    assert fleet.inventory()[0].inventory_number == "B-1"


def test_demo_finishes_with_expected_inventory(capsys):
    fleet = FleetService(SafetyServiceCenter())
    ConsoleApplication(fleet).run_demo()
    output = capsys.readouterr().out
    assert fleet.report().transport_count == 3
    assert fleet.report().equipment_count == 2
    assert fleet.report().daily_energy_kwh == pytest.approx(4)
    assert [item.inventory_number for item in fleet.beginner_transport()] == ["S-001", "B-001"]
    assert all(item.inventory_number != "S-002" for item in fleet.inventory())
    assert "Отклонено:" in output
    assert "уже занят" in output
    assert "Ошибка:" in output


def test_main_runs_demo_using_real_container(capsys):
    assert main(["--demo"]) == 0
    assert "Транспорт: 3; вещи: 2; всего: 5." in capsys.readouterr().out


def test_main_runs_menu_using_real_container(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO("0\n"))
    assert main([]) == 0
    assert "До свидания!" in capsys.readouterr().out


def test_help_does_not_start_interactive_input(capsys):
    with pytest.raises(SystemExit) as result:
        main(["--help"])
    assert result.value.code == 0
    assert "--demo" in capsys.readouterr().out


def test_unknown_argument_returns_usage_error(capsys):
    with pytest.raises(SystemExit) as result:
        main(["--unknown"])
    assert result.value.code == 2
    assert "--unknown" in capsys.readouterr().err


def test_keyboard_interrupt_has_no_traceback(monkeypatch, capsys):
    class InterruptedInput(StringIO):
        def readline(self, *args, **kwargs):
            raise KeyboardInterrupt

    monkeypatch.setattr(sys, "stdin", InterruptedInput())
    assert main([]) == 130
    assert "Работа прервана" in capsys.readouterr().out


def test_module_entry_point_is_runnable(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["vyshkat", "--demo"])
    with pytest.raises(SystemExit) as result:
        runpy.run_module("vyshkat", run_name="__main__")
    assert result.value.code == 0
    assert "4.00 кВт·ч" in capsys.readouterr().out
