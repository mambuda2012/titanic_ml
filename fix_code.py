#!/usr/bin/env python3
import os
import subprocess
import sys

# Список папок, которые нужно полностью игнорировать
EXCLUDE_DIRS = {
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    ".git",
    ".ipynb_checkpoints",
    "__pycache__",
    "build",
    "dist",
}


def run_command(command, description):
    """Выполняет команду и выводит результат с обработкой ошибок"""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,  # Явное определение, чтобы избежать предупреждений линтеров
        )

        if result.returncode != 0:
            print(f"❌ Ошибка в {description}:")
            if result.stderr.strip():
                print(result.stderr.strip())
            return False

        if result.stdout.strip():
            print(result.stdout.strip())
        print(f"✅ {description} выполнен успешно")
        return True

    except Exception as e:
        print(f"❌ Критическая ошибка при выполнении {description}: {e}")
        return False


def format_notebook_inplace(notebook_path):
    """Форматирует ноутбук .ipynb через временную конвертацию в .py"""
    print(f"\n--- Обработка ноутбука: {os.path.basename(notebook_path)} ---")

    base_name, _ = os.path.splitext(notebook_path)
    py_path = base_name + ".py"
    python_bin = sys.executable

    # 1. Конвертация в промежуточный формат py:percent
    conv_cmd = f'{python_bin} -m jupytext --to py:percent "{notebook_path}"'
    if run_command(conv_cmd, "Конвертация в .py"):

        if os.path.exists(py_path):
            # 2. Форматирование кода внутри временного файла
            run_command(f'{python_bin} -m black "{py_path}"', "Black (Jupyter)")
            run_command(f'{python_bin} -m isort "{py_path}"', "isort (Jupyter)")

            # 3. Синхронизация изменений обратно в .ipynb
            update_cmd = f'{python_bin} -m jupytext --to notebook --update "{py_path}"'
            run_command(update_cmd, "Обновление .ipynb")

            # 4. Удаление временного файла
            try:
                os.remove(py_path)
                print(f"🗑️ Временный файл {os.path.basename(py_path)} удалён")
            except Exception as e:
                print(f"⚠️ Не удалось удалить {py_path}: {e}")
        else:
            print(f"❌ Ошибка: временный файл {py_path} не найден")


def main():
    python_bin = sys.executable
    exclude_list = ",".join(EXCLUDE_DIRS)

    print(f"🐍 Интерпретатор: {python_bin}")
    print(f"📁 Игнорируемые папки: {exclude_list}")
    print("-" * 40)

    # Шаг 1: Форматирование всех .py файлов в проекте
    # Используем кавычки для exclude_list, чтобы корректно обработать строку в shell
    black_cmd = f'{python_bin} -m black . --extend-exclude "({exclude_list})"'
    isort_cmd = f'{python_bin} -m isort . --skip-glob "*/{{{exclude_list}}}/*"'

    run_command(black_cmd, "Форматирование всех .py файлов")
    run_command(isort_cmd, "Сортировка импортов во всем проекте")

    # Шаг 2: Поиск и обработка .ipynb файлов
    print("\n🔎 Поиск ноутбуков .ipynb...")
    found_notebooks = False

    for root, dirs, files in os.walk("."):
        # Фильтруем папки на лету, чтобы os.walk в них не заходил
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]

        for file in files:
            if file.endswith(".ipynb"):
                found_notebooks = True
                full_path = os.path.join(root, file)
                format_notebook_inplace(full_path)

    if not found_notebooks:
        print("ℹ️ Ноутбуки не найдены.")

    print("\n" + "=" * 40)
    print("🎉 Форматирование завершено!")
    print("=" * 40)


if __name__ == "__main__":
    main()
