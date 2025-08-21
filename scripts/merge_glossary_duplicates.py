#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для поиска и объединения дублированных записей в файле Глоссарий.md

Автор: AI Assistant
Дата: 2024
"""

import re
import sys
from collections import defaultdict
from pathlib import Path


class GlossaryMerger:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.content = ""
        self.entries = {}
        self.duplicates = defaultdict(list)
        
    def load_file(self):
        """Загружает содержимое файла глоссария"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✓ Файл {self.file_path} успешно загружен")
            return True
        except FileNotFoundError:
            print(f"✗ Файл {self.file_path} не найден")
            return False
        except Exception as e:
            print(f"✗ Ошибка при загрузке файла: {e}")
            return False
    
    def parse_entries(self):
        """Парсит записи глоссария и находит дубликаты"""
        # Регулярное выражение для поиска записей третьего уровня
        pattern = r'^### (.+?)$\n\n(.*?)(?=^###|\n##|\Z)'
        matches = re.finditer(pattern, self.content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            term = match.group(1).strip()
            full_entry = match.group(0)
            start_pos = match.start()
            end_pos = match.end()
            
            # Парсим содержимое записи
            entry_content = match.group(2).strip()
            contexts = []
            translation = ""
            
            # Извлекаем контексты
            context_pattern = r'- Раздел `([^`]+)` \(([^)]+)\): (.+?)(?=\n- |\nПеревод:|\Z)'
            for ctx_match in re.finditer(context_pattern, entry_content, re.DOTALL):
                contexts.append({
                    'section': ctx_match.group(1),
                    'page': ctx_match.group(2),
                    'text': ctx_match.group(3).strip()
                })
            
            # Извлекаем перевод
            translation_match = re.search(r'Перевод: (.+?)(?=\n|$)', entry_content)
            if translation_match:
                translation = translation_match.group(1).strip()
            
            entry_data = {
                'term': term,
                'contexts': contexts,
                'translation': translation,
                'full_entry': full_entry,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'original_content': entry_content
            }
            
            if term in self.entries:
                self.duplicates[term].append(self.entries[term])
                self.duplicates[term].append(entry_data)
            else:
                self.entries[term] = entry_data
        
        print(f"✓ Найдено {len(self.entries)} уникальных терминов")
        print(f"✓ Найдено {len(self.duplicates)} дублированных терминов")
        
        return len(self.duplicates) > 0
    
    def merge_duplicates(self):
        """Объединяет дублированные записи"""
        if not self.duplicates:
            print("Дубликаты не найдены")
            return
        
        print("\nНайденные дубликаты:")
        for term, entries in self.duplicates.items():
            print(f"  - {term}: {len(entries)} записей")
        
        # Сортируем записи по позиции в файле (в обратном порядке для корректного удаления)
        all_entries_to_remove = []
        merged_entries = {}
        
        for term, entries in self.duplicates.items():
            # Объединяем контексты
            all_contexts = []
            all_translations = set()
            
            for entry in entries:
                for context in entry['contexts']:
                    # Проверяем, нет ли уже такого контекста
                    context_key = (context['section'], context['page'], context['text'])
                    if context_key not in [
                        (c['section'], c['page'], c['text']) for c in all_contexts
                    ]:
                        all_contexts.append(context)
                
                if entry['translation']:
                    all_translations.add(entry['translation'])
            
            # Выбираем лучший перевод (самый длинный или первый)
            best_translation = max(all_translations, key=len) if all_translations else ""
            
            # Создаем объединенную запись
            merged_content = f"### {term}\n\nКонтекст:\n\n"
            for context in sorted(all_contexts, key=lambda x: (x['section'], x['page'])):
                merged_content += f"- Раздел `{context['section']}` ({context['page']}): {context['text']}\n"
            
            merged_content += f"\nПеревод: {best_translation}\n\n"
            
            # Сохраняем первую запись как основную, остальные помечаем для удаления
            entries_sorted = sorted(entries, key=lambda x: x['start_pos'])
            main_entry = entries_sorted[0]
            
            merged_entries[term] = {
                'position': main_entry['start_pos'],
                'old_content': main_entry['full_entry'],
                'new_content': merged_content.rstrip() + '\n\n',
                'term': term
            }
            
            # Добавляем остальные записи для удаления
            for entry in entries_sorted[1:]:
                all_entries_to_remove.append({
                    'start': entry['start_pos'],
                    'end': entry['end_pos'],
                    'term': term
                })
        
        return merged_entries, all_entries_to_remove
    
    def apply_changes(self, merged_entries, entries_to_remove):
        """Применяет изменения к содержимому файла"""
        new_content = self.content
        
        # Сначала удаляем дублирующие записи (в обратном порядке позиций)
        for entry in sorted(entries_to_remove, key=lambda x: x['start'], reverse=True):
            print(f"  Удаляем дублирующую запись '{entry['term']}'")
            new_content = new_content[:entry['start']] + new_content[entry['end']:]
        
        # Затем заменяем основные записи на объединенные
        for term, merged in merged_entries.items():
            print(f"  Объединяем запись '{term}'")
            # Находим позицию записи в обновленном контенте
            old_pattern = re.escape(merged['old_content'])
            new_content = re.sub(old_pattern, merged['new_content'], new_content, count=1)
        
        self.content = new_content
        return True
    
    def save_file(self, backup=True):
        """Сохраняет обновленный файл"""
        if backup:
            backup_path = self.file_path.with_suffix('.md.backup')
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    # Сохраняем оригинальное содержимое как бэкап
                    with open(self.file_path, 'r', encoding='utf-8') as orig:
                        f.write(orig.read())
                print(f"✓ Создана резервная копия: {backup_path}")
            except Exception as e:
                print(f"⚠ Не удалось создать резервную копию: {e}")
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            print(f"✓ Файл {self.file_path} успешно обновлен")
            return True
        except Exception as e:
            print(f"✗ Ошибка при сохранении файла: {e}")
            return False
    
    def run(self):
        """Основной метод выполнения скрипта"""
        print("=== Скрипт объединения дубликатов в глоссарии ===\n")
        
        if not self.load_file():
            return False
        
        if not self.parse_entries():
            print("✓ Дубликаты не найдены. Файл не требует изменений.")
            return True
        
        merged_entries, entries_to_remove = self.merge_duplicates()
        
        if not merged_entries:
            print("✓ Нет записей для объединения.")
            return True
        
        print(f"\nПрименяем изменения:")
        if self.apply_changes(merged_entries, entries_to_remove):
            return self.save_file()
        
        return False


def main():
    """Главная функция скрипта"""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "Глоссарий.md"
    
    merger = GlossaryMerger(file_path)
    
    try:
        success = merger.run()
        if success:
            print("\n✓ Скрипт выполнен успешно!")
        else:
            print("\n✗ Скрипт завершился с ошибками.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nСкрипт прерван пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
