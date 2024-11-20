from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')  # Працює без графічного інтерфейсу
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')  # Для контейнерів Docker

driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com")
print(driver.title)
driver.quit()

