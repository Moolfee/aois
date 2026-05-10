import builtins

import pytest

import src.main as main_module
from domain.exceptions import InvalidMenuChoiceError
from infrastructure.cli import Cli


def test_menu_print_menu_and_formatting(capsys):
    Cli.print_menu()
    output = capsys.readouterr().out
    assert "LAB_1 МЕНЮ" in output
    assert "IEEE-754 binary32: деление" in output

    assert Cli._format_excess3(73, [1, 0, 1, 0, 0, 1, 1, 0]) == "1010 0110"
    assert Cli._format_excess3(-73, [1, 0, 1, 0, 0, 1, 1, 0]) == "-1010 0110"


def test_menu_input_helpers(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "123")
    assert Cli._input_int("x") == 123

    monkeypatch.setattr(builtins, "input", lambda _: "1.5")
    assert Cli._input_ieee("x") == "1.5"

    monkeypatch.setattr(builtins, "input", lambda _: "42")
    assert Cli._input_bcd_number("x") == "42"


def test_menu_print_integer_result_covers_both_branches(capsys):
    Cli._print_integer_result(
        "TEST",
        {
            "a_dec": 1,
            "b_dec": 2,
            "res_dec": 3,
            "a_bin": [0, 0, 0, 1],
            "b_bin": [0, 0, 1, 0],
            "res_bin": [0, 0, 1, 1],
        },
    )
    output = capsys.readouterr().out
    assert "0011" in output

    Cli._print_integer_result(
        "TEST",
        {
            "a_dec": 1,
            "b_dec": 2,
            "res_dec": 0.5,
            "a_bin": [0, 0, 0, 1],
            "b_bin": [0, 0, 1, 0],
            "res_bin": [0, 0, 0, 0],
            "res_bin_fixed": "0000.10000",
        },
    )
    output = capsys.readouterr().out
    assert "0000.10000" in output


def test_menu_show_codes_and_operations(capsys):
    menu = Cli()

    menu._input_int = lambda prompt: -5
    menu._show_codes()
    assert "Дополнительный" in capsys.readouterr().out

    values = iter(["1.5", "2.25"])
    menu._input_ieee = lambda prompt: next(values)
    menu._ieee_operation("IEEE", menu.service.add_ieee)
    output = capsys.readouterr().out
    assert "Результат:    3.75" in output

    values = iter(["59", "14"])
    menu._input_bcd_number = lambda prompt: next(values)
    menu._bcd_add()
    output = capsys.readouterr().out
    assert "BCD-СЛОЖЕНИЕ (EXCESS-3)" in output
    assert "Результат:    73" in output


def test_menu_handle_choice_and_run_branches(monkeypatch, capsys):
    menu = Cli()
    with pytest.raises(InvalidMenuChoiceError):
        menu.handle_choice("99")

    inputs = iter(["0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    Cli().run()
    assert "Выход." in capsys.readouterr().out

    menu = Cli()
    menu.print_menu = lambda: None
    calls = {"count": 0}

    def fake_handle_choice(choice):
        calls["count"] += 1
        if calls["count"] == 1:
            raise InvalidMenuChoiceError("неизвестный пункт меню")
        raise ZeroDivisionError("деление на 0")

    menu.handle_choice = fake_handle_choice
    inputs = iter(["1", "2", "0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    menu.run()
    output = capsys.readouterr().out
    assert "Ошибка: неизвестный пункт меню" in output
    assert "Ошибка: деление на 0" in output


def test_main_calls_menu_run(monkeypatch):
    called = {"run": False}

    class FakeCli:
        def run(self):
            called["run"] = True

    monkeypatch.setattr(main_module, "Cli", FakeCli)
    main_module.main()
    assert called["run"] is True
