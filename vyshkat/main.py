"""Точка сборки и запуска приложения."""

from __future__ import annotations

import argparse

from .container import Container


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ВышКат — учёт парка кикшеринга")
    parser.add_argument("--demo", action="store_true", help="показать все основные сценарии")
    args = parser.parse_args(argv)
    application = Container().application()
    try:
        if args.demo:
            application.run_demo()
        else:
            application.run_interactive()
    except EOFError:
        print("\nВвод завершён. До свидания!")
    except KeyboardInterrupt:
        print("\nРабота прервана.")
        return 130
    return 0
