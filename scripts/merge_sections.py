#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для объединения страниц разделов в единые Markdown файлы.
Создает для каждой папки-раздела файл с названием раздела, содержащий весь текст страниц.

Использование:
    python merge_sections.py [путь_к_папке_pages]
    
Пример:
    python merge_sections.py ../pages
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


def extract_page_number_from_filename(filename):
    """
    Извлекает номер страницы из имени файла.
    
    Args:
        filename (str): Имя файла (например, "page_008.md")
    
    Returns:
        int: Номер страницы или 0 если не найден
    """
    match = re.search(r'page_(\d+)\.md', filename)
    return int(match.group(1)) if match else 0


def read_page_content(page_file):
    """
    Читает содержимое Markdown файла страницы, убирая служебную информацию.
    
    Args:
        page_file (Path): Путь к файлу страницы
    
    Returns:
        dict: Информация о странице
    """
    
    try:
        with open(page_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Извлекаем номер страницы из содержимого
        page_match = re.search(r'# Страница (\d+)', content)
        page_number = int(page_match.group(1)) if page_match else 0
        
        # Убираем заголовок "# Страница X"
        content = re.sub(r'^# Страница \d+\n\n', '', content)
        
        # Убираем HTML комментарии с метаинформацией
        content = re.sub(r'<!-- \n.*?\n-->\n\n', '', content, flags=re.DOTALL)
        
        # Убираем финальный разделитель
        content = re.sub(r'\n\n---\n\*Извлечено из страницы \d+\*\n$', '', content)
        content = re.sub(r'\n\n---\n\*Страница \d+\*\n$', '', content)
        
        # Очищаем лишние переносы строк
        content = content.strip()
        
        # Проверяем, есть ли реальный текст (не только служебные сообщения)
        has_content = bool(content and 
                          not content.startswith('*На этой странице нет текста') and
                          not content.startswith('*Ошибка извлечения текста'))
        
        return {
            'page_number': page_number,
            'content': content,
            'has_content': has_content,
            'char_count': len(content),
            'file_path': page_file
        }
        
    except Exception as e:
        print(f"❌ Ошибка чтения файла {page_file}: {str(e)}")
        return {
            'page_number': 0,
            'content': f"*Ошибка чтения страницы: {str(e)}*",
            'has_content': False,
            'char_count': 0,
            'file_path': page_file
        }


def create_section_title(section_name):
    """
    Создает красивое название раздела из имени папки.
    
    Args:
        section_name (str): Имя папки раздела
    
    Returns:
        str: Отформатированное название
    """
    
    # Убираем номер и подчеркивания
    title = re.sub(r'^\d+_', '', section_name)
    title = title.replace('_', ' ').title()
    
    # Специальные случаи для красивого отображения
    replacements = {
        'And': 'and',
        'Of': 'of',
        'The': 'the',
        'A': 'a',
        'An': 'an',
        'In': 'in',
        'On': 'on',
        'At': 'at',
        'To': 'to',
        'For': 'for',
        'With': 'with',
        'By': 'by'
    }
    
    words = title.split()
    for i, word in enumerate(words):
        if i > 0 and word in replacements:  # Не заменяем первое слово
            words[i] = replacements[word]
    
    return ' '.join(words)


def merge_section_pages(section_path):
    """
    Объединяет все страницы раздела в единый Markdown файл.
    
    Args:
        section_path (Path): Путь к папке раздела
    
    Returns:
        dict: Статистика обработки раздела
    """
    
    section_name = section_path.name
    print(f"\n📂 Обрабатываем раздел: {section_name}")
    
    # Находим все подпапки со страницами
    page_folders = [d for d in section_path.iterdir() 
                   if d.is_dir() and d.name.startswith('page_')]
    
    if not page_folders:
        print(f"   ⚠️  Не найдено папок со страницами в {section_name}")
        return {'success': False, 'pages': 0, 'chars': 0}
    
    # Собираем информацию о всех страницах
    pages_info = []
    
    for page_folder in page_folders:
        # Ищем Markdown файл в папке страницы
        md_files = list(page_folder.glob('*.md'))
        # Исключаем файлы с информацией об изображениях
        md_files = [f for f in md_files if not f.name.endswith('_images.md')]
        
        if md_files:
            page_info = read_page_content(md_files[0])
            pages_info.append(page_info)
    
    # Сортируем страницы по номеру
    pages_info.sort(key=lambda x: x['page_number'])
    
    if not pages_info:
        print(f"   ⚠️  Не найдено Markdown файлов в {section_name}")
        return {'success': False, 'pages': 0, 'chars': 0}
    
    # Создаем объединенный файл
    section_title = create_section_title(section_name)
    output_file = section_path / f"{section_name}.md"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Заголовок раздела
            f.write(f"# {section_title}\n\n")
            
            # Метаинформация
            f.write(f"<!-- \n")
            f.write(f"Раздел: {section_name}\n")
            f.write(f"Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Страниц: {len(pages_info)}\n")
            f.write(f"Диапазон страниц: {pages_info[0]['page_number']}-{pages_info[-1]['page_number']}\n")
            f.write(f"-->\n\n")
            
            # Оглавление страниц
            f.write(f"## Содержание раздела\n\n")
            pages_with_content = [p for p in pages_info if p['has_content']]
            pages_without_content = [p for p in pages_info if not p['has_content']]
            
            f.write(f"**Страниц с текстом:** {len(pages_with_content)}\n")
            f.write(f"**Страниц без текста:** {len(pages_without_content)}\n")
            f.write(f"**Общий объем:** {sum(p['char_count'] for p in pages_with_content):,} символов\n\n")
            
            if pages_without_content:
                f.write(f"*Страницы без текста: {', '.join(str(p['page_number']) for p in pages_without_content)}*\n\n")
            
            f.write("---\n\n")
            
            # Содержимое страниц
            for i, page_info in enumerate(pages_info):
                page_num = page_info['page_number']
                
                # Заголовок страницы
                f.write(f"## Страница {page_num}\n\n")
                
                # Содержимое
                if page_info['has_content']:
                    f.write(page_info['content'])
                    f.write("\n\n")
                else:
                    f.write("*На этой странице нет текста для перевода.*\n\n")
                
                # Разделитель между страницами (кроме последней)
                if i < len(pages_info) - 1:
                    f.write("---\n\n")
            
            # Финальная информация
            f.write(f"\n---\n\n")
            f.write(f"*Раздел '{section_title}' объединен из {len(pages_info)} страниц*\n")
            f.write(f"*Исходные файлы: страницы {pages_info[0]['page_number']}-{pages_info[-1]['page_number']}*\n")
        
        # Статистика
        total_chars = sum(p['char_count'] for p in pages_with_content)
        print(f"   ✅ Создан файл: {output_file.name}")
        print(f"   📊 Страниц: {len(pages_info)} (с текстом: {len(pages_with_content)})")
        print(f"   📝 Символов: {total_chars:,}")
        
        return {
            'success': True,
            'pages': len(pages_info),
            'pages_with_content': len(pages_with_content),
            'chars': total_chars,
            'output_file': output_file
        }
        
    except Exception as e:
        print(f"   ❌ Ошибка создания файла: {str(e)}")
        return {'success': False, 'pages': 0, 'chars': 0}


def merge_all_sections(pages_dir):
    """
    Объединяет страницы всех разделов.
    
    Args:
        pages_dir (str): Путь к директории с разделами
    
    Returns:
        dict: Общая статистика
    """
    
    pages_path = Path(pages_dir)
    
    if not pages_path.exists():
        print(f"❌ Ошибка: папка {pages_dir} не найдена!")
        return None
    
    # Находим все папки разделов
    section_folders = [d for d in pages_path.iterdir() 
                      if d.is_dir() and re.match(r'^\d+_', d.name)]
    
    if not section_folders:
        print(f"❌ В папке {pages_dir} не найдено разделов!")
        return None
    
    # Сортируем по номеру раздела
    section_folders.sort(key=lambda x: x.name)
    
    print(f"📚 Найдено разделов: {len(section_folders)}")
    print(f"🚀 Начинаем объединение страниц...\n")
    
    stats = {
        'total_sections': len(section_folders),
        'processed_sections': 0,
        'total_pages': 0,
        'total_pages_with_content': 0,
        'total_chars': 0,
        'created_files': [],
        'errors': 0
    }
    
    for section_folder in section_folders:
        result = merge_section_pages(section_folder)
        
        if result['success']:
            stats['processed_sections'] += 1
            stats['total_pages'] += result['pages']
            stats['total_pages_with_content'] += result['pages_with_content']
            stats['total_chars'] += result['chars']
            stats['created_files'].append(result['output_file'])
        else:
            stats['errors'] += 1
    
    return stats


def print_final_stats(stats):
    """Выводит финальную статистику."""
    
    if not stats:
        return
    
    print("\n🎉" + "="*60)
    print("✨ ОБЪЕДИНЕНИЕ РАЗДЕЛОВ ЗАВЕРШЕНО!")
    print("🎉" + "="*60)
    print(f"📊 Общая статистика:")
    print(f"   📂 Всего разделов: {stats['total_sections']}")
    print(f"   ✅ Обработано: {stats['processed_sections']}")
    print(f"   📄 Всего страниц: {stats['total_pages']}")
    print(f"   📝 Страниц с текстом: {stats['total_pages_with_content']}")
    print(f"   🔤 Всего символов: {stats['total_chars']:,}")
    print(f"   📁 Создано файлов: {len(stats['created_files'])}")
    print(f"   ❌ Ошибок: {stats['errors']}")
    
    if stats['created_files']:
        print(f"\n📋 Созданные файлы:")
        for file_path in stats['created_files']:
            file_size = file_path.stat().st_size / 1024  # KB
            print(f"   📄 {file_path.name} ({file_size:.1f} KB)")
    
    print("\n💡 Теперь можно работать с объединенными файлами разделов!")
    print("   Каждый файл содержит весь текст раздела для удобного перевода.")
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
    print("📚 ОБЪЕДИНЕНИЕ СТРАНИЦ РАЗДЕЛОВ В MARKDOWN ФАЙЛЫ")
    print("=" * 70)
    print(f"📁 Папка с разделами: {Path(pages_dir).absolute()}")
    
    stats = merge_all_sections(pages_dir)
    print_final_stats(stats)
    
    if stats and stats['processed_sections'] > 0:
        print(f"\n✨ Успешно создано {stats['processed_sections']} объединенных файлов!")
    else:
        print("\n❌ Обработка не удалась.")
        sys.exit(1)


if __name__ == "__main__":
    main()
