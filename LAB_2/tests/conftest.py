"""Общая настройка тестов.

Здесь пути проекта добавляются в `sys.path`, чтобы тесты могли
импортировать модули и через `domain/...`, и через `application/...`.
"""

import os
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")

# Добавляем корень проекта, чтобы были доступны импорты вида `src.*`.
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Добавляем директорию `src`, чтобы работали и прямые импорты `domain.*`.
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
