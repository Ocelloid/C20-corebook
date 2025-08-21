#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для извлечения изображений из страниц PDF.
Работает с уже разделенными страницами в папках.

Использование:
    python extract_images.py [путь_к_папке_со_страницами]
    
Пример:
    python extract_images.py ../pages
"""

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path
from PIL import Image
import io


def get_image_extension(image_format):
    """
    Определяет расширение файла по формату изображения.
    
    Args:
        image_format (str): Формат изображения из PyMuPDF
    
    Returns:
        str: Расширение файла
    """
    
    format_map = {
        'jpeg': '.jpg',
        'jpg': '.jpg', 
        'png': '.png',
        'bmp': '.bmp',
        'gif': '.gif',
        'tiff': '.tiff',
        'tif': '.tiff'
    }
    
    return format_map.get(image_format.lower(), '.png')


def extract_images_from_page(pdf_path, output_folder, page_number):
    """
    Извлекает изображения из одной страницы PDF.
    
    Args:
        pdf_path (str): Путь к PDF файлу страницы
        output_folder (Path): Папка для сохранения изображений
        page_number (int): Номер страницы
    
    Returns:
        dict: Информация об извлеченных изображениях
    """
    
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # У нас всегда одна страница
        
        # Получаем список изображений на странице
        image_list = page.get_images()
        
        extracted_images = []
        
        for img_index, img in enumerate(image_list):
            # Получаем данные изображения
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            image_bytes = base_image["image"]
            image_format = base_image["ext"]
            
            # Определяем имя файла
            image_name = f"page_{page_number:03d}_img_{img_index + 1:02d}{get_image_extension(image_format)}"
            image_path = output_folder / image_name
            
            # Сохраняем изображение
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            # Получаем размеры изображения
            try:
                with Image.open(io.BytesIO(image_bytes)) as pil_img:
                    width, height = pil_img.size
                    file_size = len(image_bytes)
                    
                    extracted_images.append({
                        'filename': image_name,
                        'path': image_path,
                        'format': image_format,
                        'width': width,
                        'height': height,
                        'file_size': file_size
                    })
            except Exception as e:
                print(f"⚠️  Не удалось получить размеры изображения {image_name}: {str(e)}")
                extracted_images.append({
                    'filename': image_name,
                    'path': image_path,
                    'format': image_format,
                    'width': 0,
                    'height': 0,
                    'file_size': len(image_bytes),
                    'error': str(e)
                })
        
        doc.close()
        
        return {
            'success': True,
            'image_count': len(extracted_images),
            'images': extracted_images,
            'total_size': sum(img['file_size'] for img in extracted_images)
        }
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении изображений из {pdf_path}: {str(e)}")
        return {
            'success': False,
            'image_count': 0,
            'images': [],
            'total_size': 0,
            'error': str(e)
        }


def create_images_info_file(page_info, output_folder, page_number):
    """
    Создает информационный файл об изображениях страницы.
    
    Args:
        page_info (dict): Информация об изображениях страницы
        output_folder (Path): Папка для сохранения
        page_number (int): Номер страницы
    """
    
    info_path = output_folder / f"page_{page_number:03d}_images.md"
    
    content = f"# Изображения со страницы {page_number}\n\n"
    
    if page_info['success'] and page_info['image_count'] > 0:
        content += f"**Найдено изображений:** {page_info['image_count']}\n"
        content += f"**Общий размер:** {page_info['total_size']:,} байт ({page_info['total_size']/1024:.1f} KB)\n\n"
        
        content += "## Список изображений\n\n"
        
        for i, img in enumerate(page_info['images'], 1):
            content += f"### {i}. {img['filename']}\n\n"
            content += f"- **Формат:** {img['format'].upper()}\n"
            content += f"- **Размеры:** {img['width']} × {img['height']} пикселей\n"
            content += f"- **Размер файла:** {img['file_size']:,} байт ({img['file_size']/1024:.1f} KB)\n"
            
            if 'error' in img:
                content += f"- **Предупреждение:** {img['error']}\n"
            
            content += f"- **Файл:** `{img['filename']}`\n\n"
            
            # Добавляем ссылку на изображение в Markdown
            content += f"![{img['filename']}]({img['filename']})\n\n"
    
    elif page_info['success']:
        content += "На этой странице нет изображений.\n\n"
    
    else:
        content += f"**Ошибка извлечения изображений:** {page_info.get('error', 'Неизвестная ошибка')}\n\n"
    
    content += "---\n"
    content += f"*Изображения извлечены со страницы {page_number}*\n"
    
    # Сохраняем файл
    try:
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении {info_path}: {str(e)}")
        return False


def extract_images_from_pages(pages_dir):
    """
    Извлекает изображения из всех страниц в директории.
    
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
    print(f"🚀 Начинаем извлечение изображений...\n")
    
    stats = {
        'total_pages': len(page_folders),
        'processed_pages': 0,
        'pages_with_images': 0,
        'pages_without_images': 0,
        'total_images': 0,
        'total_size': 0,
        'errors': 0,
        'formats': {}
    }
    
    for i, page_folder in enumerate(page_folders, 1):
        # Находим PDF файл в папке
        pdf_files = list(page_folder.glob('*.pdf'))
        
        if not pdf_files:
            print(f"⚠️  Страница {i:03d}: PDF файл не найден в {page_folder}")
            stats['errors'] += 1
            continue
        
        pdf_path = pdf_files[0]  # Берем первый PDF файл
        
        # Извлекаем изображения
        page_info = extract_images_from_page(pdf_path, page_folder, i)
        
        # Создаем информационный файл
        info_created = create_images_info_file(page_info, page_folder, i)
        
        if page_info['success'] and info_created:
            stats['processed_pages'] += 1
            
            if page_info['image_count'] > 0:
                stats['pages_with_images'] += 1
                stats['total_images'] += page_info['image_count']
                stats['total_size'] += page_info['total_size']
                
                # Подсчитываем форматы
                for img in page_info['images']:
                    fmt = img['format'].upper()
                    stats['formats'][fmt] = stats['formats'].get(fmt, 0) + 1
            else:
                stats['pages_without_images'] += 1
            
            # Показываем прогресс
            progress = i / len(page_folders) * 100
            status = "🖼️ " if page_info['image_count'] > 0 else "📄"
            print(f"{status} Страница {i:03d}/{len(page_folders):03d} → {page_info['image_count']} изображений")
            
            if page_info['image_count'] > 0:
                size_kb = page_info['total_size'] / 1024
                print(f"   📊 Размер: {size_kb:.1f} KB")
                formats = set(img['format'].upper() for img in page_info['images'])
                print(f"   🎨 Форматы: {', '.join(formats)}")
            
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
    print("✨ ИЗВЛЕЧЕНИЕ ИЗОБРАЖЕНИЙ ЗАВЕРШЕНО!")
    print("🎉" + "="*50)
    print(f"📊 Общая статистика:")
    print(f"   📄 Всего страниц: {stats['total_pages']}")
    print(f"   ✅ Обработано: {stats['processed_pages']}")
    print(f"   🖼️  Со изображениями: {stats['pages_with_images']}")
    print(f"   📄 Без изображений: {stats['pages_without_images']}")
    print(f"   ❌ Ошибок: {stats['errors']}")
    print()
    print(f"📈 Статистика изображений:")
    print(f"   🖼️  Всего изображений: {stats['total_images']:,}")
    print(f"   💾 Общий размер: {stats['total_size']:,} байт ({stats['total_size']/1024/1024:.1f} MB)")
    print(f"   📊 Среднее на страницу: {stats['total_images'] // max(stats['pages_with_images'], 1):.1f}")
    
    if stats['formats']:
        print(f"\n🎨 Форматы изображений:")
        for fmt, count in sorted(stats['formats'].items()):
            print(f"   {fmt}: {count} изображений")
    
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
    print("🖼️  ИЗВЛЕЧЕНИЕ ИЗОБРАЖЕНИЙ ИЗ СТРАНИЦ PDF")
    print("=" * 60)
    print(f"📁 Папка со страницами: {Path(pages_dir).absolute()}")
    print()
    
    stats = extract_images_from_pages(pages_dir)
    print_final_stats(stats)
    
    if stats and stats['processed_pages'] > 0:
        print(f"\n💡 Изображения и информационные файлы сохранены в соответствующих папках страниц")
        print(f"📁 Проверьте содержимое папки: {Path(pages_dir).absolute()}")
    else:
        print("\n❌ Обработка не удалась.")
        sys.exit(1)


if __name__ == "__main__":
    main()
