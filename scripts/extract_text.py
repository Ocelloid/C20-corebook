#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для извлечения текста из страниц PDF и сохранения в формате Markdown.
Работает с уже разделенными страницами в папках.

Использование:
    python extract_text.py [путь_к_папке_со_страницами]
    
Пример:
    python extract_text.py ../pages
"""

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path
import re


def clean_text(text):
    """
    Очищает и форматирует извлеченный текст для Markdown.
    
    Args:
        text (str): Исходный текст
    
    Returns:
        str: Очищенный и отформатированный текст
    """
    if not text:
        return ""
    
    # Убираем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Разделяем на абзацы по двойным переносам строк
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Очищаем каждый абзац
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            # Убираем лишние пробелы
            paragraph = re.sub(r'\s+', ' ', paragraph)
            cleaned_paragraphs.append(paragraph)
    
    return '\n\n'.join(cleaned_paragraphs)


def extract_text_from_page(pdf_path):
    """
    Извлекает текст из одной страницы PDF.
    
    Args:
        pdf_path (str): Путь к PDF файлу страницы
    
    Returns:
        dict: Информация о странице с текстом
    """
    
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # У нас всегда одна страница
        
        # Извлекаем текст
        raw_text = page.get_text()
        cleaned_text = clean_text(raw_text)
        
        # Получаем дополнительную информацию
        text_dict = page.get_text("dict")
        
        # Подсчитываем статистику
        char_count = len(cleaned_text)
        word_count = len(cleaned_text.split()) if cleaned_text else 0
        line_count = len(cleaned_text.split('\n')) if cleaned_text else 0
        
        doc.close()
        
        return {
            'text': cleaned_text,
            'char_count': char_count,
            'word_count': word_count,
            'line_count': line_count,
            'has_text': bool(cleaned_text.strip())
        }
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении текста из {pdf_path}: {str(e)}")
        return {
            'text': '',
            'char_count': 0,
            'word_count': 0,
            'line_count': 0,
            'has_text': False,
            'error': str(e)
        }


def create_markdown_file(page_info, output_path, page_number):
    """
    Создает Markdown файл со страницей.
    
    Args:
        page_info (dict): Информация о странице
        output_path (Path): Путь для сохранения
        page_number (int): Номер страницы
    """
    
    # Создаем заголовок
    markdown_content = f"# Страница {page_number}\n\n"
    
    # Добавляем метаинформацию
    markdown_content += f"<!-- \n"
    markdown_content += f"Страница: {page_number}\n"
    markdown_content += f"Символов: {page_info['char_count']}\n"
    markdown_content += f"Слов: {page_info['word_count']}\n"
    markdown_content += f"Строк: {page_info['line_count']}\n"
    markdown_content += f"Есть текст: {'Да' if page_info['has_text'] else 'Нет'}\n"
    markdown_content += f"-->\n\n"
    
    # Добавляем текст
    if page_info['has_text']:
        markdown_content += page_info['text']
    else:
        if 'error' in page_info:
            markdown_content += f"*Ошибка извлечения текста: {page_info['error']}*\n"
        else:
            markdown_content += "*На этой странице нет текста или текст не удалось извлечь.*\n"
    
    # Добавляем разделитель в конце
    markdown_content += "\n\n---\n"
    markdown_content += f"*Извлечено из страницы {page_number}*\n"
    
    # Сохраняем файл
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении {output_path}: {str(e)}")
        return False


def extract_text_from_pages(pages_dir):
    """
    Извлекает текст из всех страниц в директории.
    
    Args:
        pages_dir (str): Путь к директории со страницами
    
    Returns:
        dict: Статистика обработки
    """
    
    pages_path = Path(pages_dir)
    
    if not pages_path.exists():
        print(f"❌ Ошибка: папка {pages_dir} не найдена!")
        return None
    
    # Находим все папки со страницами
    page_folders = sorted([d for d in pages_path.iterdir() if d.is_dir() and d.name.startswith('page_')])
    
    if not page_folders:
        print(f"❌ В папке {pages_dir} не найдено папок со страницами!")
        return None
    
    print(f"📁 Найдено папок со страницами: {len(page_folders)}")
    print(f"🚀 Начинаем извлечение текста...\n")
    
    stats = {
        'total_pages': len(page_folders),
        'processed_pages': 0,
        'pages_with_text': 0,
        'pages_without_text': 0,
        'total_characters': 0,
        'total_words': 0,
        'errors': 0
    }
    
    for i, page_folder in enumerate(page_folders, 1):
        # Находим PDF файл в папке
        pdf_files = list(page_folder.glob('*.pdf'))
        
        if not pdf_files:
            print(f"⚠️  Страница {i:03d}: PDF файл не найден в {page_folder}")
            stats['errors'] += 1
            continue
        
        pdf_path = pdf_files[0]  # Берем первый PDF файл
        
        # Извлекаем текст
        page_info = extract_text_from_page(pdf_path)
        
        # Создаем Markdown файл
        markdown_path = page_folder / f"page_{i:03d}.md"
        success = create_markdown_file(page_info, markdown_path, i)
        
        if success:
            stats['processed_pages'] += 1
            
            if page_info['has_text']:
                stats['pages_with_text'] += 1
                stats['total_characters'] += page_info['char_count']
                stats['total_words'] += page_info['word_count']
            else:
                stats['pages_without_text'] += 1
            
            # Показываем прогресс
            progress = i / len(page_folders) * 100
            status = "📝" if page_info['has_text'] else "📄"
            print(f"{status} Страница {i:03d}/{len(page_folders):03d} → {markdown_path.name}")
            print(f"   📊 Символов: {page_info['char_count']}, слов: {page_info['word_count']}")
            print(f"   📈 Прогресс: {progress:.1f}%")
        else:
            stats['errors'] += 1
            print(f"❌ Ошибка обработки страницы {i:03d}")
        
        print()
    
    return stats


def print_final_stats(stats):
    """Выводит финальную статистику."""
    
    if not stats:
        return
    
    print("🎉" + "="*50)
    print("✨ ИЗВЛЕЧЕНИЕ ТЕКСТА ЗАВЕРШЕНО!")
    print("🎉" + "="*50)
    print(f"📊 Общая статистика:")
    print(f"   📄 Всего страниц: {stats['total_pages']}")
    print(f"   ✅ Обработано: {stats['processed_pages']}")
    print(f"   📝 Со текстом: {stats['pages_with_text']}")
    print(f"   📄 Без текста: {stats['pages_without_text']}")
    print(f"   ❌ Ошибок: {stats['errors']}")
    print()
    print(f"📈 Статистика текста:")
    print(f"   🔤 Всего символов: {stats['total_characters']:,}")
    print(f"   📝 Всего слов: {stats['total_words']:,}")
    print(f"   📊 Среднее слов на страницу: {stats['total_words'] // max(stats['pages_with_text'], 1):,}")
    print("🎉" + "="*50)


def main():
    """Основная функция скрипта."""
    
    # Определяем папку со страницами
    if len(sys.argv) > 1:
        pages_dir = sys.argv[1]
    else:
        # По умолчанию ищем в папке pages относительно корня проекта
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        pages_dir = project_root / "pages"
    
    print("=" * 60)
    print("📝 ИЗВЛЕЧЕНИЕ ТЕКСТА ИЗ СТРАНИЦ PDF")
    print("=" * 60)
    print(f"📁 Папка со страницами: {Path(pages_dir).absolute()}")
    print()
    
    stats = extract_text_from_pages(pages_dir)
    print_final_stats(stats)
    
    if stats and stats['processed_pages'] > 0:
        print(f"\n💡 Markdown файлы сохранены в соответствующих папках страниц")
        print(f"📁 Проверьте содержимое папки: {Path(pages_dir).absolute()}")
    else:
        print("\n❌ Обработка не удалась.")
        sys.exit(1)


if __name__ == "__main__":
    main()
