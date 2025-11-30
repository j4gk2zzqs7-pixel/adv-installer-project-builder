# Структура проекта Advanced Installer Project Builder

## Общая структура

```
adv-installer-project-builder/
│
├── src/                         # Исходный код приложения
│   ├── core/                    # Основные модули
│   │   ├── __init__.py
│   │   ├── aip_manager.py       # Управление .aip файлами
│   │   └── build_manager.py     # Управление сборкой проектов
│   │
│   ├── gui/                     # Графический интерфейс
│   │   ├── __init__.py
│   │   └── main_window.py       # Главное окно приложения
│   │
│   └── utils/                   # Вспомогательные утилиты
│       ├── __init__.py
│       ├── image_converter.py   # Конвертация изображений
│       └── powershell_editor.py # Редактор PowerShell скриптов
│
├── tests/                       # Тесты (будут добавлены)
│
├── main.py                      # Точка входа в приложение
├── setup.py                     # Установочный скрипт
├── requirements.txt             # Python зависимости
├── .gitignore                   # Игнорируемые файлы
│
├── README.md                    # Основная документация
├── EXAMPLES.md                  # Примеры использования
├── STRUCTURE.md                 # Описание структуры (этот файл)
├── LICENSE                      # Лицензия MIT
│
└── Altersgate.aip               # Пример проекта Advanced Installer
```

## Описание модулей

### Core Modules (src/core/)

#### aip_manager.py
**Класс: `AIPManager`**

Управляет файлами проектов Advanced Installer (.aip), которые являются XML файлами.

**Основные возможности:**
- Чтение и разбор .aip файлов
- Получение свойств проекта (ProductName, Manufacturer, Version)
- Обновление свойств проекта
- Обновление ссылок на иконки
- Создание резервных копий
- Сохранение изменений

**Основные методы:**
```python
AIPManager(aip_file_path: str)
get_property(property_name: str) -> Optional[str]
set_property(property_name: str, value: str) -> bool
update_project_info(product_name, manufacturer, version) -> Dict
update_icon(icon_bmp_path: str) -> bool
save(output_path: Optional[str])
create_backup() -> str
get_project_info() -> Dict
```

#### build_manager.py
**Класс: `BuildManager`**

Управляет процессом сборки проектов Advanced Installer.

**Основные возможности:**
- Автоматическое определение установки Advanced Installer
- Поиск в реестре Windows
- Запуск процесса сборки
- Callback для отслеживания прогресса
- Настройка папки вывода

**Основные методы:**
```python
BuildManager(advinst_path: Optional[str])
is_advanced_installer_available() -> bool
set_advanced_installer_path(path: str)
build_project(aip_file, output_folder, build_name, callback) -> bool
get_build_info(aip_file: str) -> dict
```

### GUI Modules (src/gui/)

#### main_window.py
**Класс: `MainWindow`**

Главное окно приложения на базе PyQt5.

**Основные возможности:**
- Загрузка и управление .aip проектами
- Редактирование информации о проекте
- Конвертация и применение иконок
- Запуск сборки проектов
- Редактирование PowerShell скриптов
- Управление версиями скриптов

**Вкладки интерфейса:**
1. **Информация о проекте** - редактирование названия, производителя, версии
2. **Конвертация иконки** - загрузка изображений и конвертация в .ico/.bmp
3. **Сборка проекта** - настройка и запуск сборки
4. **Редактор PowerShell** - редактирование и версионирование .ps1 файлов

**Дополнительный класс: `BuildThread`**

Асинхронный поток для выполнения сборки без блокировки UI.

### Utility Modules (src/utils/)

#### image_converter.py
**Класс: `ImageConverter`**

Конвертация изображений для использования в Advanced Installer.

**Основные возможности:**
- Конвертация PNG/JPG/JPEG в ICO
- Конвертация PNG/JPG/JPEG в BMP
- Создание мультиразмерных ICO файлов
- Настройка размеров выходных файлов
- Получение информации об изображениях

**Поддерживаемые форматы:**
- Входные: PNG, JPG, JPEG
- Выходные: ICO, BMP

**Размеры ICO по умолчанию:**
- 16x16, 32x32, 48x48, 64x64, 128x128, 256x256

**Основные методы:**
```python
ImageConverter()
is_supported_format(file_path: str) -> bool
convert_to_ico(input_path, output_path, sizes) -> str
convert_to_bmp(input_path, output_path, size) -> str
convert_image_for_installer(input_path, output_dir, base_name) -> dict
get_image_info(file_path: str) -> dict
```

#### powershell_editor.py
**Класс: `PowerShellEditor`**

Редактирование и управление версиями PowerShell скриптов.

**Основные возможности:**
- Чтение и запись .ps1 файлов
- Система версионирования
- Создание именованных версий
- Восстановление из версий
- Автоматические резервные копии
- Поиск и замена текста
- Очистка старых версий

**Структура версий:**
Версии сохраняются в директории `.versions/<script_name>/`

**Основные методы:**
```python
PowerShellEditor(script_path: str)
read_script() -> str
write_script(content: str, create_backup: bool) -> str
create_version(version_name: Optional[str]) -> str
list_versions() -> List[dict]
restore_version(version_path: str, create_backup: bool) -> bool
find_and_replace(find_text, replace_text, case_sensitive) -> int
get_script_info() -> dict
cleanup_old_versions(keep_count: int) -> int
```

## Зависимости

### Основные библиотеки

#### PyQt5 (>=5.15.0)
- **Назначение**: GUI фреймворк
- **Используется в**: src/gui/main_window.py
- **Компоненты**:
  - QMainWindow - главное окно
  - QTabWidget - вкладки
  - QFileDialog - диалоги выбора файлов
  - QMessageBox - сообщения
  - QThread - асинхронная сборка

#### Pillow (>=9.0.0)
- **Назначение**: Обработка изображений
- **Используется в**: src/utils/image_converter.py
- **Операции**:
  - Открытие изображений
  - Изменение размеров
  - Конвертация форматов
  - Сохранение в ICO/BMP

#### pywin32 (>=305)
- **Назначение**: Windows API и реестр
- **Используется в**: src/core/build_manager.py
- **Операции**:
  - Поиск Advanced Installer в реестре
  - Чтение путей установки

### Встроенные модули

- **xml.etree.ElementTree** - парсинг XML (.aip файлы)
- **subprocess** - запуск Advanced Installer
- **pathlib** - работа с путями
- **shutil** - операции с файлами
- **datetime** - метки времени для версий
- **os** - системные операции

## Форматы данных

### .aip файлы (XML)

Пример структуры:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<DOCUMENT Type="Advanced Installer" ...>
  <COMPONENT cid="caphyon.advinst.msicomp.MsiPropsComponent">
    <ROW Property="ProductName" Value="MyApp"/>
    <ROW Property="Manufacturer" Value="MyCompany"/>
    <ROW Property="ProductVersion" Value="1.0.0"/>
    <ROW Property="AppLogoIcon" MultiBuildValue="DefaultBuild:icon.bmp"/>
  </COMPONENT>
  ...
</DOCUMENT>
```

### Версии PowerShell скриптов

Формат имени: `{script_name}_{version_name}_{timestamp}.ps1`

Пример: `Deploy-Application_before_update_20240115_143025.ps1`

## Рабочие процессы

### Типичный процесс работы с проектом:

1. **Загрузка проекта**
   - Выбор .aip файла
   - Парсинг XML
   - Отображение информации

2. **Редактирование**
   - Изменение свойств проекта
   - Обновление иконок
   - Редактирование скриптов

3. **Сохранение**
   - Создание резервных копий
   - Применение изменений
   - Сохранение в XML

4. **Сборка**
   - Настройка параметров
   - Запуск Advanced Installer
   - Отслеживание прогресса

## Расширение функциональности

### Добавление новых возможностей

1. **Новый модуль утилит**
   - Создать файл в `src/utils/`
   - Реализовать класс с необходимой функциональностью
   - Импортировать в GUI при необходимости

2. **Новая вкладка GUI**
   - Добавить метод `create_*_tab()` в MainWindow
   - Создать UI элементы
   - Подключить обработчики событий

3. **Расширение AIPManager**
   - Добавить методы для новых свойств
   - Обновить XML парсинг
   - Добавить валидацию

## Тестирование

### Структура тестов (планируется)

```
tests/
├── test_aip_manager.py
├── test_build_manager.py
├── test_image_converter.py
├── test_powershell_editor.py
└── test_integration.py
```

### Запуск тестов

```bash
# Установка pytest
pip install pytest pytest-qt

# Запуск всех тестов
pytest tests/

# Запуск с покрытием
pytest --cov=src tests/
```

## Производительность

### Оптимизации

- **Асинхронная сборка**: BuildThread предотвращает зависание UI
- **Ленивая загрузка**: Модули импортируются по требованию
- **Кэширование**: Информация о проекте кэшируется после загрузки

### Ограничения

- Размер .aip файла: неограничен (но большие файлы могут медленно парситься)
- Размер изображений: рекомендуется до 2048x2048 пикселей
- Количество версий PS: рекомендуется очищать старые (cleanup_old_versions)

## Безопасность

### Рекомендации

- Всегда создавайте резервные копии перед изменениями
- Проверяйте источник .aip файлов
- Не запускайте непроверенные PowerShell скрипты
- Используйте версионирование для отката изменений

## Совместимость

### Версии Advanced Installer

Протестировано с:
- Advanced Installer 20.x
- Advanced Installer 21.x
- Advanced Installer 22.x

### Операционные системы

- Windows 10 (64-bit)
- Windows 11
- Windows Server 2016+

### Python

- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+
