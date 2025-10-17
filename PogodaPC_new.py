#!/usr/bin/env python3
"""
PogodaPC - Віджет погоди для робочого столу
Покращена версія з модульною архітектурою
"""

import sys
import os
import logging
from typing import Optional
from PySide6 import QtCore, QtGui, QtWidgets

# Додаємо поточну директорію до шляху для імпорту модулів
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from weather_parser import WeatherParser, WeatherData
from ui_components import WeatherWidget, SettingsDialog

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeatherApp(QtCore.QObject):
    """Головний клас програми"""
    
    def __init__(self):
        super().__init__()
        
        # Ініціалізація компонентів
        self.config_manager = ConfigManager()
        self.weather_parser = WeatherParser()
        self.weather_widget = WeatherWidget()
        
        # Таймер для оновлення
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_weather)
        
        # Підключення сигналів
        self.setup_connections()
        
        # Налаштування позиції вікна
        self.setup_window_position()
        
        # Налаштування таймера
        self.setup_update_timer()
        
        # Перше оновлення
        self.update_weather()
        
    def setup_connections(self):
        """Налаштування з'єднань сигналів та слотів"""
        self.weather_widget.settings_requested.connect(self.show_settings)
        self.weather_widget.position_changed.connect(self.save_window_position)
        
        # Додаємо сигнал для ручного оновлення
        if hasattr(self.weather_widget, 'update_requested'):
            self.weather_widget.update_requested.connect(self.update_weather)
            
    def setup_window_position(self):
        """Налаштування позиції вікна"""
        position = self.config_manager.get_window_position()
        size = self.config_manager.get_window_size()
        
        # Встановлюємо розмір
        self.weather_widget.resize(size['width'], size['height'])
        
        # Встановлюємо позицію
        if position['x'] is not None:
            # Ручна позиція
            self.weather_widget.move(position['x'], position['y'])
        else:
            # Автоматична позиція (правий верхній кут)
            screen = QtWidgets.QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            x = screen_geometry.width() - size['width']
            y = position['y']
            self.weather_widget.move(x, y)
            
    def setup_update_timer(self):
        """Налаштування таймера оновлення"""
        interval = self.config_manager.get_update_interval()
        auto_update = self.config_manager.get('auto_update', True)
        
        if auto_update:
            self.update_timer.start(interval * 1000)  # Конвертуємо в мілісекунди
            logger.info(f"Автооновлення налаштовано на {interval} секунд")
        else:
            logger.info("Автооновлення вимкнено")
            
    def update_weather(self):
        """Оновлення даних про погоду"""
        try:
            # Встановлюємо стан завантаження
            self.weather_widget.set_loading_state()
            
            # Отримуємо URL
            url = self.config_manager.get_weather_url()
            logger.info(f"Оновлення погоди з URL: {url}")
            
            # Завантажуємо дані в окремому потоці
            self.worker_thread = WeatherUpdateWorker(self.weather_parser, url)
            self.worker_thread.data_ready.connect(self.on_weather_data_ready)
            self.worker_thread.error_occurred.connect(self.on_weather_error)
            self.worker_thread.start()
            
        except Exception as e:
            logger.error(f"Помилка запуску оновлення: {e}")
            self.weather_widget.set_error_state("Помилка оновлення")
            
    def on_weather_data_ready(self, weather_data: WeatherData):
        """Обробка отриманих даних про погоду"""
        try:
            if weather_data.is_valid():
                # Оновлюємо інтерфейс
                self.weather_widget.set_title("За вікном!!!")
                
                if weather_data.temperature:
                    self.weather_widget.set_temperature(weather_data.temperature)
                    
                if weather_data.icon_path and os.path.exists(weather_data.icon_path):
                    pixmap = QtGui.QPixmap(weather_data.icon_path)
                    self.weather_widget.set_icon(pixmap)
                else:
                    self.weather_widget.clear_icon()
                    
                logger.info("Дані про погоду успішно оновлено")
            else:
                self.weather_widget.set_error_state("Дані недоступні")
                logger.warning("Отримано недійсні дані про погоду")
                
        except Exception as e:
            logger.error(f"Помилка обробки даних про погоду: {e}")
            self.weather_widget.set_error_state("Помилка обробки")
            
    def on_weather_error(self, error_message: str):
        """Обробка помилки оновлення погоди"""
        logger.error(f"Помилка оновлення погоди: {error_message}")
        self.weather_widget.set_error_state("Помилка мережі")
        
    def show_settings(self):
        """Показує діалог налаштувань"""
        try:
            dialog = SettingsDialog(self.weather_widget)
            
            # Завантажуємо поточні налаштування
            current_settings = {
                'weather_url': self.config_manager.get_weather_url(),
                'update_interval': self.config_manager.get_update_interval(),
                'auto_update': self.config_manager.get('auto_update', True),
                'auto_position': self.config_manager.get_window_position()['x'] is None,
                'x_position': self.config_manager.get_window_position()['x'] or 0,
                'y_position': self.config_manager.get_window_position()['y']
            }
            
            dialog.set_settings(current_settings)
            
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                # Зберігаємо нові налаштування
                new_settings = dialog.get_settings()
                self.apply_settings(new_settings)
                
        except Exception as e:
            logger.error(f"Помилка відкриття налаштувань: {e}")
            
    def apply_settings(self, settings: dict):
        """Застосовує нові налаштування"""
        try:
            # Зберігаємо URL
            if self.config_manager.set_weather_url(settings['weather_url']):
                logger.info(f"URL оновлено: {settings['weather_url']}")
                
            # Зберігаємо інтервал оновлення
            self.config_manager.set_update_interval(settings['update_interval'])
            
            # Зберігаємо автооновлення
            self.config_manager.set('auto_update', settings['auto_update'])
            
            # Зберігаємо позицію
            if settings['auto_position']:
                self.config_manager.set_window_position(None, settings['y_position'])
            else:
                self.config_manager.set_window_position(settings['x_position'], settings['y_position'])
                
            # Перезапускаємо таймер
            self.update_timer.stop()
            self.setup_update_timer()
            
            # Оновлюємо позицію вікна
            self.setup_window_position()
            
            # Запускаємо оновлення з новими налаштуваннями
            QtCore.QTimer.singleShot(1000, self.update_weather)
            
            logger.info("Налаштування успішно застосовано")
            
        except Exception as e:
            logger.error(f"Помилка застосування налаштувань: {e}")
            
    def save_window_position(self, position: QtCore.QPoint):
        """Зберігає позицію вікна"""
        try:
            self.config_manager.set_window_position(position.x(), position.y())
            logger.debug(f"Позицію вікна збережено: {position.x()}, {position.y()}")
        except Exception as e:
            logger.error(f"Помилка збереження позиції: {e}")
            
    def show(self):
        """Показує віджет"""
        self.weather_widget.show()
        
    def cleanup(self):
        """Очищення ресурсів"""
        try:
            self.update_timer.stop()
            self.weather_parser.cleanup_temp_files()
            logger.info("Очищення завершено")
        except Exception as e:
            logger.error(f"Помилка очищення: {e}")

class WeatherUpdateWorker(QtCore.QThread):
    """Робочий потік для оновлення погоди"""
    
    data_ready = QtCore.Signal(WeatherData)
    error_occurred = QtCore.Signal(str)
    
    def __init__(self, parser: WeatherParser, url: str):
        super().__init__()
        self.parser = parser
        self.url = url
        
    def run(self):
        """Виконання в окремому потоці"""
        try:
            weather_data = self.parser.fetch_weather_data(self.url)
            self.data_ready.emit(weather_data)
        except Exception as e:
            self.error_occurred.emit(str(e))

def setup_first_run():
    """Налаштування при першому запуску"""
    config_manager = ConfigManager()
    
    # Якщо це перший запуск
    if not config_manager.get_weather_url():
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication(sys.argv)
            
        dialog = SettingsDialog()
        dialog.load_default_settings()
        
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            settings = dialog.get_settings()
            config_manager.set_weather_url(settings['weather_url'])
            config_manager.set_update_interval(settings['update_interval'])
            config_manager.set('auto_update', settings['auto_update'])
            
            if not settings['auto_position']:
                config_manager.set_window_position(settings['x_position'], settings['y_position'])
                
            logger.info("Початкові налаштування збережено")
        else:
            logger.info("Використовуються налаштування за замовчуванням")

def main():
    """Головна функція"""
    try:
        # Створюємо додаток
        app = QtWidgets.QApplication(sys.argv)
        
        # Налаштування додатка
        app.setApplicationName("PogodaPC")
        app.setApplicationVersion("3.8.0")
        app.setOrganizationName("Wendors")
        
        # Перевіряємо перший запуск
        setup_first_run()
        
        # Створюємо головний об'єкт програми
        weather_app = WeatherApp()
        weather_app.show()
        
        # Налаштування виходу
        def cleanup_on_exit():
            weather_app.cleanup()
            
        app.aboutToQuit.connect(cleanup_on_exit)
        
        logger.info("PogodaPC запущено")
        
        # Запускаємо event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Критична помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()