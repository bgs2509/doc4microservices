#!/bin/bash
# Скрипт для проверки всех ссылок в документации

echo "=== ПРОВЕРКА ССЫЛОК В ДОКУМЕНТАЦИИ ==="
echo ""

# Находим все markdown файлы
find . -name "*.md" > /tmp/md_files.txt

echo "Найдено markdown файлов: $(cat /tmp/md_files.txt | wc -l)"
echo ""

# Извлекаем все ссылки формата [text](link)
echo "=== ИЗВЛЕКАЕМ ВСЕ ССЫЛКИ ==="
grep -h -n '\[.*\](.*\.md.*\|.*#.*\|\.\/.*\)' $(cat /tmp/md_files.txt) > /tmp/all_links.txt 2>/dev/null || true

if [[ -s /tmp/all_links.txt ]]; then
    echo "Найдено ссылок: $(cat /tmp/all_links.txt | wc -l)"
    echo ""
    echo "=== ПРИМЕРЫ НАЙДЕННЫХ ССЫЛОК ==="
    head -10 /tmp/all_links.txt
else
    echo "Ссылки не найдены или есть проблема с поиском"
fi

echo ""
echo "=== ПРОВЕРЯЕМ ЯКОРИ В README.md ==="
grep -n '^#' README.md | head -10

echo ""
echo "=== ПРОВЕРЯЕМ ЯКОРИ В DOCS/INDEX.md ==="  
grep -n '<a id=' docs/INDEX.md | head -10

echo ""
echo "=== ПРОВЕРЯЕМ ЗАГОЛОВКИ Framework В README.md ==="
grep -n -i 'framework' README.md | grep '^#'
