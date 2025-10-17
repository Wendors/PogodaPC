# PogodaPC - Віджет Погоди для ПК

## Опис
PogodaPC - це простий віджет погоди для робочого столу, який відображає поточну температуру та іконку погоди з сайту sinoptik.ua. Програма працює як накладка поверх інших вікон без рамок.

## Останні зміни
**Версія v.3.7.2-86 - PySide6**
- ✅ Повна підтримка PySide6
- ✅ Оновлення всіх залежностей
- ✅ Виправлення проблем сумісності
- ✅ Підтримка сучасних версій Qt

## Особливості
- Автоматичне оновлення погоди кожні 30 хвилин
- Прозорий фон та тіні для тексту
- Розташування у правому верхньому куті екрана
- Обробка помилок мережі
- Кросплатформна підтримка (Linux, Windows, macOS)
- **Вікно налаштувань при першому запуску**
- **Збереження URL адреси у конфігураційному файлі**
- **Можливість зміни налаштувань подвійним кліком по віджету**

## Системні вимоги
- Python 3.8+
- PySide6
- BeautifulSoup4
- Pillow
- urllib (стандартна бібліотека)

## Встановлення

### 1. Клонування репозиторію
```bash
git clone https://github.com/Wendors/PogodaPC.git
cd PogodaPC
```

### 2. Створення віртуального середовища (рекомендовано)
```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
# або
venv\Scripts\activate     # для Windows
```

### 3. Встановлення залежностей
```bash
pip install PySide6 beautifulsoup4 Pillow pyinstaller
```

## Використання

### Запуск програми
```bash
python PogodaPC.pyw
```

### Генерація UI з .ui файлу (якщо потрібно)
```bash
python pyside6.py
```

### Створення виконуваного файлу
```bash
python pyinstaler.py
```

## Структура проекту
```
PogodaPC/
├── PogodaPC.pyw        # Основний файл програми
├── PogodaPC.ui         # UI файл (Qt Designer)
├── pyside6.py          # Скрипт для конвертації UI
├── pyinstaler.py       # Скрипт для створення виконуваного файлу
├── reset_settings.py   # Скрипт для скидання налаштувань
├── requirements.txt    # Список залежностей
├── TROUBLESHOOTING.md  # Усунення проблем
└── README.md          # Цей файл
```

## Налаштування

### Вікно налаштувань
При першому запуску програми з'явиться вікно налаштувань, де потрібно ввести URL адресу вашого міста з сайту sinoptik.ua.

**Як знайти URL вашого міста:**
1. Відкрийте https://sinoptik.ua
2. Знайдіть ваше місто
3. Скопіюйте повний URL (наприклад: https://sinoptik.ua/pohoda/kyiv)
4. Вставте його у вікно налаштувань

### Зміна налаштувань
- **Подвійний клік** по віджету відкриє вікно налаштувань
- Або видаліть файл `~/.pogodapc_config.json` та перезапустіть програму
- Або використайте скрипт: `python reset_settings.py`

### Зміна позиції вікна
Змініть координати у методі `setupUi()`:
```python
Form.move(int(screen_geometry.width() - 300), 370)  # x, y координати
```

## Файли конфігурації

### Розташування
- **Linux/macOS:** `~/.pogodapc_config.json`
- **Windows:** `%USERPROFILE%\.pogodapc_config.json`

### Формат файлу
```json
{
  "weather_url": "https://sinoptik.ua/pohoda/your_city"
}
```

### Скидання налаштувань
```bash
python reset_settings.py
```
або видаліть файл конфігурації вручну:
```bash
rm ~/.pogodapc_config.json  # Linux/macOS
del %USERPROFILE%\.pogodapc_config.json  # Windows
```

## Технічні особливості PySide6

### API Changes від попередніх версій:
1. **Імпорти:**
   ```python
   from PySide6 import QtCore, QtGui, QtWidgets
   ```

2. **High DPI підтримка:**
   ```python
   # В PySide6 автоматично підтримується, додаткові налаштування не потрібні
   ```

3. **Screen API:**
   ```python
   # Сучасний підхід:
   self.screen = QtWidgets.QApplication.primaryScreen()
   screen_geometry = self.screen.geometry()
   Form.move(int(screen_geometry.width() - 300), 370)
   ```

4. **Font Weight:**
   ```python
   # PySide6 використовує enum:
   font.setWeight(QtGui.QFont.Weight.Bold)
   ```

5. **Application exec:**
   ```python
   # Оновлений метод:
   sys.exit(app.exec())
   ```

## Збірка виконуваного файлу

Скрипт `pyinstaler.py` автоматично визначає операційну систему та використовує відповідні налаштування:

### Linux/macOS:
```bash
python pyinstaler.py
```

Створює виконуваний файл у папці `dist/PogodaPC/`

### Windows:
Скрипт автоматично знайде шляхи до PySide6.

## Усунення несправностей

### Проблема: "Нет сети!!!"
- Перевірте інтернет-з'єднання
- Переконайтеся, що сайт sinoptik.ua доступний
- Програма автоматично спробує знову через 1 секунду

### Проблема: Програма не запускається
- Переконайтеся, що всі залежності встановлені
- Перевірте версію Python (потрібен 3.8+)
- Запустіть з терміналу для перегляду помилок

### Проблема: Помилки PyInstaller
- Переконайтеся, що pyinstaller встановлений
- На Linux може знадобитися встановити додаткові пакети:
  ```bash
  sudo apt-get install python3-dev
  ```

## Автозапуск

### Linux (systemd):
Створіть файл `~/.config/systemd/user/pogodapc.service`:
```ini
[Unit]
Description=PogodaPC Weather Widget
After=graphical-session.target

[Service]
Type=simple
ExecStart=/path/to/PogodaPC/PogodaPC
Restart=always

[Install]
WantedBy=default.target
```

Увімкніть автозапуск:
```bash
systemctl --user enable pogodapc.service
systemctl --user start pogodapc.service
```

### Windows:
Додайте до автозапуску через Task Scheduler або реєстр.

## Автор
**Сергій Полунець**

## Ліцензія
Проект розповсюджується під відкритою ліцензією. Детальніше див. у файлі LICENSE.

## Підтримка
При виникненні проблем або питань:
- Перегляньте файл [TROUBLESHOOTING.md](TROUBLESHOOTING.md) для усунення проблем
- Створіть Issue в репозиторії GitHub

---

**Версія документації:** 2025.10.17  
**Сумісність:** PySide6, Python 3.8+