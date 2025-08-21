#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания файловой структуры на основе заголовков markdown файла.

Анализирует заголовки разных уровней в markdown файле и создает соответствующую
структуру папок и файлов, где:
- Названия папок соответствуют названиям заголовков
- Уровни вложения папок соответствуют уровням заголовков
- Если у заголовка нет подзаголовков, создается файл .md вместо папки
- В каждой папке создается файл .md с тем же именем
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class HeaderNode:
    """Класс для представления узла дерева заголовков."""
    
    def __init__(self, level: int, title: str, line_number: int):
        self.level = level
        self.title = title
        self.line_number = line_number
        self.children: List['HeaderNode'] = []
        self.parent: Optional['HeaderNode'] = None
    
    def add_child(self, child: 'HeaderNode'):
        """Добавить дочерний узел."""
        child.parent = self
        self.children.append(child)
    
    def has_children(self) -> bool:
        """Проверить, есть ли дочерние узлы."""
        return len(self.children) > 0
    
    def get_safe_filename(self) -> str:
        """Получить безопасное имя файла/папки."""
        # Удаляем или заменяем недопустимые символы
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', self.title)
        # Удаляем лишние пробелы и точки в конце
        safe_name = safe_name.strip('. ')
        # Ограничиваем длину имени
        if len(safe_name) > 100:
            safe_name = safe_name[:100].strip()
        return safe_name
    
    def __str__(self):
        return f"{'  ' * (self.level - 1)}{'#' * self.level} {self.title}"


def parse_markdown_headers(file_path: str) -> List[HeaderNode]:
    """
    Парсит заголовки из markdown файла и возвращает список узлов.
    
    Args:
        file_path: Путь к markdown файлу
        
    Returns:
        Список корневых узлов дерева заголовков
    """
    headers = []
    stack = []  # Стек для отслеживания иерархии
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Ищем заголовки (# ## ### и т.д.)
                header_match = re.match(r'^(#+)\s+(.+)$', line)
                if header_match:
                    level = len(header_match.group(1))
                    title = header_match.group(2).strip()
                    
                    # Создаем новый узел
                    node = HeaderNode(level, title, line_num)
                    
                    # Находим правильного родителя
                    while stack and stack[-1].level >= level:
                        stack.pop()
                    
                    if stack:
                        # Добавляем как дочерний к последнему элементу в стеке
                        stack[-1].add_child(node)
                    else:
                        # Это корневой элемент
                        headers.append(node)
                    
                    stack.append(node)
    
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return []
    
    return headers


def create_file_structure(headers: List[HeaderNode], base_path: str, dry_run: bool = False):
    """
    Создает файловую структуру на основе дерева заголовков.
    
    Args:
        headers: Список корневых узлов дерева заголовков
        base_path: Базовый путь для создания структуры
        dry_run: Если True, только показывает что будет создано без создания файлов
    """
    base_path = Path(base_path)
    
    if not dry_run:
        # Создаем базовую папку если её нет
        base_path.mkdir(parents=True, exist_ok=True)
    
    def process_node(node: HeaderNode, current_path: Path):
        """Рекурсивно обрабатывает узел и создает файлы/папки."""
        safe_name = node.get_safe_filename()
        
        if node.has_children():
            # Если есть дочерние элементы - создаем папку
            folder_path = current_path / safe_name
            
            if dry_run:
                print(f"[ПАПКА] {folder_path}")
            else:
                folder_path.mkdir(exist_ok=True)
                print(f"Создана папка: {folder_path}")
            
            # Создаем файл с тем же именем внутри папки
            file_path = folder_path / f"{safe_name}.md"
            if dry_run:
                print(f"[ФАЙЛ]  {file_path}")
            else:
                if not file_path.exists():
                    file_path.write_text(f"# {node.title}\n\n", encoding='utf-8')
                    print(f"Создан файл: {file_path}")
            
            # Рекурсивно обрабатываем дочерние элементы
            for child in node.children:
                process_node(child, folder_path)
        
        else:
            # Если нет дочерних элементов - создаем только файл
            file_path = current_path / f"{safe_name}.md"
            
            if dry_run:
                print(f"[ФАЙЛ]  {file_path}")
            else:
                if not file_path.exists():
                    file_path.write_text(f"# {node.title}\n\n", encoding='utf-8')
                    print(f"Создан файл: {file_path}")
    
    # Обрабатываем все корневые узлы
    for header in headers:
        process_node(header, base_path)


def print_tree(headers: List[HeaderNode], indent: int = 0):
    """Выводит дерево заголовков в консоль."""
    for header in headers:
        print("  " * indent + f"{'#' * header.level} {header.title}")
        if header.children:
            print_tree(header.children, indent + 1)


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Создание файловой структуры на основе заголовков markdown файла"
    )
    parser.add_argument(
        "input_file", 
        help="Путь к входному markdown файлу"
    )
    parser.add_argument(
        "-o", "--output", 
        default="ru/Хранилище",
        help="Выходная папка (по умолчанию: ru/Хранилище)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Показать что будет создано без создания файлов"
    )
    parser.add_argument(
        "--show-tree", 
        action="store_true",
        help="Показать дерево заголовков"
    )
    
    args = parser.parse_args()
    
    print(f"Анализ файла: {args.input_file}")
    
    # Парсим заголовки
    headers = parse_markdown_headers(args.input_file)
    
    if not headers:
        print("Заголовки не найдены или произошла ошибка при чтении файла")
        return
    
    print(f"Найдено {len(headers)} корневых заголовков")
    
    # Показываем дерево если запрошено
    if args.show_tree:
        print("\nСтруктура заголовков:")
        print_tree(headers)
        print()
    
    # Создаем файловую структуру
    if args.dry_run:
        print(f"\nПредварительный просмотр структуры в {args.output}:")
    else:
        print(f"\nСоздание структуры в {args.output}:")
    
    create_file_structure(headers, args.output, args.dry_run)
    
    if args.dry_run:
        print(f"\nДля создания файлов запустите без флага --dry-run")
    else:
        print(f"\nСтруктура успешно создана в {args.output}")


if __name__ == "__main__":
    main()
