#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для анализа структуры файла Глоссарий.md

Автор: AI Assistant
Дата: 2024
"""

import re
import sys
from collections import defaultdict, Counter
from pathlib import Path


class GlossaryAnalyzer:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.content = ""
        
    def load_file(self):
        """Загружает содержимое файла глоссария"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except FileNotFoundError:
            print(f"✗ Файл {self.file_path} не найден")
            return False
        except Exception as e:
            print(f"✗ Ошибка при загрузке файла: {e}")
            return False
    
    def find_duplicates(self):
        """Находит дублированные записи"""
        pattern = r'^### (.+?)$'
        matches = re.findall(pattern, self.content, re.MULTILINE)
        
        term_counts = Counter(matches)
        duplicates = {term: count for term, count in term_counts.items() if count > 1}
        
        return duplicates, len(matches)
    
    def analyze_structure(self):
        """Анализирует структуру глоссария"""
        # Находим все заголовки разных уровней
        h1_pattern = r'^# (.+?)$'
        h2_pattern = r'^## (.+?)$'  
        h3_pattern = r'^### (.+?)$'
        
        h1_matches = re.findall(h1_pattern, self.content, re.MULTILINE)
        h2_matches = re.findall(h2_pattern, self.content, re.MULTILINE)
        h3_matches = re.findall(h3_pattern, self.content, re.MULTILINE)
        
        return {
            'h1_count': len(h1_matches),
            'h2_count': len(h2_matches), 
            'h3_count': len(h3_matches),
            'h1_titles': h1_matches,
            'h2_titles': h2_matches
        }
    
    def analyze_translations(self):
        """Анализирует переводы"""
        translation_pattern = r'Перевод: (.+?)(?=\n|$)'
        translations = re.findall(translation_pattern, self.content)
        
        # Находим записи без переводов
        entry_pattern = r'^### (.+?)$\n\n(.*?)(?=^###|\n##|\Z)'
        entries_without_translation = []
        
        matches = re.finditer(entry_pattern, self.content, re.MULTILINE | re.DOTALL)
        for match in matches:
            term = match.group(1).strip()
            content = match.group(2)
            if 'Перевод:' not in content:
                entries_without_translation.append(term)
        
        return {
            'total_translations': len(translations),
            'entries_without_translation': entries_without_translation,
            'translation_lengths': [len(t) for t in translations]
        }
    
    def analyze_contexts(self):
        """Анализирует контексты"""
        context_pattern = r'- Раздел `([^`]+)` \(([^)]+)\): (.+?)(?=\n- |\nПеревод:|\n###|\n##|\Z)'
        contexts = re.findall(context_pattern, self.content, re.DOTALL)
        
        sections = [ctx[0] for ctx in contexts]
        section_counts = Counter(sections)
        
        return {
            'total_contexts': len(contexts),
            'unique_sections': len(set(sections)),
            'section_distribution': dict(section_counts.most_common(10)),
            'contexts_per_section': section_counts
        }
    
    def generate_report(self):
        """Генерирует отчет об анализе"""
        if not self.load_file():
            return False
        
        print("=== АНАЛИЗ СТРУКТУРЫ ГЛОССАРИЯ ===\n")
        
        # Общая информация
        lines = self.content.count('\n') + 1
        chars = len(self.content)
        print(f"📄 Общая информация:")
        print(f"   Строк: {lines:,}")
        print(f"   Символов: {chars:,}")
        print(f"   Размер: {chars / 1024:.1f} KB")
        
        # Структура заголовков
        structure = self.analyze_structure()
        print(f"\n📋 Структура заголовков:")
        print(f"   Заголовки 1-го уровня (# ): {structure['h1_count']}")
        print(f"   Заголовки 2-го уровня (##): {structure['h2_count']}")
        print(f"   Заголовки 3-го уровня (###): {structure['h3_count']} (термины)")
        
        if structure['h2_titles']:
            print(f"\n   Разделы (## ):")
            for i, title in enumerate(structure['h2_titles'], 1):
                print(f"   {i:2}. {title}")
        
        # Дубликаты
        duplicates, total_terms = self.find_duplicates()
        print(f"\n🔍 Анализ дубликатов:")
        print(f"   Всего терминов: {total_terms}")
        print(f"   Уникальных терминов: {total_terms - sum(duplicates.values()) + len(duplicates)}")
        print(f"   Дублированных терминов: {len(duplicates)}")
        
        if duplicates:
            print(f"\n   Найденные дубликаты:")
            for term, count in sorted(duplicates.items()):
                print(f"   • {term}: {count} раз")
        
        # Переводы
        translations = self.analyze_translations()
        print(f"\n🌐 Анализ переводов:")
        print(f"   Записей с переводами: {translations['total_translations']}")
        print(f"   Записей без переводов: {len(translations['entries_without_translation'])}")
        
        if translations['entries_without_translation']:
            print(f"   Термины без переводов:")
            for term in translations['entries_without_translation'][:10]:  # Показываем первые 10
                print(f"   • {term}")
            if len(translations['entries_without_translation']) > 10:
                print(f"   ... и еще {len(translations['entries_without_translation']) - 10}")
        
        if translations['translation_lengths']:
            avg_length = sum(translations['translation_lengths']) / len(translations['translation_lengths'])
            print(f"   Средняя длина перевода: {avg_length:.1f} символов")
        
        # Контексты
        contexts = self.analyze_contexts()
        print(f"\n📚 Анализ контекстов:")
        print(f"   Всего контекстных ссылок: {contexts['total_contexts']}")
        print(f"   Уникальных разделов: {contexts['unique_sections']}")
        
        print(f"\n   Топ-10 разделов по количеству ссылок:")
        for section, count in contexts['section_distribution'].items():
            print(f"   • {section}: {count} ссылок")
        
        # Статистика по разделам
        avg_contexts = contexts['total_contexts'] / structure['h3_count'] if structure['h3_count'] > 0 else 0
        print(f"\n   Среднее количество контекстов на термин: {avg_contexts:.1f}")
        
        return True


def main():
    """Главная функция скрипта"""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "Глоссарий.md"
    
    analyzer = GlossaryAnalyzer(file_path)
    
    try:
        analyzer.generate_report()
    except KeyboardInterrupt:
        print("\n\nАнализ прерван пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка при анализе: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
