import requests
from collections import Counter
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import re
from bs4 import BeautifulSoup  # Для парсингу HTML

# URL сторінки для завантаження
url = "https://allmarathons-lp-ua.goit.global/"

# Заголовки, які емулюють запит від браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# Функція для завантаження тексту з URL
def fetch_text(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Перевірка на помилки запиту
    return response.text

# Функція для очищення HTML та отримання чистого тексту
def clean_text(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()  # Отримуємо лише текст
    text = re.sub(r'[^\w\s]', '', text.lower())  # Видаляємо всі символи, окрім слів
    words = text.split()
    return words

# Функція для підрахунку частоти слів (Map)
def count_words(words):
    return Counter(words)

# Функція для зведення підсумків (Reduce)
def reduce_counts(counters):
    total_count = Counter()
    for counter in counters:
        total_count.update(counter)
    return total_count

# Функція для візуалізації топ-10 слів
def visualize_top_words(word_counts):
    top_words = word_counts.most_common(10)
    words, counts = zip(*top_words)
    plt.bar(words, counts)
    plt.title("Top 10 Most Common Words")
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.show()

# Основна функція для запуску
def main(url):
    # Завантажуємо текст
    html_text = fetch_text(url)

    # Очищаємо HTML і отримуємо список слів
    words = clean_text(html_text)

    # Розділяємо список слів на частини для паралельної обробки
    chunk_size = len(words) // 4  # Розбиваємо на 4 частини для 4 потоків
    word_chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

    # Використовуємо ThreadPoolExecutor для багатопотокової обробки
    with ThreadPoolExecutor() as executor:
        counters = list(executor.map(count_words, word_chunks))

    # Зводимо підсумки
    total_count = reduce_counts(counters)

    # Візуалізуємо результати
    visualize_top_words(total_count)

if __name__ == "__main__":
    main(url)
