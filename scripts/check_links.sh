#!/bin/bash

# Скрипт для проверки корректности ссылок в документации
echo "=== Проверка корректности ссылок в документации ==="

# Массив для хранения проблемных ссылок
declare -a broken_links=()
declare -a missing_files=()

# Функция для проверки существования файла
check_file_exists() {
    local file_path=$1
    local base_dir=$2
    local source_file=$3

    # Убираем якоря из пути
    local clean_path=$(echo "$file_path" | sed 's/#.*//')

    # Пропускаем внешние ссылки (http/https)
    if [[ "$clean_path" =~ ^https?:// ]]; then
        return 0
    fi

    # Проверяем абсолютные пути относительно корня проекта
    if [[ "$clean_path" =~ ^/ ]]; then
        full_path="/home/bgs/Henry_Bud_GitHub/doc4microservices$clean_path"
    else
        # Относительные пути относительно файла
        full_path=$(realpath "$base_dir/$clean_path" 2>/dev/null)
    fi

    if [ ! -f "$full_path" ]; then
        missing_files+=("$source_file: $file_path -> $full_path")
        return 1
    fi

    return 0
}

# Поиск всех markdown файлов
echo "Поиск markdown файлов..."
while IFS= read -r -d '' file; do
    echo "Проверяем: $file"

    # Получаем директорию файла
    file_dir=$(dirname "$file")

    # Извлекаем ссылки в формате [text](path)
    while IFS= read -r line; do
        # Пропускаем пустые строки
        [ -z "$line" ] && continue

        # Извлекаем ссылку из скобок
        link=$(echo "$line" | sed -n 's/.*\[.*\](\([^)]*\)).*/\1/p')

        # Пропускаем если ссылка не найдена
        [ -z "$link" ] && continue

        # Проверяем существование файла
        if ! check_file_exists "$link" "$file_dir" "$file"; then
            echo "  ❌ Битая ссылка: $link"
        else
            echo "  ✅ Ссылка OK: $link"
        fi

    done < <(grep -n '\[.*\](' "$file")

done < <(find /home/bgs/Henry_Bud_GitHub/doc4microservices -name "*.md" -print0)

# Выводим результаты
echo ""
echo "=== РЕЗУЛЬТАТЫ ПРОВЕРКИ ==="

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ Все ссылки корректны!"
else
    echo "❌ Найдены проблемные ссылки:"
    printf '%s\n' "${missing_files[@]}"
fi

echo ""
echo "=== Проверка завершена ==="
