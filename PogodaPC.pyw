"""Program: PogodaPC."""

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PogodaPC.ui'
#
# Created by: PySide6 UI code generator
#
# WARNING! All changes made in this file will be lost!

# import module
import os
import sys
import tempfile
import json
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
from PySide6 import QtCore, QtGui, QtWidgets

# PySide6 автоматично підтримує High DPI


class Ui_Form(object):
    """Class Ui_Form"""

    def setupUi(self, Form):
        """SetupUi"""
        # Ініціалізуємо прапор оновлення
        self.updating = False
        
        Form.setObjectName("Form")
        Form.resize(300, 305)
        # PySide6: використовуємо сучасний Screen API
        self.screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = self.screen.geometry()
        Form.move(int(screen_geometry.width() - 300), 370)
        Form.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        Form.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(0, 0, 301, 61))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label.setPalette(palette)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(2)
        self.shadow.setColor(QtGui.QColor(0, 0, 0))
        self.shadow.setOffset(5)
        self.label.setGraphicsEffect(self.shadow)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(31)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(QtGui.QFont.Weight.Bold)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 271, 181))
        self.shadow_2 = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow_2.setBlurRadius(2)
        self.shadow_2.setColor(QtGui.QColor(0, 0, 0))
        self.shadow_2.setOffset(5)
        self.label_2.setGraphicsEffect(self.shadow_2)
        self.label_2.setText("")
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(10, 220, 281, 71))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label_3.setPalette(palette)
        self.shadow_3 = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow_3.setBlurRadius(2)
        self.shadow_3.setColor(QtGui.QColor(0, 0, 0))
        self.shadow_3.setOffset(5)
        self.label_3.setGraphicsEffect(self.shadow_3)
        font = QtGui.QFont()
        font.setFamily("Cooper Black")
        font.setPointSize(60)
        font.setBold(True)
        font.setWeight(QtGui.QFont.Weight.Bold)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        
        # Додаємо обробку подвійного кліку для відкриття налаштувань
        Form.mouseDoubleClickEvent = self.open_settings

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", ""))
        self.label_3.setText(_translate("Form", ""))
        
    def open_settings(self, event):
        """Відкриває вікно налаштувань при подвійному кліці"""
        try:
            # Перевіряємо, чи не відбувається вже оновлення
            if hasattr(self, 'updating') and self.updating:
                print("Оновлення вже відбувається, пропускаємо...")
                return
                
            if not hasattr(self, 'config_manager'):
                self.config_manager = ConfigManager()
                
            settings_dialog = SettingsDialog()
            current_url = self.config_manager.get_weather_url()
            if current_url:
                settings_dialog.url_input.setText(current_url)
                
            if settings_dialog.exec() == QtWidgets.QDialog.Accepted:
                url = settings_dialog.get_url()
                if url:
                    if self.config_manager.set_weather_url(url):
                        print(f"URL оновлено: {url}")
                        # Показуємо повідомлення про оновлення
                        self.label.setText("Оновлення...")
                        # Встановлюємо прапор оновлення
                        self.updating = True
                        # Запланувати оновлення через таймер
                        QtCore.QTimer.singleShot(2000, self.safe_update)
                    else:
                        print("Помилка збереження URL")
        except Exception as e:
            print(f"Помилка при відкритті налаштувань: {e}")
            
    def safe_update(self):
        """Безпечне оновлення з захистом від повторних викликів"""
        try:
            self.upd()
        except Exception as e:
            print(f"Помилка в safe_update: {e}")
        finally:
            # Скидаємо прапор оновлення
            self.updating = False

    def upd(self):
        # Перевіряємо, чи не відбувається вже оновлення
        if hasattr(self, 'updating') and self.updating:
            print("Оновлення вже відбувається, пропускаємо...")
            return
            
        self.updating = True
        print("Початок оновлення...")
        try:
            self.paths = tempfile.gettempdir() + "/"
            # Отримуємо URL з конфігурації
            if not hasattr(self, 'config_manager'):
                self.config_manager = ConfigManager()
            
            weather_url = self.config_manager.get_weather_url()
            if not weather_url:
                weather_url = "https://sinoptik.ua/pohoda/truskavets"  # За замовчуванням
            
            print(f"Використовується URL: {weather_url}")
            
            self.urs = Request(
                weather_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"
                },
            )
            print("Request створено, отримуємо дані...")
            self.html_doc = urlopen(self.urs).read()
            print("HTML отримано, парсимо...")
            self.soup = BeautifulSoup(self.html_doc, "html.parser")
            
            # Шукаємо зображення за різними можливими селекторами
            print("Шукаємо зображення...")
            self.linc = None
            
            # Список можливих селекторів для блоку з погодою
            weather_selectors = [
                "qyyKXdcq",  # Старий селектор
                "weather-block",
                "today-weather",
                "current-weather",
                "main-weather"
            ]
            
            # Пробуємо знайти блок з погодою
            weather_block = None
            for selector in weather_selectors:
                weather_block = self.soup.find("div", selector)
                if weather_block:
                    print(f"Знайдено блок погоди з селектором: {selector}")
                    break
            
            # Якщо специфічний блок не знайдено, шукаємо зображення по всій сторінці
            if not weather_block:
                print("Специфічний блок не знайдено, шукаємо зображення по всій сторінці...")
                weather_block = self.soup
            
            # Шукаємо зображення погоди
            try:
                images = weather_block.find_all("img")
                print(f"Знайдено {len(images)} зображень")
                
                for i, img in enumerate(images):
                    img_str = str(img)
                    print(f"Зображення {i}: {img_str[:100]}...")
                    
                    # Шукаємо зображення, що містить погодні іконки
                    if ("src" in img_str and 
                        (".png" in img_str or ".jpg" in img_str) and
                        ("weather" in img_str.lower() or 
                         "icon" in img_str.lower() or
                         "pogoda" in img_str.lower() or
                         "/p/" in img_str)):
                        
                        # Витягуємо src
                        src_attr = img.get('src')
                        if src_attr:
                            if src_attr.startswith('http'):
                                self.linc = src_attr
                            elif src_attr.startswith('/'):
                                self.linc = "https://sinoptik.ua" + src_attr
                            else:
                                self.linc = "https://sinoptik.ua/" + src_attr
                            print(f"Знайдено зображення: {self.linc}")
                            break
                            
            except Exception as img_error:
                print(f"Помилка при пошуку зображення: {img_error}")
            
            # Якщо зображення не знайдено, створюємо заглушку
            if not self.linc:
                print("Зображення не знайдено, створюємо заглушку")
                # Не викидаємо помилку, просто продовжуємо без зображення
                self.linc = None
            
            # Шукаємо температуру за різними селекторами
            print("Шукаємо температуру...")
            temperature = None
            
            # Список можливих селекторів для температури
            temp_selectors = [
                ("p", "R1ENpvZz"),  # Старий селектор
                ("div", "temperature"),
                ("span", "temp"),
                ("div", "temp-value"),
                ("span", "temperature-value")
            ]
            
            # Пробуємо знайти температуру
            for tag, class_name in temp_selectors:
                temp_element = self.soup.find(tag, class_name)
                if temp_element:
                    if temp_element.string:
                        temperature = str(temp_element.string).strip()
                        break
                    else:
                        # Шукаємо текст в дочірніх елементах
                        text = temp_element.get_text().strip()
                        if text and any(char.isdigit() for char in text):
                            temperature = text
                            break
            
            # Якщо не знайдено за селекторами, шукаємо за регулярними виразами
            if not temperature:
                import re
                # Шукаємо паттерн температури в HTML
                temp_pattern = r'[-+]?\d+\s*[°С℃]'
                matches = re.findall(temp_pattern, str(self.soup))
                if matches:
                    temperature = matches[0]
                    print(f"Температура знайдена за регулярним виразом: {temperature}")
            
            if temperature:
                self.label_3.setText(temperature)
                print(f"Встановлено температуру: {temperature}")
            else:
                print("Температуру не знайдено")
                self.label_3.setText("--°")
            
            # Обробляємо зображення, якщо воно знайдено
            if self.linc:
                try:
                    print(f"Завантажуємо зображення з: {self.linc}")
                    self.uri = Request(self.linc)
                    self.uri.add_header(
                        "User-Agent",
                        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,"
                        " like Gecko) Chrome/45.0.2454.85 Safari/537.36 ",
                    )
                    self.ur = urlopen(self.uri)
                    self.fil = open(self.paths + "11.jpg", "wb")
                    self.fil.write(self.ur.read())
                    self.fil.close()
                    self.ur.close()
                    print("Обробляємо зображення...")
                    self.im = Image.open(self.paths + "11.jpg")
                    self.im.save(self.paths + "11.png", "PNG")
                    self.im = Image.open(self.paths + "11.png")
                    self.pix = self.im.load()
                    self.xx, self.yy = self.im.size
                    # Обработка изображения убераем белый фон и оставляем только саму картинку
                    self.x = 0
                    self.y = 0
                    while self.x < self.xx and self.y < self.yy:
                        if self.pix[self.x, self.y] == (255, 255, 255):
                            self.pix[self.x, self.y] = (0, 0, 0, 0)
                        self.x += 1
                        if self.x == self.xx:
                            self.y += 1
                            self.x = 0
                    self.im.save(self.paths + "11.png", "PNG")
                    self.mask = Image.open(self.paths + "11.png").convert("L")
                    self.output = ImageOps.fit(self.im, self.mask.size, centering=(0.5, 0.5))
                    self.output.putalpha(self.mask)
                    self.output.save(self.paths + "output.png")
                    print("Встановлюємо зображення...")
                    self.label_2.setPixmap(QtGui.QPixmap(self.paths + "output.png"))
                    try:
                        os.remove(self.paths + "11.jpg")
                        os.remove(self.paths + "11.png")
                        os.remove(self.paths + "11.png")
                    except:
                        pass
                except Exception as img_download_error:
                    print(f"Помилка завантаження зображення: {img_download_error}")
                    # Створюємо порожнє зображення
                    empty_pixmap = QtGui.QPixmap(100, 100)
                    empty_pixmap.fill(QtCore.Qt.transparent)
                    self.label_2.setPixmap(empty_pixmap)
            else:
                print("Зображення не знайдено, встановлюємо порожнє")
                # Створюємо порожнє зображення
                empty_pixmap = QtGui.QPixmap(100, 100)
                empty_pixmap.fill(QtCore.Qt.transparent)
                self.label_2.setPixmap(empty_pixmap)
            
            print("Оновлюємо інтерфейс...")
            self.label.setText("За вікном!!!")
            self.timer.setInterval(1800000)
            print("Оновлення завершено успішно!")
        except Exception as e:
            print(f"ДЕТАЛЬНА ПОМИЛКА при оновленні погоди: {e}")
            print(f"Тип помилки: {type(e).__name__}")
            import traceback
            print(f"Трасування: {traceback.format_exc()}")
            self.label.setText("Нет сети!!!")
            # Створюємо пустий pixmap замість None
            empty_pixmap = QtGui.QPixmap(1, 1)
            empty_pixmap.fill(QtCore.Qt.transparent)
            self.label_2.setPixmap(empty_pixmap)
            self.label_3.setText("")
            self.timer.setInterval(1000)
        finally:
            # Скидаємо прапор оновлення
            self.updating = False

    def Timers(self):
        # Ініціалізуємо config_manager, якщо ще не ініціалізований
        if not hasattr(self, 'config_manager'):
            self.config_manager = ConfigManager()
            
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.upd)
        self.timer.start()


class SettingsDialog(QtWidgets.QDialog):
    """Вікно налаштувань для вводу URL"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.setWindowTitle("Налаштування PogodaPC")
        self.setFixedSize(400, 200)
        self.setWindowIcon(QtGui.QIcon("PogodaPC.ico"))
        
    def setupUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Заголовок
        title = QtWidgets.QLabel("Налаштування адреси погоди")
        title.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Опис
        description = QtWidgets.QLabel(
            "Введіть URL адресу вашого міста з сайту sinoptik.ua\n"
            "Наприклад: https://sinoptik.ua/pohoda/kyiv"
        )
        description.setAlignment(QtCore.Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Поле для URL
        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setPlaceholderText("https://sinoptik.ua/pohoda/ваше_місто")
        self.url_input.setText("https://sinoptik.ua/pohoda/truskavets")  # Значення за замовчуванням
        layout.addWidget(self.url_input)
        
        # Кнопки
        button_layout = QtWidgets.QHBoxLayout()
        
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_url)
        self.ok_button.setDefault(True)
        
        self.cancel_button = QtWidgets.QPushButton("Скасувати")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def accept_url(self):
        """Перевіряє URL перед закриттям діалогу"""
        url = self.url_input.text().strip()
        if not url:
            QtWidgets.QMessageBox.warning(self, "Помилка", "Будь ласка, введіть URL адресу!")
            return
        
        if not url.startswith("https://sinoptik.ua/"):
            QtWidgets.QMessageBox.warning(self, "Помилка", 
                "URL повинен починатися з https://sinoptik.ua/")
            return
            
        self.accept()
        
    def get_url(self):
        """Повертає введений URL"""
        return self.url_input.text().strip()


class ConfigManager:
    """Менеджер конфігурації для збереження налаштувань"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser("~"), ".pogodapc_config.json")
        
    def load_config(self):
        """Завантажує конфігурацію з файлу"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Помилка завантаження конфігурації: {e}")
        return {}
        
    def save_config(self, config):
        """Зберігає конфігурацію у файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Помилка збереження конфігурації: {e}")
            return False
            
    def get_weather_url(self):
        """Отримує URL погоди з конфігурації"""
        config = self.load_config()
        return config.get('weather_url', '')
        
    def set_weather_url(self, url):
        """Зберігає URL погоди в конфігурації"""
        config = self.load_config()
        config['weather_url'] = url
        return self.save_config(config)


if __name__ == "__main__":
    if sys.platform == "win32":
        import winreg

        try:
            regs = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            mykeys = winreg.OpenKey(
                regs,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_ALL_ACCESS,
            )
            winreg.DeleteValue(mykeys, "PogodaPC")
            winreg.CloseKey(mykeys)
        except:
            pass
        regs = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        mykeys = winreg.OpenKey(
            regs,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_ALL_ACCESS,
        )
        # winreg.SetValueEx(mykeys, 'PogodaPC', 0, winreg.REG_SZ,'"' + sys.argv[0] + '"' + " Minimum")
        winreg.CloseKey(mykeys)
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Перевіряємо наявність конфігурації
    config_manager = ConfigManager()
    weather_url = config_manager.get_weather_url()
    
    # Якщо URL не збережений, показуємо вікно налаштувань
    if not weather_url:
        settings_dialog = SettingsDialog()
        if settings_dialog.exec() == QtWidgets.QDialog.Accepted:
            url = settings_dialog.get_url()
            if url:
                config_manager.set_weather_url(url)
                print(f"URL збережено: {url}")
            else:
                print("URL не введено, використовується за замовчуванням")
        else:
            print("Налаштування скасовано, використовується URL за замовчуванням")
    
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    ui.Timers()
    Form.show()
    sys.exit(app.exec())
