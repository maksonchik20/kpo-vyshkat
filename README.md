# ВышКат

Python 3.9+. Команды из корня проекта:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m vyshkat          # меню
python -m vyshkat --demo   # пример работы
python -m pytest -q        # тесты
```

## Решения

Данные хранятся в памяти и теряются после выхода. Для техосмотра проверяются два признака: исправность тормозов и целостность рамы. Их вводит пользователь.

- **S:** [модель](vyshkat/domain.py) проверяет значения, [техцентр](vyshkat/services.py) — исправность, [консоль](vyshkat/cli.py) отвечает за ввод и вывод. Хранение и отчёты оставлены в `FleetService`: отдельный репозиторий здесь не нужен.
- **O:** новый транспорт наследует `Transport` или `ElectricTransport`, сервис парка менять не нужно. Меню дополняется вручную — это сознательное ограничение, чтобы не усложнять код системой плагинов.
- **L:** все потомки `Transport` сохраняют общие поля и ограничения, поэтому подходят существующему сервису.
- **I:** `InventoryItem` и `EnergyConsumer` разделены: шлему и обычному велосипеду не нужно поле энергии.
- **D — самый явный пример:** `FleetService` получает техцентр через конструктор. [Контейнер](vyshkat/container.py) создаёт настоящую реализацию, тесты подставляют свою.

Для сотрудников нужна отдельная модель, для склада — учёт остатков и перемещений. Эти изменения не затрагивают нынешние отчёты парка.

## Тесты

В [test_services.py](tests/test_services.py) `test_fake_rejection_excludes_transport_from_all_reports` проверяет отказ техосмотра, а `test_beginner_boundary_excludes_five_and_includes_six_and_ten` — отбор новичков. В [test_container.py](tests/test_container.py) техцентр заменяется через `override` до первого создания `FleetService`.
