#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки объединенных файлов разделов от дублирующих заголовков.
Удаляет повторяющиеся номера страниц и названия глав после заголовков страниц.

Использование:
    python clean_section_files.py [путь_к_папке_pages]
    
Пример:
    python clean_section_files.py ../pages
"""

import os
import sys
import re
from pathlib import Path


def clean_section_content(content):
    """
    Очищает содержимое файла от дублирующих заголовков.
    
    Args:
        content (str): Исходное содержимое файла
    
    Returns:
        tuple: (очищенное_содержимое, количество_удаленных_строк)
    """
    
    lines = content.split('\n')
    cleaned_lines = []
    removed_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Проверяем, является ли текущая строка заголовком страницы
        if re.match(r'^## Страница \d+$', line):
            cleaned_lines.append(lines[i])  # Добавляем заголовок страницы
            i += 1
            
            # Пропускаем пустые строки после заголовка
            while i < len(lines) and lines[i].strip() == '':
                cleaned_lines.append(lines[i])
                i += 1
            
            # Проверяем следующие строки на наличие дублирующих данных
            if i < len(lines):
                next_line = lines[i].strip()
                
                # Проверяем, является ли следующая строка только номером страницы
                if re.match(r'^\d+$', next_line):
                    # Пропускаем строку с номером страницы
                    removed_count += 1
                    i += 1
                    
                    # Пропускаем пустые строки
                    while i < len(lines) and lines[i].strip() == '':
                        i += 1
                    
                    # Проверяем, есть ли название главы
                    if i < len(lines):
                        chapter_line = lines[i].strip()
                        
                        # Проверяем различные форматы названий глав
                        chapter_patterns = [
                            r'^CHapter .+',  # CHapter One: A World of Darkness
                            r'^Chapter .+',  # Chapter One: A World of Darkness
                            r'^CHAPTER .+',  # CHAPTER ONE: A WORLD OF DARKNESS
                            r'^Appendix .+', # Appendix Gallain
                            r'^APPENDIX .+', # APPENDIX GALLAIN
                            r'^Introduction$', # Introduction
                            r'^INTRODUCTION$', # INTRODUCTION
                            r'^Contents$',   # Contents
                            r'^CONTENTS$',   # CONTENTS
                            r'^Prelude.+',   # Prelude: Both Sides of the Coin
                            r'^PRELUDE.+',   # PRELUDE: BOTH SIDES OF THE COIN
                            r'^Credits$',    # Credits
                            r'^CREDITS$',    # CREDITS
                            r'^Dedication$', # Dedication
                            r'^DEDICATION$', # DEDICATION
                        ]
                        
                        is_chapter_title = any(re.match(pattern, chapter_line) for pattern in chapter_patterns)
                        
                        if is_chapter_title:
                            # Пропускаем название главы
                            removed_count += 1
                            i += 1
                        else:
                            # Если это не название главы, добавляем строку
                            cleaned_lines.append(lines[i])
                            i += 1
                    else:
                        # Больше строк нет
                        break
                else:
                    # Следующая строка не является номером страницы
                    cleaned_lines.append(lines[i])
                    i += 1
            else:
                # Больше строк нет
                break
        else:
            # Обычная строка, добавляем как есть
            cleaned_lines.append(lines[i])
            i += 1
    
    return '\n'.join(cleaned_lines), removed_count


def clean_section_file(file_path):
    """
    Очищает один файл раздела.
    
    Args:
        file_path (Path): Путь к файлу
    
    Returns:
        dict: Результат обработки
    """
    
    try:
        # Читаем исходный файл
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Очищаем содержимое
        cleaned_content, removed_count = clean_section_content(original_content)
        
        # Сохраняем очищенный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        # Подсчитываем изменения
        original_lines = len(original_content.split('\n'))
        cleaned_lines = len(cleaned_content.split('\n'))
        
        return {
            'success': True,
            'removed_lines': removed_count,
            'original_lines': original_lines,
            'cleaned_lines': cleaned_lines,
            'file_size_before': len(original_content),
            'file_size_after': len(cleaned_content)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'removed_lines': 0,
            'original_lines': 0,
            'cleaned_lines': 0,
            'file_size_before': 0,
            'file_size_after': 0
        }


def clean_all_section_files(pages_dir):
    """
    Очищает все файлы разделов в директории.
    
    Args:
        pages_dir (str): Путь к директории с разделами
    
    Returns:
        dict: Общая статистика
    """
    
    pages_path = Path(pages_dir)
    
    if not pages_path.exists():
        print(f"❌ Ошибка: папка {pages_dir} не найдена!")
        return None
    
    # Находим все файлы разделов (файлы .md в корне папок разделов)
    section_files = []
    
    for section_folder in pages_path.iterdir():
        if section_folder.is_dir() and re.match(r'^\d+_', section_folder.name):
            # Ищем файл с названием раздела
            section_file = section_folder / f"{section_folder.name}.md"
            if section_file.exists():
                section_files.append(section_file)
    
    if not section_files:
        print(f"❌ В папке {pages_dir} не найдено файлов разделов!")
        return None
    
    section_files.sort(key=lambda x: x.parent.name)
    
    print(f"📚 Найдено файлов разделов: {len(section_files)}")
    print(f"🧹 Начинаем очистку от дублирующих заголовков...\n")
    
    stats = {
        'total_files': len(section_files),
        'processed_files': 0,
        'total_removed_lines': 0,
        'total_size_saved': 0,
        'errors': 0,
        'files_changed': 0
    }
    
    for section_file in section_files:
        section_name = section_file.parent.name
        print(f"🧹 Очищаем: {section_name}")
        
        result = clean_section_file(section_file)
        
        if result['success']:
            stats['processed_files'] += 1
            stats['total_removed_lines'] += result['removed_lines']
            size_saved = result['file_size_before'] - result['file_size_after']
            stats['total_size_saved'] += size_saved
            
            if result['removed_lines'] > 0:
                stats['files_changed'] += 1
                print(f"   ✅ Удалено строк: {result['removed_lines']}")
                print(f"   📊 Строк: {result['original_lines']} → {result['cleaned_lines']}")
                print(f"   💾 Размер: {size_saved} байт сохранено")
            else:
                print(f"   ℹ️  Изменений не требуется")
        else:
            stats['errors'] += 1
            print(f"   ❌ Ошибка: {result['error']}")
        
        print()
    
    return stats


def print_final_stats(stats):
    """Выводит финальную статистику."""
    
    if not stats:
        return
    
    print("🎉" + "="*60)
    print("✨ ОЧИСТКА ФАЙЛОВ ЗАВЕРШЕНА!")
    print("🎉" + "="*60)
    print(f"📊 Общая статистика:")
    print(f"   📁 Всего файлов: {stats['total_files']}")
    print(f"   ✅ Обработано: {stats['processed_files']}")
    print(f"   📝 Файлов изменено: {stats['files_changed']}")
    print(f"   🗑️  Всего удалено строк: {stats['total_removed_lines']}")
    print(f"   💾 Сэкономлено места: {stats['total_size_saved']:,} байт ({stats['total_size_saved']/1024:.1f} KB)")
    print(f"   ❌ Ошибок: {stats['errors']}")
    
    if stats['files_changed'] > 0:
        print(f"\n💡 Успешно очищено {stats['files_changed']} файлов от дублирующих заголовков!")
        print("   Теперь файлы готовы для удобного редактирования и перевода.")
    else:
        print(f"\n ℹ️ Все файлы уже были чистыми - изменений не потребовалось.")
    
    print("🎉" + "="*60)


def main():
    """Основная функция скрипта."""
    
    # Определяем папку с разделами
    if len(sys.argv) > 1:
        pages_dir = sys.argv[1]
    else:
        # По умолчанию ищем в папке pages относительно корня проекта
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        pages_dir = project_root / "pages"
    
    print("=" * 70)
    print("🧹 ОЧИСТКА ФАЙЛОВ РАЗДЕЛОВ ОТ ДУБЛИРУЮЩИХ ЗАГОЛОВКОВ")
    print("=" * 70)
    print(f"📁 Папка с разделами: {Path(pages_dir).absolute()}")
    print(f"🎯 Цель: Удаление повторяющихся номеров страниц и названий глав")
    print()
    
    stats = clean_all_section_files(pages_dir)
    print_final_stats(stats)
    
    if stats and stats['processed_files'] > 0:
        print(f"\n✨ Обработано {stats['processed_files']} файлов!")
        if stats['files_changed'] > 0:
            print(f"🎉 {stats['files_changed']} файлов было очищено и улучшено!")
    else:
        print("\n❌ Обработка не удалась.")
        sys.exit(1)


if __name__ == "__main__":
    main()
