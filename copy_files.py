import asyncio
import os
import shutil
import logging
from pathlib import Path
import aiofiles
import argparse

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Функція для створення підкаталогів за розширенням
def create_output_folder_structure(output_folder, file_extension):
    # Створюємо підпапку для кожного розширення
    ext_folder = output_folder / file_extension.lstrip('.')
    ext_folder.mkdir(parents=True, exist_ok=True)
    return ext_folder

# Асинхронна функція для копіювання файлів
async def copy_file(file_path, output_folder):
    try:
        # Отримуємо розширення файлу
        file_extension = file_path.suffix
        # Створюємо підкаталог за розширенням файлу
        dest_folder = create_output_folder_structure(output_folder, file_extension)
        dest_file_path = dest_folder / file_path.name

        # Копіюємо файл асинхронно
        async with aiofiles.open(file_path, mode='rb') as src_file:
            data = await src_file.read()
            async with aiofiles.open(dest_file_path, mode='wb') as dest_file:
                await dest_file.write(data)
        
        logging.info(f'Файл {file_path.name} успішно скопійовано до {dest_file_path}')
    except Exception as e:
        logging.error(f'Помилка при копіюванні файлу {file_path.name}: {e}')

# Асинхронна функція для читання папки
async def read_folder(source_folder, output_folder):
    try:
        # Перевіряємо, чи існує вихідна папка
        if not source_folder.exists():
            logging.error(f'Вихідна папка {source_folder} не існує.')
            return

        # Проходимо всі файли в папці та підпапках
        tasks = []
        async for file_path in async_walk(source_folder):
            if file_path.is_file():
                tasks.append(copy_file(file_path, output_folder))
        
        # Чекаємо завершення всіх задач
        await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(f'Помилка при читанні папки {source_folder}: {e}')

# Асинхронна генератор функція для рекурсивного обходу папки
async def async_walk(folder):
    for file in folder.iterdir():
        if file.is_dir():
            async for child in async_walk(file):
                yield child
        else:
            yield file

# Головна функція для запуску
async def main():
    # Обробка аргументів командного рядка
    parser = argparse.ArgumentParser(description="Асинхронний скрипт для сортування файлів за розширеннями")
    parser.add_argument("source_folder", type=str, help="Шлях до вихідної папки")
    parser.add_argument("output_folder", type=str, help="Шлях до цільової папки")
    
    args = parser.parse_args()
    
    source_folder = Path(args.source_folder)
    output_folder = Path(args.output_folder)

    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    # Запуск асинхронної обробки
    await read_folder(source_folder, output_folder)

# Запуск скрипта
if __name__ == "__main__":
    asyncio.run(main())
