#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для извлечения информации о шрифтах из всех PDF файлов в папке chapters.
Создает сводный файл fonts.md с информацией о всех найденных шрифтах.

Использование:
    python extract_fonts.py [путь_к_папке_chapters]
    
Пример:
    python extract_fonts.py ../chapters
"""

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import re


def extract_fonts_from_pdf(pdf_path):
    """
    Извлекает информацию о шрифтах из PDF файла.
    
    Args:
        pdf_path (str): Путь к PDF файлу
    
    Returns:
        dict: Информация о шрифтах в файле
    """
    
    doc = None
    try:
        doc = fitz.open(pdf_path)
        fonts_info = {}
        total_pages = doc.page_count
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Получаем список шрифтов на странице
            font_list = page.get_fonts()
            
            for font in font_list:
                font_ref = font[0]      # Ссылка на шрифт
                font_name = font[3]     # Название шрифта
                font_type = font[1]     # Тип шрифта
                font_encoding = font[2] # Кодировка
                
                # Очищаем название шрифта от префиксов
                clean_name = re.sub(r'^[A-Z]{6}\+', '', font_name)
                
                if clean_name not in fonts_info:
                    fonts_info[clean_name] = {
                        'original_name': font_name,
                        'type': font_type,
                        'encoding': font_encoding,
                        'pages': set(),
                        'ref_count': 0
                    }
                
                fonts_info[clean_name]['pages'].add(page_num + 1)
                fonts_info[clean_name]['ref_count'] += 1
        
        # Конвертируем set в list для JSON-совместимости
        for font_info in fonts_info.values():
            font_info['pages'] = sorted(list(font_info['pages']))
        
        return {
            'success': True,
            'fonts': fonts_info,
            'total_pages': total_pages,
            'font_count': len(fonts_info)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'fonts': {},
            'total_pages': 0,
            'font_count': 0
        }
    finally:
        if doc is not None:
            doc.close()


def find_pdf_files(chapters_dir):
    """
    Находит все PDF файлы в папке chapters и её подпапках.
    
    Args:
        chapters_dir (str): Путь к папке chapters
    
    Returns:
        list: Список путей к PDF файлам
    """
    
    chapters_path = Path(chapters_dir)
    
    if not chapters_path.exists():
        print(f"❌ Ошибка: папка {chapters_dir} не найдена!")
        return []
    
    pdf_files = []
    
    # Рекурсивно ищем все PDF файлы
    for pdf_file in chapters_path.rglob('*.pdf'):
        pdf_files.append(pdf_file)
    
    return sorted(pdf_files)


def analyze_all_fonts(chapters_dir):
    """
    Анализирует шрифты во всех PDF файлах.
    
    Args:
        chapters_dir (str): Путь к папке chapters
    
    Returns:
        dict: Сводная информация о шрифтах
    """
    
    pdf_files = find_pdf_files(chapters_dir)
    
    if not pdf_files:
        print(f"❌ В папке {chapters_dir} не найдено PDF файлов!")
        return None
    
    print(f"📁 Найдено PDF файлов: {len(pdf_files)}")
    print(f"🚀 Начинаем анализ шрифтов...\n")
    
    all_fonts = defaultdict(lambda: {
        'files': [],
        'total_pages': [],
        'types': set(),
        'encodings': set(),
        'total_refs': 0
    })
    
    stats = {
        'total_files': len(pdf_files),
        'processed_files': 0,
        'total_pages': 0,
        'files_with_fonts': 0,
        'files_without_fonts': 0,
        'errors': 0,
        'file_results': {}
    }
    
    for i, pdf_file in enumerate(pdf_files, 1):
        relative_path = pdf_file.relative_to(Path(chapters_dir).parent)
        print(f"📄 {i:02d}/{len(pdf_files):02d}: {relative_path}")
        
        result = extract_fonts_from_pdf(pdf_file)
        stats['file_results'][str(relative_path)] = result
        
        if result['success']:
            stats['processed_files'] += 1
            stats['total_pages'] += result['total_pages']
            
            if result['font_count'] > 0:
                stats['files_with_fonts'] += 1
                
                # Объединяем информацию о шрифтах
                for font_name, font_info in result['fonts'].items():
                    all_fonts[font_name]['files'].append(str(relative_path))
                    all_fonts[font_name]['total_pages'].extend(font_info['pages'])
                    all_fonts[font_name]['types'].add(font_info['type'])
                    all_fonts[font_name]['encodings'].add(font_info['encoding'])
                    all_fonts[font_name]['total_refs'] += font_info['ref_count']
                
                print(f"   ✅ Найдено шрифтов: {result['font_count']}")
                print(f"   📄 Страниц: {result['total_pages']}")
            else:
                stats['files_without_fonts'] += 1
                print(f"   📄 Шрифтов не найдено (страниц: {result['total_pages']})")
        else:
            stats['errors'] += 1
            print(f"   ❌ Ошибка: {result['error']}")
        
        print()
    
    # Конвертируем sets в lists для удобства
    for font_info in all_fonts.values():
        font_info['types'] = sorted(list(font_info['types']))
        font_info['encodings'] = sorted(list(font_info['encodings']))
        font_info['unique_pages'] = len(set(font_info['total_pages']))
        font_info['total_page_refs'] = len(font_info['total_pages'])
    
    stats['unique_fonts'] = len(all_fonts)
    stats['all_fonts'] = dict(all_fonts)
    
    return stats


def create_fonts_markdown(stats, output_file):
    """
    Создает Markdown файл с информацией о шрифтах.
    
    Args:
        stats (dict): Статистика анализа шрифтов
        output_file (str): Путь к выходному файлу
    """
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Заголовок
            f.write("# Анализ шрифтов в PDF файлах проекта\n\n")
            
            # Метаинформация
            f.write(f"<!-- \n")
            f.write(f"Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Проанализировано файлов: {stats['processed_files']}\n")
            f.write(f"Найдено уникальных шрифтов: {stats['unique_fonts']}\n")
            f.write(f"-->\n\n")
            
            # Общая статистика
            f.write("## 📊 Общая статистика\n\n")
            f.write(f"- **Всего PDF файлов:** {stats['total_files']}\n")
            f.write(f"- **Обработано успешно:** {stats['processed_files']}\n")
            f.write(f"- **Файлов с шрифтами:** {stats['files_with_fonts']}\n")
            f.write(f"- **Файлов без шрифтов:** {stats['files_without_fonts']}\n")
            f.write(f"- **Ошибок обработки:** {stats['errors']}\n")
            f.write(f"- **Всего страниц:** {stats['total_pages']:,}\n")
            f.write(f"- **Уникальных шрифтов:** {stats['unique_fonts']}\n\n")
            
            # Топ шрифтов по использованию
            f.write("## 🏆 Топ шрифтов по использованию\n\n")
            
            # Сортируем шрифты по количеству ссылок
            sorted_fonts = sorted(
                stats['all_fonts'].items(),
                key=lambda x: x[1]['total_refs'],
                reverse=True
            )
            
            f.write("| Шрифт | Файлов | Ссылок | Страниц | Типы |\n")
            f.write("|-------|--------|--------|---------|------|\n")
            
            for font_name, font_info in sorted_fonts[:20]:  # Топ 20
                files_count = len(font_info['files'])
                refs_count = font_info['total_refs']
                pages_count = font_info['unique_pages']
                types = ', '.join(font_info['types'])
                
                f.write(f"| `{font_name}` | {files_count} | {refs_count} | {pages_count} | {types} |\n")
            
            f.write("\n")
            
            # Полный список шрифтов
            f.write("## 📝 Полный список шрифтов\n\n")
            
            for font_name, font_info in sorted_fonts:
                f.write(f"### `{font_name}`\n\n")
                f.write(f"- **Использован в файлах:** {len(font_info['files'])}\n")
                f.write(f"- **Общее количество ссылок:** {font_info['total_refs']}\n")
                f.write(f"- **Уникальных страниц:** {font_info['unique_pages']}\n")
                f.write(f"- **Всего упоминаний на страницах:** {font_info['total_page_refs']}\n")
                f.write(f"- **Типы шрифта:** {', '.join(font_info['types'])}\n")
                f.write(f"- **Кодировки:** {', '.join(font_info['encodings'])}\n")
                
                f.write(f"\n**Файлы:**\n")
                for file_path in font_info['files']:
                    f.write(f"- `{file_path}`\n")
                
                f.write("\n")
            
            # Статистика по файлам
            f.write("## 📁 Статистика по файлам\n\n")
            
            for file_path, result in stats['file_results'].items():
                f.write(f"### `{file_path}`\n\n")
                
                if result['success']:
                    f.write(f"- **Страниц:** {result['total_pages']}\n")
                    f.write(f"- **Шрифтов:** {result['font_count']}\n")
                    
                    if result['font_count'] > 0:
                        f.write(f"\n**Найденные шрифты:**\n")
                        for font_name, font_info in result['fonts'].items():
                            pages_range = f"{min(font_info['pages'])}-{max(font_info['pages'])}" if len(font_info['pages']) > 1 else str(font_info['pages'][0])
                            f.write(f"- `{font_name}` (страницы: {pages_range}, ссылок: {font_info['ref_count']})\n")
                else:
                    f.write(f"- **Ошибка:** {result['error']}\n")
                
                f.write("\n")
            
            # Анализ типов шрифтов
            f.write("## 🎨 Анализ типов шрифтов\n\n")
            
            type_counter = Counter()
            encoding_counter = Counter()
            
            for font_info in stats['all_fonts'].values():
                for font_type in font_info['types']:
                    type_counter[font_type] += 1
                for encoding in font_info['encodings']:
                    encoding_counter[encoding] += 1
            
            f.write("### Типы шрифтов\n\n")
            f.write("| Тип | Количество шрифтов |\n")
            f.write("|-----|--------------------|\n")
            for font_type, count in type_counter.most_common():
                f.write(f"| `{font_type}` | {count} |\n")
            
            f.write("\n### Кодировки\n\n")
            f.write("| Кодировка | Количество шрифтов |\n")
            f.write("|-----------|--------------------|\n")
            for encoding, count in encoding_counter.most_common():
                f.write(f"| `{encoding}` | {count} |\n")
            
            f.write("\n---\n\n")
            f.write(f"*Анализ выполнен {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Скрипт: extract_fonts.py*\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания файла {output_file}: {str(e)}")
        return False


def print_final_stats(stats):
    """Выводит финальную статистику."""
    
    if not stats:
        return
    
    print("🎉" + "="*60)
    print("✨ АНАЛИЗ ШРИФТОВ ЗАВЕРШЕН!")
    print("🎉" + "="*60)
    print(f"📊 Результаты:")
    print(f"   📁 Обработано файлов: {stats['processed_files']}/{stats['total_files']}")
    print(f"   📄 Всего страниц: {stats['total_pages']:,}")
    print(f"   🔤 Уникальных шрифтов: {stats['unique_fonts']}")
    print(f"   ✅ Файлов с шрифтами: {stats['files_with_fonts']}")
    print(f"   📄 Файлов без шрифтов: {stats['files_without_fonts']}")
    print(f"   ❌ Ошибок: {stats['errors']}")
    
    if stats['unique_fonts'] > 0:
        # Топ-5 самых используемых шрифтов
        sorted_fonts = sorted(
            stats['all_fonts'].items(),
            key=lambda x: x[1]['total_refs'],
            reverse=True
        )
        
        print(f"\n🏆 Топ-5 самых используемых шрифтов:")
        for i, (font_name, font_info) in enumerate(sorted_fonts[:5], 1):
            print(f"   {i}. {font_name} ({font_info['total_refs']} ссылок)")
    
    print("🎉" + "="*60)


def main():
    """Основная функция скрипта."""
    
    # Определяем папку chapters
    if len(sys.argv) > 1:
        chapters_dir = sys.argv[1]
    else:
        # По умолчанию ищем в папке chapters относительно корня проекта
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        chapters_dir = project_root / "chapters"
    
    # Определяем выходной файл
    output_file = Path(__file__).parent.parent / "fonts.md"
    
    print("=" * 70)
    print("🔤 АНАЛИЗ ШРИФТОВ В PDF ФАЙЛАХ")
    print("=" * 70)
    print(f"📁 Папка с главами: {Path(chapters_dir).absolute()}")
    print(f"📄 Выходной файл: {output_file.absolute()}")
    print()
    
    # Анализируем шрифты
    stats = analyze_all_fonts(chapters_dir)
    
    if not stats:
        print("❌ Анализ не удался.")
        sys.exit(1)
    
    # Создаем Markdown файл
    print("📝 Создаем файл fonts.md...")
    success = create_fonts_markdown(stats, output_file)
    
    if success:
        print(f"✅ Файл создан: {output_file}")
        print_final_stats(stats)
        
        file_size = output_file.stat().st_size / 1024  # KB
        print(f"\n💡 Размер файла: {file_size:.1f} KB")
        print(f"📁 Проверьте содержимое: {output_file.absolute()}")
    else:
        print("❌ Создание файла не удалось.")
        sys.exit(1)


if __name__ == "__main__":
    main()
