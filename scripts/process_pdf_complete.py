#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный скрипт для полной обработки PDF файла.
Выполняет все этапы: разделение на страницы, извлечение текста и изображений.

Использование:
    python process_pdf_complete.py <путь_к_pdf_файлу> [--test N]
    
Примеры:
    python process_pdf_complete.py source.pdf              # Полная обработка
    python process_pdf_complete.py source.pdf --test 5     # Тест на 5 страницах
"""

import fitz  # PyMuPDF
import os
import sys
import time
from pathlib import Path
import argparse
from datetime import datetime

# Импортируем функции из других скриптов
sys.path.append(str(Path(__file__).parent))


def format_time(seconds):
    """Форматирует время в читаемом виде."""
    if seconds < 60:
        return f"{seconds:.1f} сек"
    elif seconds < 3600:
        return f"{seconds/60:.1f} мин"
    else:
        return f"{seconds/3600:.1f} час"


def format_size(bytes_size):
    """Форматирует размер файла в читаемом виде."""
    if bytes_size < 1024:
        return f"{bytes_size} байт"
    elif bytes_size < 1024**2:
        return f"{bytes_size/1024:.1f} KB"
    elif bytes_size < 1024**3:
        return f"{bytes_size/1024**2:.1f} MB"
    else:
        return f"{bytes_size/1024**3:.1f} GB"


def split_pdf_pages(pdf_path, output_base_dir, max_pages=None):
    """
    Разделяет PDF файл на отдельные страницы.
    Адаптированная версия из split_pdf_pages.py
    """
    
    if not os.path.exists(pdf_path):
        print(f"❌ Ошибка: файл {pdf_path} не найден!")
        return 0
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        pages_to_process = min(max_pages or total_pages, total_pages)
        
        print(f"📄 Всего страниц в документе: {total_pages}")
        if max_pages:
            print(f"🔬 Будем обрабатывать: {pages_to_process} страниц (тестовый режим)")
        
        output_path = Path(output_base_dir)
        output_path.mkdir(exist_ok=True)
        
        for page_num in range(pages_to_process):
            page_folder = output_path / f"page_{page_num + 1:03d}"
            page_folder.mkdir(exist_ok=True)
            
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            output_pdf_path = page_folder / f"page_{page_num + 1:03d}.pdf"
            new_doc.save(str(output_pdf_path))
            new_doc.close()
            
            if (page_num + 1) % 50 == 0 or page_num + 1 == pages_to_process:
                progress = (page_num + 1) / pages_to_process * 100
                print(f"   📄 Разделено страниц: {page_num + 1}/{pages_to_process} ({progress:.1f}%)")
        
        doc.close()
        return pages_to_process
        
    except Exception as e:
        print(f"❌ Ошибка при разделении файла: {str(e)}")
        return 0


def extract_text_from_pages(pages_dir):
    """
    Извлекает текст из всех страниц.
    Упрощенная версия из extract_text.py
    """
    
    pages_path = Path(pages_dir)
    page_folders = sorted([d for d in pages_path.iterdir() if d.is_dir() and d.name.startswith('page_')])
    
    if not page_folders:
        return {'processed': 0, 'with_text': 0, 'total_chars': 0}
    
    stats = {'processed': 0, 'with_text': 0, 'total_chars': 0}
    
    for i, page_folder in enumerate(page_folders, 1):
        pdf_files = list(page_folder.glob('*.pdf'))
        if not pdf_files:
            continue
        
        try:
            doc = fitz.open(pdf_files[0])
            page = doc.load_page(0)
            text = page.get_text().strip()
            doc.close()
            
            # Создаем простой markdown файл
            markdown_path = page_folder / f"page_{i:03d}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(f"# Страница {i}\n\n")
                if text:
                    f.write(text)
                    stats['with_text'] += 1
                    stats['total_chars'] += len(text)
                else:
                    f.write("*На этой странице нет текста.*\n")
                f.write(f"\n\n---\n*Страница {i}*\n")
            
            stats['processed'] += 1
            
            if i % 50 == 0 or i == len(page_folders):
                progress = i / len(page_folders) * 100
                print(f"   📝 Извлечен текст: {i}/{len(page_folders)} ({progress:.1f}%)")
        
        except Exception as e:
            print(f"❌ Ошибка обработки текста страницы {i}: {str(e)}")
    
    return stats


def extract_images_from_pages(pages_dir):
    """
    Извлекает изображения из всех страниц.
    Упрощенная версия из extract_images.py
    """
    
    pages_path = Path(pages_dir)
    page_folders = sorted([d for d in pages_path.iterdir() if d.is_dir() and d.name.startswith('page_')])
    
    if not page_folders:
        return {'processed': 0, 'with_images': 0, 'total_images': 0, 'total_size': 0}
    
    stats = {'processed': 0, 'with_images': 0, 'total_images': 0, 'total_size': 0}
    
    for i, page_folder in enumerate(page_folders, 1):
        pdf_files = list(page_folder.glob('*.pdf'))
        if not pdf_files:
            continue
        
        try:
            doc = fitz.open(pdf_files[0])
            page = doc.load_page(0)
            image_list = page.get_images()
            
            page_images = 0
            page_size = 0
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_format = base_image["ext"]
                
                image_name = f"page_{i:03d}_img_{img_index + 1:02d}.{image_format}"
                image_path = page_folder / image_name
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                page_images += 1
                page_size += len(image_bytes)
            
            doc.close()
            
            # Создаем простой информационный файл
            if page_images > 0:
                info_path = page_folder / f"page_{i:03d}_images.md"
                with open(info_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Изображения со страницы {i}\n\n")
                    f.write(f"Найдено изображений: {page_images}\n")
                    f.write(f"Общий размер: {format_size(page_size)}\n")
                
                stats['with_images'] += 1
                stats['total_images'] += page_images
                stats['total_size'] += page_size
            
            stats['processed'] += 1
            
            if i % 50 == 0 or i == len(page_folders):
                progress = i / len(page_folders) * 100
                print(f"   🖼️  Извлечены изображения: {i}/{len(page_folders)} ({progress:.1f}%)")
        
        except Exception as e:
            print(f"❌ Ошибка обработки изображений страницы {i}: {str(e)}")
    
    return stats


def main():
    """Основная функция скрипта."""
    
    parser = argparse.ArgumentParser(description='Полная обработка PDF файла')
    parser.add_argument('pdf_file', help='Путь к PDF файлу')
    parser.add_argument('--test', type=int, metavar='N', help='Тестовый режим: обработать только N страниц')
    parser.add_argument('--output', help='Папка для результатов (по умолчанию: pages или pages_test)')
    
    args = parser.parse_args()
    
    # Определяем выходную папку
    if args.output:
        output_dir = args.output
    elif args.test:
        output_dir = "pages_test"
    else:
        output_dir = "pages"
    
    # Путь относительно корня проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_path = project_root / output_dir
    
    print("=" * 70)
    print("🚀 ПОЛНАЯ ОБРАБОТКА PDF ФАЙЛА")
    print("=" * 70)
    print(f"📁 Исходный файл: {args.pdf_file}")
    print(f"📂 Результаты в: {output_path.absolute()}")
    if args.test:
        print(f"🧪 Тестовый режим: {args.test} страниц")
    print(f"⏰ Начало: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_start_time = time.time()
    
    # Этап 1: Разделение на страницы
    print("📄 ЭТАП 1: РАЗДЕЛЕНИЕ НА СТРАНИЦЫ")
    print("-" * 40)
    step_start = time.time()
    
    pages_processed = split_pdf_pages(args.pdf_file, output_path, args.test)
    
    if pages_processed == 0:
        print("❌ Ошибка разделения страниц. Остановка.")
        sys.exit(1)
    
    step_time = time.time() - step_start
    print(f"✅ Разделено {pages_processed} страниц за {format_time(step_time)}")
    print()
    
    # Этап 2: Извлечение текста
    print("📝 ЭТАП 2: ИЗВЛЕЧЕНИЕ ТЕКСТА")
    print("-" * 40)
    step_start = time.time()
    
    text_stats = extract_text_from_pages(output_path)
    
    step_time = time.time() - step_start
    print(f"✅ Обработано {text_stats['processed']} страниц за {format_time(step_time)}")
    print(f"   📝 Страниц с текстом: {text_stats['with_text']}")
    print(f"   🔤 Всего символов: {text_stats['total_chars']:,}")
    print()
    
    # Этап 3: Извлечение изображений
    print("🖼️  ЭТАП 3: ИЗВЛЕЧЕНИЕ ИЗОБРАЖЕНИЙ")
    print("-" * 40)
    step_start = time.time()
    
    image_stats = extract_images_from_pages(output_path)
    
    step_time = time.time() - step_start
    print(f"✅ Обработано {image_stats['processed']} страниц за {format_time(step_time)}")
    print(f"   🖼️  Страниц с изображениями: {image_stats['with_images']}")
    print(f"   📊 Всего изображений: {image_stats['total_images']}")
    print(f"   💾 Общий размер: {format_size(image_stats['total_size'])}")
    print()
    
    # Финальная статистика
    total_time = time.time() - total_start_time
    
    print("🎉" + "="*60)
    print("✨ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
    print("🎉" + "="*60)
    print(f"📊 Итоговая статистика:")
    print(f"   📄 Обработано страниц: {pages_processed}")
    print(f"   📝 Страниц с текстом: {text_stats['with_text']}")
    print(f"   🖼️  Страниц с изображениями: {image_stats['with_images']}")
    print(f"   📊 Всего изображений: {image_stats['total_images']}")
    print(f"   💾 Размер изображений: {format_size(image_stats['total_size'])}")
    print()
    print(f"⏰ Общее время обработки: {format_time(total_time)}")
    print(f"📁 Результаты сохранены в: {output_path.absolute()}")
    print()
    print("💡 Структура каждой папки со страницей:")
    print("   📄 page_XXX.pdf     - PDF страница")
    print("   📝 page_XXX.md      - Текст в Markdown")
    print("   🖼️  page_XXX_img_XX  - Изображения")
    print("   📋 page_XXX_images.md - Информация об изображениях")
    print("🎉" + "="*60)


if __name__ == "__main__":
    main()
