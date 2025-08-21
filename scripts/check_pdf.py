#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для предварительной проверки PDF файла.
Анализирует структуру, размер, защиту и другие характеристики.

Использование:
    python check_pdf.py <путь_к_pdf_файлу>
"""

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path


def analyze_pdf(pdf_path):
    """
    Анализирует PDF файл и выводит подробную информацию.
    
    Args:
        pdf_path (str): Путь к PDF файлу
    
    Returns:
        dict: Словарь с информацией о файле
    """
    
    if not os.path.exists(pdf_path):
        print(f"❌ Ошибка: файл {pdf_path} не найден!")
        return None
    
    try:
        # Получаем информацию о файле
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        
        # Открываем документ
        doc = fitz.open(pdf_path)
        
        info = {
            'file_path': pdf_path,
            'file_size_mb': round(file_size, 2),
            'page_count': len(doc),
            'is_encrypted': doc.is_encrypted,
            'needs_pass': doc.needs_pass,
            'metadata': doc.metadata,
            'has_images': False,
            'has_text': False,
            'estimated_images': 0,
            'sample_text': ""
        }
        
        # Анализируем первые несколько страниц для примера
        pages_to_check = min(3, len(doc))
        total_text_length = 0
        
        for page_num in range(pages_to_check):
            page = doc.load_page(page_num)
            
            # Проверяем текст
            text = page.get_text()
            if text.strip():
                info['has_text'] = True
                total_text_length += len(text)
                if not info['sample_text'] and len(text.strip()) > 50:
                    info['sample_text'] = text.strip()[:200] + "..."
            
            # Проверяем изображения
            image_list = page.get_images()
            if image_list:
                info['has_images'] = True
                info['estimated_images'] += len(image_list)
        
        # Экстраполируем количество изображений на весь документ
        if pages_to_check > 0:
            info['estimated_images'] = int(info['estimated_images'] * len(doc) / pages_to_check)
        
        info['avg_text_per_page'] = total_text_length // pages_to_check if pages_to_check > 0 else 0
        
        doc.close()
        return info
        
    except Exception as e:
        print(f"❌ Ошибка при анализе файла: {str(e)}")
        return None


def print_analysis(info):
    """Выводит результаты анализа в читаемом виде."""
    
    if not info:
        return
    
    print("=" * 60)
    print("📊 АНАЛИЗ PDF ФАЙЛА")
    print("=" * 60)
    
    print(f"📁 Файл: {info['file_path']}")
    print(f"📏 Размер: {info['file_size_mb']} MB")
    print(f"📄 Страниц: {info['page_count']}")
    
    print(f"\n🔒 Защита:")
    print(f"   Зашифрован: {'Да' if info['is_encrypted'] else 'Нет'}")
    print(f"   Нужен пароль: {'Да' if info['needs_pass'] else 'Нет'}")
    
    print(f"\n📝 Содержимое:")
    print(f"   Есть текст: {'Да' if info['has_text'] else 'Нет'}")
    print(f"   Есть изображения: {'Да' if info['has_images'] else 'Нет'}")
    print(f"   Примерное количество изображений: {info['estimated_images']}")
    print(f"   Среднее количество символов на страницу: {info['avg_text_per_page']}")
    
    if info['sample_text']:
        print(f"\n📖 Образец текста:")
        print(f"   {info['sample_text']}")
    
    if info['metadata']:
        print(f"\n📋 Метаданные:")
        for key, value in info['metadata'].items():
            if value:
                print(f"   {key}: {value}")
    
    # Предупреждения и рекомендации
    print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ И РЕКОМЕНДАЦИИ:")
    
    if info['needs_pass']:
        print("   🔐 Файл защищен паролем - потребуется ввод пароля")
    
    if not info['has_text']:
        print("   📷 Текст не обнаружен - возможно, файл состоит из сканированных изображений")
        print("       Рекомендуется использовать OCR для извлечения текста")
    
    if info['file_size_mb'] > 100:
        print(f"   💾 Большой размер файла ({info['file_size_mb']} MB) - обработка может занять много времени")
    
    if info['page_count'] > 500:
        print(f"   📚 Много страниц ({info['page_count']}) - будет создано много файлов")
    
    if info['estimated_images'] > 1000:
        print(f"   🖼️  Много изображений ({info['estimated_images']}) - потребуется много дискового пространства")
    
    # Оценка дискового пространства
    estimated_space = (info['file_size_mb'] * 1.5 + info['estimated_images'] * 0.5)
    print(f"\n💾 Примерная потребность в дисковом пространстве: {estimated_space:.1f} MB")


def main():
    """Основная функция скрипта."""
    
    if len(sys.argv) != 2:
        print("Использование: python check_pdf.py <путь_к_pdf_файлу>")
        print("Пример: python check_pdf.py ../source.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    info = analyze_pdf(pdf_path)
    print_analysis(info)


if __name__ == "__main__":
    main()
