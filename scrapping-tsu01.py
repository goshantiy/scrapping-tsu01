from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import random
import schedule
import time
import re

url = 'https://ria.ru/lenta/'
keywords = ['SpaceX', 'ИИ', 'AI', 'инопланетяне', 'пришельцы', 'космос', '3D', 'космический', '3Д', 'ученый', 'учёный', 'ученые', 'Microsoft','Apple', 'США']
proxies_file_path = 'proxies.txt'
agents_file_path = 'user_agents.txt'
output_file = 'matched_articles.txt'
start_time = datetime.now()
max_duration_hours = 24
existing_urls = set()

def read_lines_from_file(file_path):
    proxies = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                proxies.append(line.strip())
    except IOError:
     print(f"Failed to open or read the file: {file_path}, please specify name to proxies.txt")
    return proxies

proxies = read_lines_from_file(proxies_file_path)
agents = read_lines_from_file(agents_file_path)

def schedule_scrap_site(url):
    if(len(proxies)&len(agents)):
        for proxy in proxies:
            try:
                headers = {'User-Agent':random.choice(agents)}
                print(headers)
                response = requests.get(url, proxies={'http': proxy, 'https': proxy}, headers=headers, timeout=5)
                print('Success proxy request')
                soup = BeautifulSoup(response.content, "html.parser")
                articles = soup.find_all("div", class_="list-item")
                for article in articles:
                    content = article.find("div", class_="list-item__content")
                    if content:
                        title_element = content.find("a", class_="list-item__title color-font-hover-only")
                        if title_element:
                            title = title_element.text.strip()
                            article_url = title_element["href"]
                        if article_url in existing_urls:
                            continue
                        if any(re.search(r'\b{}\b'.format(re.escape(keyword)), title, flags=re.IGNORECASE) for keyword in keywords):
                            with open(output_file, "a", encoding="utf-8") as file:
                                file.write("Title: {}\n".format(title))
                                file.write("URL: {}\n".format(article_url))
                                file.write("\n")
                                existing_urls.add(article_url)
                break
            except requests.exceptions.RequestException:
                print(f"Failed to connect using proxy: {proxy}")

schedule_scrap_site(url)
schedule.every(15).minutes.do(schedule_scrap_site, url)

while True:
    elapsed_time = datetime.now() - start_time
    if elapsed_time.total_seconds() / 3600 >= max_duration_hours:
        break
    schedule.run_pending()
    time.sleep(1000)
