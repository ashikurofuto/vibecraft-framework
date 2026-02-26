# 🧹 Аудит проекта Vibecraft Framework v0.4

**Дата:** 27 февраля 2026 г.  
**Цель:** Очистка проекта от мусора перед релизом v0.4.0

---

## 📊 Классификация файлов

### ✅ PRODUCTION (оставить)

#### vibecraft-framework/vibecraft/
```
__init__.py
bootstrapper.py
cli.py
context_manager.py
doctor.py
exporter.py
main.py
rollback.py
runner.py

adapters/
  __init__.py
  base_adapter.py
  clipboard_adapter.py

core/
  __init__.py
  base_bootstrapper.py
  base_runner.py
  config.py
  exceptions.py
  factory.py
  migrations.py
  protocols.py

modes/
  __init__.py
  
  modes/modular/
    __init__.py (ModularBootstrapper)
    bootstrapper.py
    context_manager.py
    dependency_analyzer.py
    integration_manager.py
    module_manager.py
    module_registry.py
    plan_generator.py
    runner.py
    security.py
    structure.py
    validation.py
  
  modes/simple/
    __init__.py
    bootstrapper.py
    runner.py

templates/ (все шаблоны)
```

#### vibecraft-framework/tests/ (ОСНОВНЫЕ ТЕСТЫ)
```
__init__.py
conftest.py

unit/
  adapters/test_clipboard_adapter.py
  core/
    test_base_bootstrapper.py
    test_base_runner.py
    test_config.py
    test_exceptions.py
    test_protocols.py
  modes/modular/
    test_context_manager.py
    test_integration_manager.py
    test_modular_runner.py
    test_module_manager.py
    test_module_registry.py
  test_bootstrapper.py
  test_context_manager.py
  test_doctor.py
  test_exporter.py
  test_rollback.py
  test_runner.py

integration/test_modular_runner_workflow.py
unit/test_modular_runner.py
```

#### vibecraft-framework/docs/ (ОСНОВНАЯ ДОКУМЕНТАЦИЯ)
```
MODULAR_MODE.md
MODULE_DEVELOPMENT.md
INTEGRATION_GUIDE.md
MIGRATION_SIMPLE_TO_MODULAR.md
```

#### vibecraft-framework/ (КОРНЕВЫЕ ФАЙЛЫ)
```
pyproject.toml
setup.py
README.md
RELEASE_NOTES_v0.4.0.md
```

---

### ⚠️ DEVELOPMENT ARTIFACTS (удалить)

#### 1. Временные файлы сборки
```
vibecraft-framework/.coverage           ← Покрытие тестов (временный)
vibecraft-framework/test_results.txt    ← Старые результаты тестов
vibecraft-framework/3.12/               ← Неизвестная директория
vibecraft-framework/3.2/                ← Неизвестная директория
vibecraft-framework/dist/               ← Build артефакты
vibecraft-framework/vibecraft.egg-info/ ← Build артефакты
```

#### 2. Кэш Python
```
**/__pycache__/              ← Все __pycache__ директории
**/*.pyc                     ← Все .pyc файлы
.mypy_cache/                 ← Кэш mypy
.ruff_cache/                 ← Кэш ruff
.pytest_cache/               ← Кэш pytest
```

#### 3. Скрипты установки (дубликаты)
```
vibecraft-framework/configure_path.py     ← Не используется
vibecraft-framework/install-to-project.py ← Не используется
vibecraft-framework/install.py            ← Не используется
vibecraft-framework/install.bat           ← Не используется
vibecraft-framework/install.ps1           ← Не используется
vibecraft-framework/vibecraft.bat         ← Не используется
vibecraft-framework/INSTALL.md            ← Устарело (есть в README)
```

#### 4. Служебные файлы
```
vibecraft-framework/.pypirc    ← PyPI credentials template (не для репо)
```

---

### 🗑️ DUPLICATES (удалить дубликаты)

#### 1. Snapshots тестов (АВТОМАТИЧЕСКИЕ КОПИИ)
```
.vibecraft/snapshots/*/src/tests/
```
**Проблема:** Каждый snapshot содержит полную копию тестов на момент фазы.  
**Решение:** Удалить все snapshot тесты, оставить только основные в `vibecraft-framework/tests/`

**Файлы для удаления (~90 файлов):**
```
.vibecraft/snapshots/*/src/tests/phase_2/
.vibecraft/snapshots/*/src/tests/phase_3/
.vibecraft/snapshots/*/src/tests/phase_4/
.vibecraft/snapshots/*/src/tests/phase_5/
.vibecraft/snapshots/*/src/tests/phase_6/
.vibecraft/snapshots/*/src/tests/phase_7/
.vibecraft/snapshots/*/src/tests/phase_8/
```

#### 2. Старые тесты в src/tests/
```
src/tests/phase_2/    ← Перенесены в vibecraft-framework/tests/
src/tests/phase_3/    ← Перенесены в vibecraft-framework/tests/
src/tests/phase_4/    ← Перенесены в vibecraft-framework/tests/
src/tests/phase_5/    ← Перенесены в vibecraft-framework/tests/
src/tests/phase_6/    ← Перенесены в vibecraft-framework/tests/
src/tests/phase_7/    ← Перенесены в vibecraft-framework/tests/
src/tests/phase_8/    ← Перенесены в vibecraft-framework/tests/
```
**Решение:** Удалить, т.к. актуальные версии в `vibecraft-framework/tests/`

#### 3. Дублирующаяся документация фаз
```
docs/plans/phase_1.md            ← Отчёт о фазе 1
docs/plans/phase_2.md            ← Отчёт о фазе 2
...
docs/plans/phase_10.md           ← Отчёт о фазе 10

docs/plans/green_result_phase_*.md   ← Результаты тестов
docs/plans/red_result_phase_*.md     ← Результаты тестов
docs/plans/code_review_phase_*.md    ← Code review

docs/plans/pre_check_phase_*.md      ← Pre-check отчёты
docs/plans/output.md                 ← Случайный output
```
**Решение:** Оставить только `phase_10_result.md` (финальный релиз), остальные - история разработки

---

### 📝 ДОКУМЕНТАЦИЯ (ревизия)

#### Оставить (актуально):
```
docs/plans/phase_10_result.md    ← Финальный отчёт о релизе
QWEN.md                          ← Контекст проекта
research.md                      ← Исследование проекта
stack.md                         ← Технологический стек
```

#### Удалить (история разработки):
```
docs/plans/phase_1.md - phase_9.md
docs/plans/green_result_phase_*.md (6 файлов)
docs/plans/red_result_phase_*.md (7 файлов)
docs/plans/code_review_phase_*.md (6 файлов)
docs/plans/pre_check_phase_*.md (7 файлов)
docs/plans/output.md
```

---

### 📦 VIBECRAFT-FRAMEWORK КОРНЕВЫЕ ФАЙЛЫ

#### Оставить:
```
pyproject.toml
setup.py
README.md
RELEASE_NOTES_v0.4.0.md
docs/MODULAR_MODE.md
docs/MODULE_DEVELOPMENT.md
docs/INTEGRATION_GUIDE.md
docs/MIGRATION_SIMPLE_TO_MODULAR.md
```

#### Удалить:
```
REFACTORING_REPORT.md        ← Отчёт о рефакторинге v0.3 (не актуально)
test_results.txt             ← Старые логи тестов
configure_path.py            ← Не используется
install.py                   ← Не используется
install.bat                  ← Не используется
install.ps1                  ← Не используется
vibecraft.bat                ← Не используется
INSTALL.md                   ← Дубликат README
.pypirc                      ← Не для репозитория
```

---

## 🎯 ПЛАН ОЧИСТКИ

### Шаг 1: Удалить временные файлы сборки
```bash
cd vibecraft-framework
rm -rf .coverage test_results.txt dist/ vibecraft.egg-info/
rm -rf 3.12/ 3.2/
rm -rf configure_path.py install-to-project.py install.py
rm -rf install.bat install.ps1 vibecraft.bat INSTALL.md .pypirc
rm -rf REFACTORING_REPORT.md
```

### Шаг 2: Очистить кэш Python
```bash
# В корне проекта
rm -rf .mypy_cache/ .ruff_cache/ .pytest_cache/
rm -rf **/__pycache__/ **/*.pyc

# В vibecraft-framework
cd vibecraft-framework
rm -rf .mypy_cache/ .ruff_cache/ .pytest_cache/
rm -rf **/__pycache__/ **/*.pyc
```

### Шаг 3: Удалить дубликаты тестов
```bash
# Удалить snapshot тесты
rm -rf .vibecraft/snapshots/*/src/tests/

# Удалить старые тесты из src/
rm -rf src/tests/phase_*/
rm -rf src/output.md
```

### Шаг 4: Очистить документацию фаз
```bash
cd docs/plans/

# Оставить только финальный отчёт
rm -rf phase_1.md phase_2.md phase_3.md phase_4.md 
rm -rf phase_5.md phase_6.md phase_7.md phase_8.md phase_9.md phase_10.md
rm -rf green_result_phase_*.md (6 файлов)
rm -rf red_result_phase_*.md (7 файлов)
rm -rf code_review_phase_*.md (6 файлов)
rm -rf pre_check_phase_*.md (7 файлов)
rm -rf output.md
```

### Шаг 5: Создать .gitignore и .qwenignore
```bash
# В корне проекта
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Vibecraft specific
.vibecraft/snapshots/
src/tests/
integration/
modules/
shared/
EOF

# .qwenignore
cat > .qwenignore << 'EOF'
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
.vibecraft/snapshots/
dist/
*.egg-info/
EOF
```

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### До очистки:
- **Тестовых файлов:** ~130 (многие дублируются)
- **Документов фаз:** ~40
- **Временных файлов:** ~20
- **Кэш файлов:** ~60

### После очистки:
- **Тестовых файлов:** 18 (актуальные)
- **Документов:** 8 (актуальные)
- **Временных файлов:** 0
- **Кэш файлов:** 0

### Экономия:
- **~112 тестовых дубликатов** удалено
- **~32 документа истории** удалено
- **~80 временных/кэш файлов** удалено

---

## ✅ ЧЕКЛИСТ ПЕРЕД РЕЛИЗОМ

- [ ] Удалить временные файлы сборки
- [ ] Очистить Python кэш
- [ ] Удалить дубликаты тестов (snapshots + src/tests)
- [ ] Очистить документацию фаз
- [ ] Создать .gitignore
- [ ] Создать .qwenignore
- [ ] Финальный запуск тестов
- [ ] Проверка структуры проекта

---

*Generated for Vibecraft Framework v0.4.0 Release*
