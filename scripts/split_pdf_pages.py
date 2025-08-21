#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для разделения PDF-файла на отдельные страницы.
Каждая страница сохраняется в отдельной папке в формате PDF.

Использование:
    python split_pdf_pages.py <путь_к_pdf_файлу>
    
Пример:
    python split_pdf_pages.py ../source.pdf
"""

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path


def split_pdf_to_pages(pdf_path, output_base_dir=None):
    """
    Разделяет PDF файл на отдельные страницы.
    
    Args:
        pdf_path (str): Путь к исходному PDF файлу
        output_base_dir (str): Базовая директория для сохранения страниц
    
    Returns:
        int: Количество обработанных страниц
    """
    
    # Проверяем существование исходного файла
    if not os.path.exists(pdf_path):
        print(f"❌ Ошибка: файл {pdf_path} не найден!")
        return 0
    
    # Определяем путь к корню проекта (папка, где лежит source.pdf)
    if output_base_dir is None:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        output_base_dir = project_root / "pages"
    else:
        output_base_dir = Path(output_base_dir)
    
    try:
        # Открываем PDF документ
        print(f"📖 Открываем файл: {pdf_path}")
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        print(f"📄 Найдено страниц: {total_pages}")
        print(f"📁 Папки будут созданы в: {output_base_dir.absolute()}")
        
        # Создаем базовую директорию для страниц
        output_path = Path(output_base_dir)
        output_path.mkdir(exist_ok=True)
        
        # Обрабатываем каждую страницу
        for page_num in range(total_pages):
            # Создаем папку для текущей страницы
            page_folder = output_path / f"page_{page_num + 1:03d}"
            page_folder.mkdir(exist_ok=True)
            
            # Создаем новый PDF документ для одной страницы
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            # Сохраняем страницу в отдельный PDF файл
            output_pdf_path = page_folder / f"page_{page_num + 1:03d}.pdf"
            new_doc.save(str(output_pdf_path))
            new_doc.close()
            
            # Показываем прогресс
            progress = (page_num + 1) / total_pages * 100
            print(f"✅ Страница {page_num + 1:03d}/{total_pages:03d} сохранена в {page_folder} ({progress:.1f}%)")
        
        doc.close()
        print(f"🎉 Успешно разделено {total_pages} страниц в папки!")
        return total_pages
        
    except Exception as e:
        print(f"❌ Ошибка при обработке файла: {str(e)}")
        return 0


def main():
    """Основная функция скрипта."""
    
    if len(sys.argv) != 2:
        print("Использование: python split_pdf_pages.py <путь_к_pdf_файлу>")
        print("Пример: python split_pdf_pages.py ../source.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print("=" * 60)
    print("🔄 РАЗДЕЛЕНИЕ PDF НА ОТДЕЛЬНЫЕ СТРАНИЦЫ")
    print("=" * 60)
    
    pages_processed = split_pdf_to_pages(pdf_path)
    
    if pages_processed > 0:
        print(f"\n✨ Готово! Обработано {pages_processed} страниц.")
        print("📁 Каждая страница сохранена в отдельной папке в директории 'pages/'")
    else:
        print("\n❌ Обработка не удалась.")
        sys.exit(1)


if __name__ == "__main__":
    main()
