#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный инструмент для работы с глоссарием

Автор: AI Assistant
Дата: 2024
"""

import sys
import subprocess
from pathlib import Path


def print_help():
    """Выводит справку по использованию"""
    print("""
🔧 ИНСТРУМЕНТЫ ДЛЯ РАБОТЫ С ГЛОССАРИЕМ

Использование: python scripts/glossary_tools.py <команда> [файл]

Команды:
  analyze    - Анализ структуры глоссария
  validate   - Валидация корректности структуры
  merge      - Объединение дубликатов
  fix        - Полный цикл: анализ → валидация → объединение → повторная валидация
  help       - Показать эту справку

Примеры:
  python scripts/glossary_tools.py analyze
  python scripts/glossary_tools.py validate Глоссарий.md
  python scripts/glossary_tools.py merge
  python scripts/glossary_tools.py fix

По умолчанию обрабатывается файл "Глоссарий.md" в текущей директории.
""")


def run_script(script_name, file_path=None):
    """Запускает указанный скрипт"""
    script_path = Path(__file__).parent / f"{script_name}.py"
    
    if not script_path.exists():
        print(f"❌ Скрипт {script_name}.py не найден")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if file_path:
        cmd.append(file_path)
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка при запуске {script_name}: {e}")
        return False


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    file_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "help" or command == "-h" or command == "--help":
        print_help()
        return
    
    print("🔧 Инструменты для работы с глоссарием\n")
    
    if command == "analyze":
        print("📊 Запуск анализа структуры...")
        run_script("analyze_glossary", file_path)
    
    elif command == "validate":
        print("✅ Запуск валидации...")
        success = run_script("validate_glossary", file_path)
        if success:
            print("\n🎉 Валидация прошла успешно!")
        else:
            print("\n❌ Обнаружены ошибки валидации")
    
    elif command == "merge":
        print("🔄 Запуск объединения дубликатов...")
        success = run_script("merge_glossary_duplicates", file_path)
        if success:
            print("\n🎉 Дубликаты успешно объединены!")
        else:
            print("\n❌ Ошибка при объединении дубликатов")
    
    elif command == "fix":
        print("🛠️  Запуск полного цикла исправлений...\n")
        
        # Шаг 1: Анализ
        print("1️⃣  Анализ структуры:")
        print("-" * 50)
        run_script("analyze_glossary", file_path)
        
        # Шаг 2: Валидация
        print("\n2️⃣  Валидация:")
        print("-" * 50)
        validation_success = run_script("validate_glossary", file_path)
        
        # Шаг 3: Объединение дубликатов (если есть ошибки валидации)
        if not validation_success:
            print("\n3️⃣  Объединение дубликатов:")
            print("-" * 50)
            merge_success = run_script("merge_glossary_duplicates", file_path)
            
            if merge_success:
                # Шаг 4: Повторная валидация
                print("\n4️⃣  Повторная валидация:")
                print("-" * 50)
                final_validation = run_script("validate_glossary", file_path)
                
                if final_validation:
                    print("\n🎉 Все исправления применены успешно!")
                else:
                    print("\n⚠️  Остались некоторые проблемы, требующие ручного исправления")
            else:
                print("\n❌ Ошибка при объединении дубликатов")
        else:
            print("\n🎉 Глоссарий уже в отличном состоянии!")
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("Используйте 'help' для получения справки")
        sys.exit(1)


if __name__ == "__main__":
    main()
