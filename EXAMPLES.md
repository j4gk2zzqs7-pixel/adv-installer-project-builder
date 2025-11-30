# Примеры использования Advanced Installer Project Builder

Этот файл содержит примеры программного использования модулей проекта.

## Содержание

- [Работа с AIP файлами](#работа-с-aip-файлами)
- [Конвертация изображений](#конвертация-изображений)
- [Управление сборкой](#управление-сборкой)
- [Редактирование PowerShell скриптов](#редактирование-powershell-скриптов)

## Работа с AIP файлами

### Базовое использование

```python
from core.aip_manager import AIPManager

# Загрузка проекта
aip = AIPManager("C:/Projects/MyApp/MyApp.aip")

# Получение информации о проекте
info = aip.get_project_info()
print(f"Продукт: {info['ProductName']}")
print(f"Производитель: {info['Manufacturer']}")
print(f"Версия: {info['ProductVersion']}")
```

### Обновление информации о проекте

```python
from core.aip_manager import AIPManager

aip = AIPManager("MyApp.aip")

# Создание резервной копии перед изменениями
backup_path = aip.create_backup()
print(f"Резервная копия создана: {backup_path}")

# Обновление информации
results = aip.update_project_info(
    product_name="My New Application",
    manufacturer="My Company LLC",
    version="2.0.0"
)

print("Результаты обновления:")
for key, success in results.items():
    print(f"  {key}: {'✓' if success else '✗'}")

# Сохранение изменений
aip.save()
print("Изменения сохранены!")
```

### Изменение отдельных свойств

```python
from core.aip_manager import AIPManager

aip = AIPManager("MyApp.aip")

# Изменение только версии
aip.update_project_info(version="1.5.2")
aip.save()

# Изменение только названия
aip.update_project_info(product_name="Updated App Name")
aip.save()
```

### Обновление иконки

```python
from core.aip_manager import AIPManager

aip = AIPManager("MyApp.aip")

# Обновление иконки (должна быть уже в формате .bmp)
aip.update_icon("C:/Icons/MyNewIcon.bmp")
aip.save()
```

## Конвертация изображений

### Конвертация в ICO

```python
from utils.image_converter import ImageConverter

converter = ImageConverter()

# Конвертация PNG в ICO
ico_path = converter.convert_to_ico(
    input_path="C:/Images/icon.png",
    output_path="C:/Output/icon.ico"
)

print(f"ICO файл создан: {ico_path}")
```

### Конвертация в BMP

```python
from utils.image_converter import ImageConverter

converter = ImageConverter()

# Конвертация JPG в BMP
bmp_path = converter.convert_to_bmp(
    input_path="C:/Images/logo.jpg",
    output_path="C:/Output/logo.bmp",
    size=(256, 256)  # Размер BMP файла
)

print(f"BMP файл создан: {bmp_path}")
```

### Конвертация для использования в установщике

```python
from utils.image_converter import ImageConverter

converter = ImageConverter()

# Автоматическая конвертация в оба формата
result = converter.convert_image_for_installer(
    input_path="C:/Images/app_icon.png",
    output_dir="C:/MyProject",
    base_name="ApplicationIcon"
)

print(f"ICO создан: {result['ico']}")
print(f"BMP создан: {result['bmp']}")
```

### Получение информации об изображении

```python
from utils.image_converter import ImageConverter

converter = ImageConverter()

info = converter.get_image_info("C:/Images/icon.png")
print(f"Размер: {info['width']}x{info['height']}")
print(f"Формат: {info['format']}")
print(f"Режим: {info['mode']}")
```

### Пользовательские размеры для ICO

```python
from utils.image_converter import ImageConverter

converter = ImageConverter()

# Создание ICO с кастомными размерами
custom_sizes = [(16, 16), (32, 32), (64, 64), (128, 128)]

ico_path = converter.convert_to_ico(
    input_path="icon.png",
    output_path="custom_icon.ico",
    sizes=custom_sizes
)
```

## Управление сборкой

### Автоматическая сборка

```python
from core.build_manager import BuildManager

# Создание менеджера (автоматически ищет Advanced Installer)
builder = BuildManager()

# Проверка доступности Advanced Installer
if builder.is_advanced_installer_available():
    print(f"Advanced Installer найден: {builder.advinst_path}")

    # Запуск сборки
    success = builder.build_project(
        aip_file="C:/Projects/MyApp/MyApp.aip",
        callback=lambda msg: print(msg, end='')
    )

    if success:
        print("\nСборка успешно завершена!")
    else:
        print("\nСборка завершилась с ошибкой!")
else:
    print("Advanced Installer не найден!")
```

### Сборка с указанием пути к Advanced Installer

```python
from core.build_manager import BuildManager

# Создание менеджера с явным указанием пути
builder = BuildManager(
    advinst_path=r"C:\Program Files (x86)\Caphyon\Advanced Installer 22.1\bin\x86\AdvancedInstaller.com"
)

# Сборка с указанием папки вывода
success = builder.build_project(
    aip_file="MyApp.aip",
    output_folder="C:/Builds/MyApp",
    build_name="DefaultBuild",
    callback=print
)
```

### Ручная установка пути к Advanced Installer

```python
from core.build_manager import BuildManager

builder = BuildManager()

# Ручная установка пути
try:
    builder.set_advanced_installer_path(
        r"C:\Program Files\Caphyon\Advanced Installer 22.1\bin\x86\AdvancedInstaller.com"
    )
    print("Путь установлен успешно!")
except FileNotFoundError as e:
    print(f"Ошибка: {e}")
```

### Получение информации о сборке

```python
from core.build_manager import BuildManager

builder = BuildManager()

info = builder.get_build_info("MyApp.aip")
print(f"Билд по умолчанию: {info['default_build']}")
print(f"Advanced Installer доступен: {info['advinst_available']}")
print(f"Путь к AIP: {info['aip_file']}")
```

## Редактирование PowerShell скриптов

### Базовое редактирование

```python
from utils.powershell_editor import PowerShellEditor

# Открытие скрипта
editor = PowerShellEditor("C:/Scripts/Deploy-Application.ps1")

# Чтение содержимого
content = editor.read_script()
print("Текущее содержимое скрипта:")
print(content[:200])  # Первые 200 символов

# Модификация
new_content = content.replace("$AppVersion = '1.0'", "$AppVersion = '2.0'")

# Сохранение (автоматически создается резервная копия)
backup_path = editor.write_script(new_content, create_backup=True)
print(f"Резервная копия: {backup_path}")
```

### Создание версий

```python
from utils.powershell_editor import PowerShellEditor

editor = PowerShellEditor("Deploy-Application.ps1")

# Создание именованной версии
version_path = editor.create_version("before_major_changes")
print(f"Версия создана: {version_path}")

# Внесение изменений
content = editor.read_script()
modified = content + "\n# Добавлен новый функционал\n"
editor.write_script(modified)

# Создание еще одной версии
version_path2 = editor.create_version("after_new_feature")
```

### Управление версиями

```python
from utils.powershell_editor import PowerShellEditor

editor = PowerShellEditor("Deploy-Application.ps1")

# Список всех версий
versions = editor.list_versions()
print(f"Всего версий: {len(versions)}")

for version in versions:
    print(f"\nВерсия: {version['name']}")
    print(f"  Путь: {version['path']}")
    print(f"  Размер: {version['size']} байт")
    print(f"  Изменена: {version['modified']}")
```

### Восстановление версий

```python
from utils.powershell_editor import PowerShellEditor

editor = PowerShellEditor("Deploy-Application.ps1")

# Получение списка версий
versions = editor.list_versions()

if versions:
    # Восстановление последней версии
    latest_version = versions[0]
    editor.restore_version(
        latest_version['path'],
        create_backup=True  # Создать резервную копию перед восстановлением
    )
    print(f"Восстановлена версия: {latest_version['name']}")
```

### Поиск и замена

```python
from utils.powershell_editor import PowerShellEditor

editor = PowerShellEditor("Deploy-Application.ps1")

# Поиск и замена с учетом регистра
count = editor.find_and_replace(
    find_text="$OldVariable",
    replace_text="$NewVariable",
    case_sensitive=True,
    create_backup=True
)

print(f"Выполнено замен: {count}")

# Поиск и замена без учета регистра
count = editor.find_and_replace(
    find_text="oldvalue",
    replace_text="NewValue",
    case_sensitive=False
)

print(f"Выполнено замен (без учета регистра): {count}")
```

### Получение информации о скрипте

```python
from utils.powershell_editor import PowerShellEditor

editor = PowerShellEditor("Deploy-Application.ps1")

info = editor.get_script_info()
print(f"Имя: {info['name']}")
print(f"Путь: {info['path']}")
print(f"Размер: {info['size']} байт")
print(f"Изменен: {info['modified']}")
print(f"Количество версий: {info['versions_count']}")
print(f"Директория версий: {info['versions_dir']}")
```

### Очистка старых версий

```python
from utils.powershell_editor import PowerShellEditor

editor = PowerShellEditor("Deploy-Application.ps1")

# Удаление старых версий, оставить только 5 последних
deleted = editor.cleanup_old_versions(keep_count=5)
print(f"Удалено старых версий: {deleted}")
```

## Комплексный пример

### Полный цикл работы с проектом

```python
from core.aip_manager import AIPManager
from core.build_manager import BuildManager
from utils.image_converter import ImageConverter
from utils.powershell_editor import PowerShellEditor

# 1. Обновление информации о проекте
print("Шаг 1: Обновление информации о проекте...")
aip = AIPManager("MyApp.aip")
aip.create_backup()
aip.update_project_info(
    product_name="My Application",
    manufacturer="My Company",
    version="2.0.0"
)

# 2. Конвертация и применение новой иконки
print("\nШаг 2: Конвертация иконки...")
converter = ImageConverter()
icon_result = converter.convert_image_for_installer(
    "new_icon.png",
    "./",
    base_name="AppIcon"
)
aip.update_icon(icon_result['bmp'])
aip.save()
print(f"  Иконка обновлена: {icon_result['bmp']}")

# 3. Редактирование PowerShell скрипта
print("\nШаг 3: Обновление PowerShell скрипта...")
ps_editor = PowerShellEditor("Deploy-Application.ps1")
ps_editor.create_version("before_v2_update")

content = ps_editor.read_script()
updated_content = content.replace(
    "$AppVersion = '1.0'",
    "$AppVersion = '2.0.0'"
)
ps_editor.write_script(updated_content)
print("  Скрипт обновлен")

# 4. Запуск сборки
print("\nШаг 4: Запуск сборки...")
builder = BuildManager()
if builder.is_advanced_installer_available():
    success = builder.build_project(
        "MyApp.aip",
        output_folder="./builds",
        callback=lambda msg: print(f"  {msg}", end='')
    )

    if success:
        print("\n\nВсе операции завершены успешно!")
    else:
        print("\n\nСборка завершилась с ошибкой!")
else:
    print("  Advanced Installer не найден!")
```

## Обработка ошибок

### Правильная обработка исключений

```python
from core.aip_manager import AIPManager
from utils.image_converter import ImageConverter

try:
    # Попытка загрузить несуществующий проект
    aip = AIPManager("nonexistent.aip")
except FileNotFoundError as e:
    print(f"Файл не найден: {e}")
except ValueError as e:
    print(f"Ошибка формата файла: {e}")

try:
    # Попытка конвертировать неподдерживаемый формат
    converter = ImageConverter()
    converter.convert_to_ico("image.gif", "output.ico")
except ValueError as e:
    print(f"Неподдерживаемый формат: {e}")
except FileNotFoundError as e:
    print(f"Файл не найден: {e}")
```

## Советы и рекомендации

1. **Всегда создавайте резервные копии** перед внесением изменений
2. **Используйте систему версионирования** для PowerShell скриптов
3. **Проверяйте доступность Advanced Installer** перед попыткой сборки
4. **Используйте обработку исключений** для надежной работы
5. **Закрывайте файл .aip в Advanced Installer** перед программным редактированием
