"""
Модуль для управління конфігурацією PogodaPC
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ConfigManager:
    """Менеджер конфігурації для збереження налаштувань"""
    
    # Константи
    DEFAULT_CONFIG = {
        'weather_url': 'https://sinoptik.ua/pohoda/truskavets',
        'update_interval': 1800,  # 30 хвилин в секундах
        'window_position': {'x': None, 'y': 370},  # None означає автопозиціонування
        'window_size': {'width': 300, 'height': 305},
        'auto_update': True,
        'language': 'uk'
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Ініціалізація конфіг менеджера
        
        Args:
            config_file: Шлях до файлу конфігурації. Якщо None, використовується за замовчуванням
        """
        if config_file:
            self.config_file = config_file
        else:
            self.config_file = os.path.join(
                os.path.expanduser("~"), 
                ".pogodapc_config.json"
            )
        
        self._config = self.DEFAULT_CONFIG.copy()
        self._load_config()
        
    def _load_config(self) -> None:
        """Завантажує конфігурацію з файлу"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                # Оновлюємо конфігурацію, зберігаючи значення за замовчуванням
                self._config.update(loaded_config)
                logger.info(f"Конфігурацію завантажено з {self.config_file}")
            else:
                logger.info("Файл конфігурації не існує, використовуються значення за замовчуванням")
                
        except Exception as e:
            logger.error(f"Помилка завантаження конфігурації: {e}")
            
    def save_config(self) -> bool:
        """
        Зберігає конфігурацію у файл
        
        Returns:
            bool: True якщо успішно збережено
        """
        try:
            # Створюємо директорію якщо не існує
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            logger.info(f"Конфігурацію збережено в {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Помилка збереження конфігурації: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Отримує значення з конфігурації
        
        Args:
            key: Ключ конфігурації
            default: Значення за замовчуванням
            
        Returns:
            Значення конфігурації
        """
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any) -> bool:
        """
        Встановлює значення в конфігурації
        
        Args:
            key: Ключ конфігурації
            value: Значення для встановлення
            
        Returns:
            bool: True якщо успішно встановлено
        """
        try:
            self._config[key] = value
            return self.save_config()
        except Exception as e:
            logger.error(f"Помилка встановлення конфігурації {key}={value}: {e}")
            return False
            
    def get_weather_url(self) -> str:
        """Отримує URL погоди з конфігурації"""
        return self.get('weather_url', self.DEFAULT_CONFIG['weather_url'])
        
    def set_weather_url(self, url: str) -> bool:
        """
        Зберігає URL погоди в конфігурації з валідацією
        
        Args:
            url: URL для збереження
            
        Returns:
            bool: True якщо успішно збережено
        """
        if not self.validate_weather_url(url):
            logger.error(f"Невалідний URL: {url}")
            return False
            
        return self.set('weather_url', url)
        
    def get_update_interval(self) -> int:
        """Отримує інтервал оновлення в секундах"""
        return self.get('update_interval', self.DEFAULT_CONFIG['update_interval'])
        
    def set_update_interval(self, interval: int) -> bool:
        """
        Встановлює інтервал оновлення
        
        Args:
            interval: Інтервал в секундах (мінімум 60)
            
        Returns:
            bool: True якщо успішно встановлено
        """
        if interval < 60:
            logger.error(f"Інтервал оновлення занадто малий: {interval}")
            return False
            
        return self.set('update_interval', interval)
        
    def get_window_position(self) -> Dict[str, Optional[int]]:
        """Отримує позицію вікна"""
        return self.get('window_position', self.DEFAULT_CONFIG['window_position'])
        
    def set_window_position(self, x: Optional[int], y: int) -> bool:
        """
        Встановлює позицію вікна
        
        Args:
            x: X координата (None для автопозиціонування)
            y: Y координата
            
        Returns:
            bool: True якщо успішно встановлено
        """
        return self.set('window_position', {'x': x, 'y': y})
        
    def get_window_size(self) -> Dict[str, int]:
        """Отримує розмір вікна"""
        return self.get('window_size', self.DEFAULT_CONFIG['window_size'])
        
    @staticmethod
    def validate_weather_url(url: str) -> bool:
        """
        Валідує URL погоди
        
        Args:
            url: URL для перевірки
            
        Returns:
            bool: True якщо URL валідний
        """
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                'sinoptik.ua' in parsed.netloc and
                len(url.strip()) > 0
            )
        except Exception:
            return False
            
    def reset_to_defaults(self) -> bool:
        """
        Скидає конфігурацію до значень за замовчуванням
        
        Returns:
            bool: True якщо успішно скинуто
        """
        self._config = self.DEFAULT_CONFIG.copy()
        return self.save_config()
        
    def get_all_config(self) -> Dict[str, Any]:
        """Повертає всю конфігурацію"""
        return self._config.copy()