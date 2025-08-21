#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для копирования пронумерованных markdown файлов из подпапок chapters в папку pages.

Скрипт ищет все файлы вида page_XXX/page_XXX.md в подпапках chapters/ 
и копирует их в папку pages/ в корне проекта.
"""

import os
import shutil
import re
from pathlib import Path


def find_page_files(chapters_dir):
    """
    Находит все файлы page_XXX.md в подпапках chapters.
    
    Args:
        chapters_dir (Path): Путь к папке chapters
        
    Returns:
        list: Список кортежей (source_path, page_number)
    """
    page_files = []
    
    # Паттерн для поиска папок page_XXX
    page_folder_pattern = re.compile(r'^page_(\d+)$')
    
    # Проходим по всем подпапкам в chapters
    for chapter_dir in chapters_dir.iterdir():
        if not chapter_dir.is_dir():
            continue
            
        print(f"Сканирование главы: {chapter_dir.name}")
        
        # Проходим по содержимому каждой главы
        for item in chapter_dir.iterdir():
            if not item.is_dir():
                continue
                
            # Проверяем, соответствует ли имя папки паттерну page_XXX
            match = page_folder_pattern.match(item.name)
            if match:
                page_number = match.group(1)
                
                # Ищем файл page_XXX.md в этой папке
                md_file = item / f"page_{page_number}.md"
                if md_file.exists():
                    page_files.append((md_file, page_number))
                    print(f"  Найден: {md_file.relative_to(chapters_dir)}")
    
    return page_files


def copy_pages(page_files, target_dir):
    """
    Копирует найденные файлы в целевую папку.
    
    Args:
        page_files (list): Список кортежей (source_path, page_number)
        target_dir (Path): Целевая папка для копирования
    """
    # Создаем целевую папку, если она не существует
    target_dir.mkdir(exist_ok=True)
    
    copied_count = 0
    
    for source_path, page_number in page_files:
        target_path = target_dir / f"page_{page_number}.md"
        
        try:
            shutil.copy2(source_path, target_path)
            print(f"Скопирован: {source_path} -> {target_path}")
            copied_count += 1
        except Exception as e:
            print(f"Ошибка при копировании {source_path}: {e}")
    
    return copied_count


def main():
    """Основная функция скрипта."""
    # Определяем пути
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    chapters_dir = project_root / "chapters"
    pages_dir = project_root / "pages"
    
    print(f"Корень проекта: {project_root}")
    print(f"Папка chapters: {chapters_dir}")
    print(f"Целевая папка: {pages_dir}")
    print()
    
    # Проверяем, существует ли папка chapters
    if not chapters_dir.exists():
        print(f"Ошибка: Папка {chapters_dir} не найдена!")
        return 1
    
    # Находим все файлы page_XXX.md
    print("Поиск файлов page_XXX.md...")
    page_files = find_page_files(chapters_dir)
    
    if not page_files:
        print("Файлы page_XXX.md не найдены!")
        return 1
    
    print(f"\nНайдено {len(page_files)} файлов для копирования.")
    
    # Спрашиваем подтверждение
    response = input("\nПродолжить копирование? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'да', 'д']:
        print("Копирование отменено.")
        return 0
    
    # Копируем файлы
    print(f"\nКопирование файлов в {pages_dir}...")
    copied_count = copy_pages(page_files, pages_dir)
    
    print(f"\nГотово! Скопировано {copied_count} файлов.")
    
    # Показываем статистику
    if copied_count > 0:
        print(f"\nВсе файлы сохранены в папке: {pages_dir}")
        print("Файлы переименованы в формат page_XXX.md для удобства.")
    
    return 0


if __name__ == "__main__":
    exit(main())
