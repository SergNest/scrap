import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/129.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7"
}
url = 'https://bpower.com.ua'


def get_products():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('article', class_='product item')

    product_list = []

    for product in products:
        product_data = {
            'title': product['data-title'],
            'price': product['data-price'],
            'link': product['data-href'],
            'image': product.find('img')['src'],
            'stock_status': product.find('div', class_='stock-status').text.strip(),
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        product_list.append(product_data)

    return product_list


# Оновлення файлу з продуктами
def update_json_file(new_data):
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    new_products_count = 0
    updated_products_count = 0
    updated_data = []

    updated_titles = []
    new_products_titles = []

    # Перевірка та оновлення продуктів
    for new_product in new_data:
        matched_product = next((prod for prod in existing_data if prod['title'] == new_product['title']), None)

        if matched_product:
            if matched_product['stock_status'] != new_product['stock_status'] or matched_product['price'] != new_product['price']:
                matched_product['stock_status'] = new_product['stock_status']
                matched_product['price'] = new_product['price']
                matched_product['date'] = new_product['date']
                updated_products_count += 1
                updated_titles.append(matched_product['title'])
            updated_data.append(matched_product)
        else:
            updated_data.append(new_product)  # Додаємо новий товар
            new_products_titles.append(new_product['title'])
            new_products_count += 1

    # Видалення товарів, яких більше немає в нових даних
    titles_in_new_data = {prod['title'] for prod in new_data}
    deleted_products = [prod for prod in existing_data if prod['title'] not in titles_in_new_data]
    deleted_titles = [prod['title'] for prod in deleted_products]
    deleted_products_count = len(deleted_titles)
    updated_data = [prod for prod in updated_data if prod['title'] in titles_in_new_data]

    # Оновлення файлу, якщо є зміни
    if existing_data != updated_data or updated_products_count > 0:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        # Лог змін
        changes_log = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updated_titles': updated_titles,
            'deleted_titles': deleted_titles,
            'new_products_titles': new_products_titles
        }

        # Перезаписуємо changes_log.json кожного разу
        with open('changes_log.json', 'w', encoding='utf-8') as f:
            json.dump(changes_log, f, ensure_ascii=False, indent=4)

        print(f"Файл оновлено: {new_products_count} нових, {updated_products_count} змінених, {deleted_products_count} видалених.")
    else:
        print("Немає змін.")


# Отримання товарів "в наявності"
def get_in_stock_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Фільтруємо товари, залишаючи тільки ті, що "в наявності"
        in_stock_products = [product for product in data if product['stock_status'] == "В наявності"]
        return in_stock_products
    except (FileNotFoundError, json.JSONDecodeError):
        print("Файл не знайдено або порожній.")
        return []
# Функція для отримання товарів з останніми змінами у заданому форматі


def get_changed_products():
    try:
        # Зчитуємо останні зміни з changes_log.json
        with open('changes_log.json', 'r', encoding='utf-8') as log_file:
            last_change = json.load(log_file)

        # Зчитуємо поточний список товарів з products.json
        with open('products.json', 'r', encoding='utf-8') as products_file:
            products_data = json.load(products_file)

        # Вибираємо тільки ті товари, які були змінені або додані
        changed_products = [
            product for product in products_data
            if product['title'] in last_change['updated_titles'] or
               product['title'] in last_change['new_products_titles']
        ]

        # Формуємо нову назву для changes_log.json з поточною датою і часом
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_log_filename = f"changes_log_{timestamp}.json"

        # Перейменовуємо файл
        os.rename('changes_log.json', new_log_filename)

        return changed_products

    except (FileNotFoundError, json.JSONDecodeError) as e:
        # print("Помилка зчитування файлів:", e)
        return []


def main2():
    new_data = get_products()
    update_json_file(new_data)
    return get_changed_products()


def main():
    new_data = get_products()
    update_json_file(new_data)
    changed_products = get_changed_products()
    print(json.dumps(changed_products, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    main()
