#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для разделения первых N страниц PDF-файла.
Используется для проверки работы основного скрипта на небольшом количестве страниц.

Использование:
    python test_split_pages.py <путь_к_pdf_файлу> [количество_страниц]
    
Пример:
    python test_split_pages.py ../source.pdf 10
"""

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path


def test_split_pdf_pages(pdf_path, max_pages=10, output_base_dir=None):
    """
    Разделяет первые N страниц PDF файла для тестирования.
    
    Args:
        pdf_path (str): Путь к исходному PDF файлу
        max_pages (int): Максимальное количество страниц для обработки
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
        output_base_dir = project_root / "pages_test"
    else:
        output_base_dir = Path(output_base_dir)
    
    try:
        # Открываем PDF документ
        print(f"📖 Открываем файл: {pdf_path}")
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        # Определяем количество страниц для обработки
        pages_to_process = min(max_pages, total_pages)
        
        print(f"📄 Всего страниц в документе: {total_pages}")
        print(f"🔬 Будем обрабатывать: {pages_to_process} страниц (тест)")
        print(f"📁 Тестовые папки будут созданы в: {output_base_dir.absolute()}")
        
        # Создаем базовую директорию для тестовых страниц
        output_path = Path(output_base_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n🚀 Начинаем обработку...")
        
        # Обрабатываем каждую страницу
        for page_num in range(pages_to_process):
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
            
            # Получаем информацию о странице для отчета
            page = doc.load_page(page_num)
            text_length = len(page.get_text().strip())
            image_count = len(page.get_images())
            
            # Показываем прогресс с дополнительной информацией
            progress = (page_num + 1) / pages_to_process * 100
            print(f"✅ Страница {page_num + 1:03d}/{pages_to_process:03d} → {page_folder.name}")
            print(f"   📄 PDF: {output_pdf_path.name}")
            print(f"   📝 Символов текста: {text_length}")
            print(f"   🖼️  Изображений: {image_count}")
            print(f"   📊 Прогресс: {progress:.1f}%")
            print()
        
        doc.close()
        
        print("🎉" + "="*50)
        print(f"✨ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
        print(f"📊 Обработано страниц: {pages_to_process}")
        print(f"📁 Результаты в папке: {output_base_dir}")
        print("🎉" + "="*50)
        
        return pages_to_process
        
    except Exception as e:
        print(f"❌ Ошибка при обработке файла: {str(e)}")
        return 0


def main():
    """Основная функция скрипта."""
    
    if len(sys.argv) < 2:
        print("Использование: python test_split_pages.py <путь_к_pdf_файлу> [количество_страниц]")
        print("Пример: python test_split_pages.py source.pdf 10")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print("=" * 60)
    print(f"🧪 ТЕСТИРОВАНИЕ РАЗДЕЛЕНИЯ PDF ({max_pages} СТРАНИЦ)")
    print("=" * 60)
    
    pages_processed = test_split_pdf_pages(pdf_path, max_pages)
    
    if pages_processed > 0:
        print(f"\n✅ Тест прошел успешно!")
        print(f"📈 Обработано {pages_processed} страниц")
        print(f"📁 Проверьте папку 'pages_test/' для просмотра результатов")
        print(f"\n💡 Если результат устраивает, можно запускать полную обработку:")
        print(f"   python scripts/split_pdf_pages.py {pdf_path}")
    else:
        print("\n❌ Тест не удался.")
        sys.exit(1)


if __name__ == "__main__":
    main()
