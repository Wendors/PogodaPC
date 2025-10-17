#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для скидання налаштувань PogodaPC
"""

import os
import sys

def reset_settings():
    """Скидає налаштування PogodaPC"""
    config_file = os.path.join(os.path.expanduser("~"), ".pogodapc_config.json")
    
    if os.path.exists(config_file):
        try:
            os.remove(config_file)
            print("✓ Налаштування успішно скинуто!")
            print("При наступному запуску програми з'явиться вікно налаштувань.")
        except Exception as e:
            print(f"✗ Помилка при скиданні налаштувань: {e}")
    else:
        print("! Файл налаштувань не знайдено. Можливо, налаштування вже скинуто.")

if __name__ == "__main__":
    print("PogodaPC - Скидання налаштувань")
    print("=" * 40)
    
    answer = input("Ви впевнені, що хочете скинути налаштування? (y/N): ")
    if answer.lower() in ['y', 'yes', 'так', 'т']:
        reset_settings()
    else:
        print("Скидання скасовано.")