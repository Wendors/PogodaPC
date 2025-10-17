"""
UI компоненти для PogodaPC
"""
import logging
from typing import Optional, Callable
from PySide6 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

class DraggableWidget(QtWidgets.QWidget):
    """Віджет, який можна перетягувати"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = None
        self._dragging = False
        
    def mousePressEvent(self, event):
        """Обробка натискання миші"""
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._dragging = True
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        """Обробка переміщення миші"""
        if (event.buttons() == QtCore.Qt.LeftButton and 
            self.drag_position is not None and 
            self._dragging):
            
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Обробка відпускання миші"""
        if event.button() == QtCore.Qt.LeftButton:
            self._dragging = False
            # Сигналізуємо про зміну позиції
            if hasattr(self, 'position_changed'):
                self.position_changed.emit(self.pos())
        super().mouseReleaseEvent(event)

class WeatherWidget(DraggableWidget):
    """Основний віджет погоди"""
    
    # Сигнали
    settings_requested = QtCore.Signal()
    position_changed = QtCore.Signal(QtCore.QPoint)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.createContextMenu()
        
    def setupUi(self):
        """Налаштування UI"""
        self.setObjectName("WeatherWidget")
        self.resize(300, 305)
        
        # Налаштування вікна
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        
        # Створюємо лейбли
        self.title_label = QtWidgets.QLabel(self)
        self.title_label.setGeometry(QtCore.QRect(0, 0, 301, 61))
        self.title_label.setText("За вікном!!!")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setGeometry(QtCore.QRect(10, 50, 271, 181))
        self.icon_label.setScaledContents(True)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.temperature_label = QtWidgets.QLabel(self)
        self.temperature_label.setGeometry(QtCore.QRect(10, 220, 281, 71))
        self.temperature_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Налаштування стилів
        self.setupStyles()
        
    def setupStyles(self):
        """Налаштування стилів віджетів"""
        # Стиль заголовка
        title_font = QtGui.QFont()
        title_font.setFamily("Arial Black")
        title_font.setPointSize(31)
        title_font.setBold(True)
        title_font.setItalic(True)
        title_font.setUnderline(True)
        title_font.setWeight(QtGui.QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        
        # Палітра для заголовка
        title_palette = QtGui.QPalette()
        title_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 255))
        self.title_label.setPalette(title_palette)
        
        # Тінь для заголовка
        title_shadow = QtWidgets.QGraphicsDropShadowEffect()
        title_shadow.setBlurRadius(2)
        title_shadow.setColor(QtGui.QColor(0, 0, 0))
        title_shadow.setOffset(5)
        self.title_label.setGraphicsEffect(title_shadow)
        
        # Тінь для іконки
        icon_shadow = QtWidgets.QGraphicsDropShadowEffect()
        icon_shadow.setBlurRadius(2)
        icon_shadow.setColor(QtGui.QColor(0, 0, 0))
        icon_shadow.setOffset(5)
        self.icon_label.setGraphicsEffect(icon_shadow)
        
        # Стиль температури
        temp_font = QtGui.QFont()
        temp_font.setFamily("Cooper Black")
        temp_font.setPointSize(60)
        temp_font.setBold(True)
        temp_font.setWeight(QtGui.QFont.Weight.Bold)
        self.temperature_label.setFont(temp_font)
        
        # Палітра для температури
        temp_palette = QtGui.QPalette()
        temp_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 255))
        self.temperature_label.setPalette(temp_palette)
        
        # Тінь для температури
        temp_shadow = QtWidgets.QGraphicsDropShadowEffect()
        temp_shadow.setBlurRadius(2)
        temp_shadow.setColor(QtGui.QColor(0, 0, 0))
        temp_shadow.setOffset(5)
        self.temperature_label.setGraphicsEffect(temp_shadow)
        
    def createContextMenu(self):
        """Створює контекстне меню"""
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        
    def showContextMenu(self, position):
        """Показує контекстне меню"""
        context_menu = QtWidgets.QMenu(self)
        
        # Налаштування
        settings_action = context_menu.addAction("Налаштування")
        settings_action.triggered.connect(self.settings_requested.emit)
        
        # Оновити
        refresh_action = context_menu.addAction("Оновити зараз")
        refresh_action.triggered.connect(self.request_update)
        
        context_menu.addSeparator()
        
        # Вихід
        exit_action = context_menu.addAction("Вихід")
        exit_action.triggered.connect(QtWidgets.QApplication.quit)
        
        context_menu.exec(self.mapToGlobal(position))
        
    def request_update(self):
        """Запитує оновлення даних"""
        if hasattr(self, 'update_requested'):
            self.update_requested.emit()
            
    def mouseDoubleClickEvent(self, event):
        """Обробка подвійного кліку"""
        if event.button() == QtCore.Qt.LeftButton:
            self.settings_requested.emit()
        super().mouseDoubleClickEvent(event)
        
    def set_title(self, title: str):
        """Встановлює заголовок"""
        self.title_label.setText(title)
        
    def set_temperature(self, temperature: str):
        """Встановлює температуру"""
        self.temperature_label.setText(temperature)
        
    def set_icon(self, pixmap: QtGui.QPixmap):
        """Встановлює іконку погоди"""
        self.icon_label.setPixmap(pixmap)
        
    def clear_icon(self):
        """Очищає іконку"""
        empty_pixmap = QtGui.QPixmap(1, 1)
        empty_pixmap.fill(QtCore.Qt.transparent)
        self.icon_label.setPixmap(empty_pixmap)
        
    def set_loading_state(self):
        """Встановлює стан завантаження"""
        self.set_title("Оновлення...")
        self.clear_icon()
        self.set_temperature("--°")
        
    def set_error_state(self, error_message: str = "Помилка мережі"):
        """Встановлює стан помилки"""
        self.set_title(error_message)
        self.clear_icon()
        self.set_temperature("")

class SettingsDialog(QtWidgets.QDialog):
    """Розширене вікно налаштувань"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.setWindowTitle("Налаштування PogodaPC")
        self.setFixedSize(500, 400)
        self.setWindowIcon(QtGui.QIcon("PogodaPC.ico"))
        
    def setupUI(self):
        """Налаштування UI діалогу"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Заголовок
        title = QtWidgets.QLabel("Налаштування PogodaPC")
        title.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Створюємо tabs
        tab_widget = QtWidgets.QTabWidget()
        
        # Вкладка загальних налаштувань
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "Загальні")
        
        # Вкладка позиції
        position_tab = self.create_position_tab()
        tab_widget.addTab(position_tab, "Позиція")
        
        layout.addWidget(tab_widget)
        
        # Кнопки
        button_layout = QtWidgets.QHBoxLayout()
        
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        self.ok_button.setDefault(True)
        
        self.cancel_button = QtWidgets.QPushButton("Скасувати")
        self.cancel_button.clicked.connect(self.reject)
        
        self.reset_button = QtWidgets.QPushButton("Скинути")
        self.reset_button.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def create_general_tab(self):
        """Створює вкладку загальних налаштувань"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        
        # URL адреса
        layout.addRow(QtWidgets.QLabel("URL адреса погоди:"))
        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setPlaceholderText("https://sinoptik.ua/pohoda/ваше_місто")
        layout.addRow(self.url_input)
        
        # Опис URL
        url_help = QtWidgets.QLabel(
            "Введіть URL адресу вашого міста з сайту sinoptik.ua\\n"
            "Наприклад: https://sinoptik.ua/pohoda/kyiv"
        )
        url_help.setWordWrap(True)
        url_help.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow(url_help)
        
        layout.addRow(QtWidgets.QLabel(""))  # Роздільник
        
        # Інтервал оновлення
        layout.addRow(QtWidgets.QLabel("Інтервал оновлення (хвилини):"))
        self.interval_spin = QtWidgets.QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(1440)  # 24 години
        self.interval_spin.setValue(30)
        layout.addRow(self.interval_spin)
        
        # Автооновлення
        self.auto_update_check = QtWidgets.QCheckBox("Автоматичне оновлення")
        self.auto_update_check.setChecked(True)
        layout.addRow(self.auto_update_check)
        
        return widget
        
    def create_position_tab(self):
        """Створює вкладку налаштувань позиції"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        
        # Автопозиціонування
        self.auto_position_check = QtWidgets.QCheckBox("Автоматичне розташування")
        self.auto_position_check.setChecked(True)
        self.auto_position_check.toggled.connect(self.toggle_manual_position)
        layout.addRow(self.auto_position_check)
        
        layout.addRow(QtWidgets.QLabel(""))  # Роздільник
        
        # Ручне розташування
        self.manual_group = QtWidgets.QGroupBox("Ручне розташування")
        self.manual_group.setEnabled(False)
        manual_layout = QtWidgets.QFormLayout(self.manual_group)
        
        self.x_spin = QtWidgets.QSpinBox()
        self.x_spin.setMinimum(0)
        self.x_spin.setMaximum(9999)
        manual_layout.addRow("X координата:", self.x_spin)
        
        self.y_spin = QtWidgets.QSpinBox()
        self.y_spin.setMinimum(0)
        self.y_spin.setMaximum(9999)
        manual_layout.addRow("Y координата:", self.y_spin)
        
        layout.addRow(self.manual_group)
        
        return widget
        
    def toggle_manual_position(self, checked):
        """Перемикає ручне позиціонування"""
        self.manual_group.setEnabled(not checked)
        
    def accept_settings(self):
        """Перевіряє та приймає налаштування"""
        # Валідація URL
        url = self.url_input.text().strip()
        if not url:
            QtWidgets.QMessageBox.warning(self, "Помилка", "Будь ласка, введіть URL адресу!")
            return
            
        if not url.startswith("https://sinoptik.ua/"):
            QtWidgets.QMessageBox.warning(
                self, "Помилка", 
                "URL повинен починатися з https://sinoptik.ua/"
            )
            return
            
        self.accept()
        
    def reset_settings(self):
        """Скидає налаштування до значень за замовчуванням"""
        reply = QtWidgets.QMessageBox.question(
            self, "Скидання налаштувань",
            "Ви впевнені, що хочете скинути всі налаштування?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.load_default_settings()
            
    def load_default_settings(self):
        """Завантажує налаштування за замовчуванням"""
        self.url_input.setText("https://sinoptik.ua/pohoda/truskavets")
        self.interval_spin.setValue(30)
        self.auto_update_check.setChecked(True)
        self.auto_position_check.setChecked(True)
        self.x_spin.setValue(0)
        self.y_spin.setValue(370)
        
    def get_settings(self):
        """Повертає поточні налаштування"""
        return {
            'weather_url': self.url_input.text().strip(),
            'update_interval': self.interval_spin.value() * 60,  # Конвертуємо в секунди
            'auto_update': self.auto_update_check.isChecked(),
            'auto_position': self.auto_position_check.isChecked(),
            'x_position': self.x_spin.value() if not self.auto_position_check.isChecked() else None,
            'y_position': self.y_spin.value()
        }
        
    def set_settings(self, settings):
        """Встановлює налаштування у форму"""
        self.url_input.setText(settings.get('weather_url', ''))
        self.interval_spin.setValue(settings.get('update_interval', 1800) // 60)  # Конвертуємо з секунд
        self.auto_update_check.setChecked(settings.get('auto_update', True))
        
        auto_pos = settings.get('auto_position', True)
        self.auto_position_check.setChecked(auto_pos)
        
        if not auto_pos:
            self.x_spin.setValue(settings.get('x_position', 0))
        self.y_spin.setValue(settings.get('y_position', 370))