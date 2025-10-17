"""
Модуль для парсингу даних про погоду з sinoptik.ua
"""
import re
import logging
import tempfile
import os
import asyncio
import aiohttp
import time
from typing import Optional, Dict, Any, List, Tuple
from urllib.error import URLError, HTTPError

from bs4 import BeautifulSoup
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

class WeatherData:
    """Клас для зберігання даних про погоду"""
    
    def __init__(self):
        self.temperature: Optional[str] = None
        self.description: Optional[str] = None
        self.icon_url: Optional[str] = None
        self.icon_path: Optional[str] = None
        self.last_updated: Optional[float] = None
        self.error_message: Optional[str] = None
        
    def is_valid(self) -> bool:
        """Перевіряє чи дані валідні"""
        return self.temperature is not None or self.icon_path is not None
        
    def __str__(self) -> str:
        return f"WeatherData(temp={self.temperature}, desc={self.description}, icon={self.icon_url})"

class WeatherParser:
    """Клас для парсингу погоди з веб-сайтів"""
    
    # Константи
    REQUEST_TIMEOUT = 10  # секунд
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # секунд
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Селектори для пошуку елементів
    WEATHER_SELECTORS = [
        "qyyKXdcq",  # Оригінальний селектор
        "weather-block",
        "today-weather", 
        "current-weather",
        "main-weather",
        "weather-info"
    ]
    
    TEMPERATURE_SELECTORS = [
        ("p", "R1ENpvZz"),  # Оригінальний селектор
        ("div", "temperature"),
        ("span", "temp"),
        ("div", "temp-value"),
        ("span", "temperature-value"),
        ("div", "current-temp")
    ]
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Ініціалізація парсера
        
        Args:
            temp_dir: Директорія для тимчасових файлів
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.session_files: List[str] = []  # Список файлів для очищення
        
    def fetch_weather_data(self, url: str) -> WeatherData:
        """
        Завантажує дані про погоду з вказаного URL (синхронна версія)
        
        Args:
            url: URL сторінки з погодою
            
        Returns:
            WeatherData: Об'єкт з даними про погоду
        """
        # Запускаємо асинхронну версію в event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self.fetch_weather_data_async(url))
        
    async def fetch_weather_data_async(self, url: str) -> WeatherData:
        """
        Асинхронно завантажує дані про погоду з вказаного URL
        
        Args:
            url: URL сторінки з погодою
            
        Returns:
            WeatherData: Об'єкт з даними про погоду
        """
        weather_data = WeatherData()
        
        try:
            logger.info(f"Завантаження даних з URL: {url}")
            html_content = await self._fetch_html_with_retry_async(url)
            
            if not html_content:
                weather_data.error_message = "Не вдалося завантажити HTML"
                return weather_data
                
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Парсимо температуру
            weather_data.temperature = self._parse_temperature(soup)
            
            # Парсимо іконку
            weather_data.icon_url = self._parse_weather_icon(soup)
            
            # Завантажуємо та обробляємо іконку
            if weather_data.icon_url:
                weather_data.icon_path = await self._download_and_process_icon_async(weather_data.icon_url)
                
            weather_data.last_updated = time.time()
            
            logger.info(f"Дані успішно отримано: {weather_data}")
            
        except Exception as e:
            logger.error(f"Помилка при отриманні даних про погоду: {e}")
            weather_data.error_message = str(e)
            
        return weather_data
        
    async def _fetch_html_with_retry_async(self, url: str) -> Optional[str]:
        """
        Асинхронно завантажує HTML з повторними спробами
        
        Args:
            url: URL для завантаження
            
        Returns:
            str: HTML контент або None при помилці
        """
        headers = {'User-Agent': self.USER_AGENT}
        timeout = aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Асинхронна спроба {attempt + 1} завантаження {url}")
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            return content
                        else:
                            logger.warning(f"HTTP статус {response.status} для {url}")
                            
            except Exception as e:
                logger.warning(f"Асинхронна спроба {attempt + 1} невдала: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Всі {self.MAX_RETRIES} асинхронних спроб завантаження невдалі")
                    
        return None
        """
        Завантажує HTML з повторними спробами
        
        Args:
            url: URL для завантаження
            
        Returns:
            str: HTML контент або None при помилці
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Спроба {attempt + 1} завантаження {url}")
                
                request = Request(url, headers={'User-Agent': self.USER_AGENT})
                
                with urlopen(request, timeout=self.REQUEST_TIMEOUT) as response:
                    return response.read().decode('utf-8', errors='replace')
                    
            except (URLError, HTTPError) as e:
                logger.warning(f"Спроба {attempt + 1} невдала: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Всі {self.MAX_RETRIES} спроб завантаження невдалі")
                    
        return None
        
    def _parse_temperature(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Парсить температуру з HTML
        
        Args:
            soup: BeautifulSoup об'єкт
            
        Returns:
            str: Температура або None
        """
        try:
            # Спробуємо знайти за селекторами
            for tag, class_name in self.TEMPERATURE_SELECTORS:
                element = soup.find(tag, class_name)
                if element:
                    text = element.get_text().strip()
                    if text and any(char.isdigit() for char in text):
                        logger.debug(f"Температура знайдена за селектором {tag}.{class_name}: {text}")
                        return text
                        
            # Якщо не знайдено, використовуємо регулярні вирази
            temp_pattern = r'[-+]?\d+\s*[°С℃C]'
            html_text = str(soup)
            matches = re.findall(temp_pattern, html_text)
            
            if matches:
                temperature = matches[0]
                logger.debug(f"Температура знайдена за регулярним виразом: {temperature}")
                return temperature
                
            logger.warning("Температуру не знайдено")
            return None
            
        except Exception as e:
            logger.error(f"Помилка парсингу температури: {e}")
            return None
            
    def _parse_weather_icon(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Парсить URL іконки погоди
        
        Args:
            soup: BeautifulSoup об'єкт
            
        Returns:
            str: URL іконки або None
        """
        try:
            # Спробуємо знайти блок з погодою
            weather_block = None
            for selector in self.WEATHER_SELECTORS:
                weather_block = soup.find("div", selector)
                if weather_block:
                    logger.debug(f"Знайдено блок погоди з селектором: {selector}")
                    break
                    
            # Якщо не знайдено, шукаємо по всій сторінці
            if not weather_block:
                logger.debug("Специфічний блок не знайдено, пошук по всій сторінці")
                weather_block = soup
                
            # Шукаємо зображення
            images = weather_block.find_all("img")
            logger.debug(f"Знайдено {len(images)} зображень")
            
            for img in images:
                # Отримуємо src атрибут
                src = img.get('src')
                if not src:
                    continue
                    
                # Перевіряємо чи це іконка погоди
                if self._is_weather_icon(src, str(img)):
                    # Конвертуємо у повний URL
                    if src.startswith('http'):
                        icon_url = src
                    elif src.startswith('/'):
                        icon_url = "https://sinoptik.ua" + src
                    else:
                        icon_url = "https://sinoptik.ua/" + src
                        
                    logger.debug(f"Знайдена іконка погоди: {icon_url}")
                    return icon_url
                    
            logger.warning("Іконку погоди не знайдено")
            return None
            
        except Exception as e:
            logger.error(f"Помилка парсингу іконки: {e}")
            return None
            
    def _is_weather_icon(self, src: str, img_html: str) -> bool:
        """
        Перевіряє чи є зображення іконкою погоди
        
        Args:
            src: URL зображення
            img_html: HTML код img тегу
            
        Returns:
            bool: True якщо це іконка погоди
        """
        src_lower = src.lower()
        html_lower = img_html.lower()
        
        # Перевіряємо розширення файлу
        if not any(ext in src_lower for ext in ['.png', '.jpg', '.jpeg', '.svg']):
            return False
            
        # Перевіряємо ключові слова
        weather_keywords = [
            'weather', 'icon', 'pogoda', '/p/', 'icons/',
            'sunny', 'cloudy', 'rain', 'snow', 'clear',
            'хмарно', 'сонце', 'дощ', 'сніг'
        ]
        
        return any(keyword in src_lower or keyword in html_lower 
                  for keyword in weather_keywords)
                  
    async def _download_and_process_icon_async(self, icon_url: str) -> Optional[str]:
        """
        Асинхронно завантажує та обробляє іконку погоди
        
        Args:
            icon_url: URL іконки
            
        Returns:
            str: Шлях до обробленої іконки або None
        """
        try:
            logger.debug(f"Асинхронне завантаження іконки з: {icon_url}")
            
            headers = {'User-Agent': self.USER_AGENT}
            timeout = aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(icon_url, headers=headers) as response:
                    if response.status == 200:
                        image_data = await response.read()
                    else:
                        logger.error(f"Помилка завантаження іконки: HTTP {response.status}")
                        return None
                        
            # Зберігаємо у тимчасовий файл
            temp_image_path = os.path.join(self.temp_dir, "weather_icon.jpg")
            with open(temp_image_path, "wb") as f:
                f.write(image_data)
                
            self.session_files.append(temp_image_path)
            
            # Обробляємо зображення
            processed_path = self._process_image(temp_image_path)
            
            logger.debug(f"Іконка асинхронно оброблена: {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.error(f"Помилка асинхронного завантаження іконки: {e}")
            return None
        """
        Завантажує та обробляє іконку погоди
        
        Args:
            icon_url: URL іконки
            
        Returns:
            str: Шлях до обробленої іконки або None
        """
        try:
            logger.debug(f"Завантаження іконки з: {icon_url}")
            
            # Завантажуємо зображення
            request = Request(icon_url, headers={'User-Agent': self.USER_AGENT})
            
            with urlopen(request, timeout=self.REQUEST_TIMEOUT) as response:
                image_data = response.read()
                
            # Зберігаємо у тимчасовий файл
            temp_image_path = os.path.join(self.temp_dir, "weather_icon.jpg")
            with open(temp_image_path, "wb") as f:
                f.write(image_data)
                
            self.session_files.append(temp_image_path)
            
            # Обробляємо зображення
            processed_path = self._process_image(temp_image_path)
            
            logger.debug(f"Іконка оброблена: {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.error(f"Помилка завантаження іконки: {e}")
            return None
            
    def _process_image(self, image_path: str) -> Optional[str]:
        """
        Обробляє зображення (прибирає білий фон, додає прозорість)
        
        Args:
            image_path: Шлях до зображення
            
        Returns:
            str: Шлях до обробленого зображення
        """
        try:
            # Відкриваємо зображення
            image = Image.open(image_path)
            
            # Конвертуємо в PNG для підтримки прозорості
            png_path = os.path.join(self.temp_dir, "weather_icon.png")
            image.save(png_path, "PNG")
            self.session_files.append(png_path)
            
            # Завантажуємо як RGBA для обробки прозорості
            image = Image.open(png_path).convert("RGBA")
            pixels = image.load()
            width, height = image.size
            
            # Прибираємо білий фон
            for x in range(width):
                for y in range(height):
                    r, g, b, a = pixels[x, y]
                    # Якщо піксель близький до білого, робимо прозорим
                    if r > 240 and g > 240 and b > 240:
                        pixels[x, y] = (r, g, b, 0)
                        
            # Зберігаємо оброблене зображення
            output_path = os.path.join(self.temp_dir, "weather_icon_processed.png")
            image.save(output_path, "PNG")
            self.session_files.append(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Помилка обробки зображення: {e}")
            return None
            
    def cleanup_temp_files(self) -> None:
        """Очищає тимчасові файли"""
        for file_path in self.session_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Видалено тимчасовий файл: {file_path}")
            except Exception as e:
                logger.warning(f"Не вдалося видалити файл {file_path}: {e}")
                
        self.session_files.clear()
        
    def __del__(self):
        """Деструктор - очищає тимчасові файли"""
        self.cleanup_temp_files()