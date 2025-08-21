#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для валидации структуры файла Глоссарий.md

Автор: AI Assistant  
Дата: 2024
"""

import re
import sys
from pathlib import Path


class GlossaryValidator:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.content = ""
        self.errors = []
        self.warnings = []
        
    def load_file(self):
        """Загружает содержимое файла глоссария"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except FileNotFoundError:
            self.errors.append(f"Файл {self.file_path} не найден")
            return False
        except Exception as e:
            self.errors.append(f"Ошибка при загрузке файла: {e}")
            return False
    
    def validate_structure(self):
        """Проверяет общую структуру файла"""
        lines = self.content.split('\n')
        
        # Проверяем наличие заголовков второго уровня
        h2_pattern = r'^## .+$'
        h2_matches = [i for i, line in enumerate(lines, 1) if re.match(h2_pattern, line)]
        
        if not h2_matches:
            self.warnings.append("Не найдено ни одного заголовка второго уровня (##)")
        
        # Проверяем наличие терминов
        h3_pattern = r'^### .+$'
        h3_matches = [i for i, line in enumerate(lines, 1) if re.match(h3_pattern, line)]
        
        if not h3_matches:
            self.errors.append("Не найдено ни одного термина (заголовка третьего уровня ###)")
        
        return len(h3_matches)
    
    def validate_entries(self):
        """Проверяет структуру отдельных записей"""
        entry_pattern = r'^### (.+?)$\n\n(.*?)(?=^###|\n##|\Z)'
        matches = list(re.finditer(entry_pattern, self.content, re.MULTILINE | re.DOTALL))
        
        for i, match in enumerate(matches, 1):
            term = match.group(1).strip()
            content = match.group(2).strip()
            line_start = self.content[:match.start()].count('\n') + 1
            
            # Проверяем наличие секции "Контекст:"
            if 'Контекст:' not in content:
                self.errors.append(f"Термин '{term}' (строка {line_start}): отсутствует секция 'Контекст:'")
            
            # Проверяем наличие хотя бы одного контекста
            context_pattern = r'- Раздел `[^`]+` \([^)]+\): .+'
            if not re.search(context_pattern, content):
                self.warnings.append(f"Термин '{term}' (строка {line_start}): нет контекстных ссылок")
            
            # Проверяем наличие перевода
            if 'Перевод:' not in content:
                self.warnings.append(f"Термин '{term}' (строка {line_start}): отсутствует перевод")
            else:
                # Проверяем, что перевод не пустой
                translation_match = re.search(r'Перевод: (.+?)(?=\n|$)', content)
                if translation_match and not translation_match.group(1).strip():
                    self.warnings.append(f"Термин '{term}' (строка {line_start}): пустой перевод")
            
            # Проверяем правильность форматирования контекстов
            wrong_contexts = re.findall(r'^- Раздел [^`]', content, re.MULTILINE)
            if wrong_contexts:
                self.errors.append(f"Термин '{term}' (строка {line_start}): неправильное форматирование контекста (отсутствуют обратные кавычки)")
        
        return len(matches)
    
    def validate_duplicates(self):
        """Проверяет наличие дубликатов"""
        pattern = r'^### (.+?)$'
        matches = re.findall(pattern, self.content, re.MULTILINE)
        
        seen = set()
        duplicates = []
        
        for term in matches:
            if term in seen:
                duplicates.append(term)
            else:
                seen.add(term)
        
        if duplicates:
            self.errors.append(f"Найдены дублированные термины: {', '.join(set(duplicates))}")
        
        return len(duplicates)
    
    def validate_formatting(self):
        """Проверяет форматирование"""
        lines = self.content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Проверяем заголовки третьего уровня
            if line.startswith('### '):
                if len(line) <= 4:  # Только '### '
                    self.errors.append(f"Строка {i}: пустой заголовок термина")
                
                # Проверяем, что после заголовка идет пустая строка
                if i < len(lines) and lines[i] != '':
                    self.warnings.append(f"Строка {i}: после заголовка '{line}' должна быть пустая строка")
            
            # Проверяем контекстные ссылки
            if line.startswith('- Раздел '):
                if not re.match(r'- Раздел `[^`]+` \([^)]+\): .+', line):
                    self.errors.append(f"Строка {i}: неправильный формат контекстной ссылки")
            
            # Проверяем переводы
            if line.startswith('Перевод: '):
                if len(line) <= 10:  # Только 'Перевод: '
                    self.warnings.append(f"Строка {i}: пустой перевод")
    
    def generate_report(self):
        """Генерирует отчет о валидации"""
        print("=== ВАЛИДАЦИЯ ГЛОССАРИЯ ===\n")
        
        if not self.load_file():
            self.print_results()
            return False
        
        print(f"📄 Проверяем файл: {self.file_path}")
        
        # Проверяем структуру
        terms_count = self.validate_structure()
        print(f"✓ Найдено терминов: {terms_count}")
        
        # Проверяем записи
        entries_count = self.validate_entries()
        print(f"✓ Проверено записей: {entries_count}")
        
        # Проверяем дубликаты
        duplicates_count = self.validate_duplicates()
        if duplicates_count == 0:
            print("✓ Дубликаты не найдены")
        else:
            print(f"⚠ Найдено дубликатов: {duplicates_count}")
        
        # Проверяем форматирование
        self.validate_formatting()
        print("✓ Проверка форматирования завершена")
        
        self.print_results()
        
        return len(self.errors) == 0
    
    def print_results(self):
        """Выводит результаты валидации"""
        print(f"\n=== РЕЗУЛЬТАТЫ ВАЛИДАЦИИ ===")
        
        if not self.errors and not self.warnings:
            print("🎉 Файл прошел все проверки успешно!")
            return
        
        if self.errors:
            print(f"\n❌ ОШИБКИ ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        print(f"\nИтого: {len(self.errors)} ошибок, {len(self.warnings)} предупреждений")


def main():
    """Главная функция скрипта"""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "Глоссарий.md"
    
    validator = GlossaryValidator(file_path)
    
    try:
        success = validator.generate_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nВалидация прервана пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка при валидации: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
