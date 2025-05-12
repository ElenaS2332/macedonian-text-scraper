import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import os
from typing import List

CATEGORY_URL = "https://makedonskijazik.mk/category/%d0%bf%d0%b8%d1%88%d1%83%d0%b2%d0%b0%d1%9a%d0%b5-%d0%b8-%d1%87%d0%b8%d1%82%d0%b0%d1%9a%d0%b5/%d0%b5%d1%81%d0%b5%d1%98"

def get_article_links(category_url: str) -> List[str]:
    print(f"Scraping category page: {category_url}")
    response = requests.get(category_url)
    if response.status_code != 200:
        print(f"Failed to load category page. Status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if re.match(r'^https://makedonskijazik.mk/\d{4}/\d{2}/', href):
            links.append(href)

    unique_links = list(set(links))  
    print(f"Found {len(unique_links)} article links.")
    return unique_links

def extract_sentences_from_article(url: str) -> List[str]:
    print(f"Scraping article: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to load article: {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    sentences = []

    for p in soup.find_all('p'):
        if p.find('strong'):  
            continue

        text = p.get_text()
        split_sentences = re.split(r'[.!?]', text)
        for sentence in split_sentences:
            cleaned = sentence.strip()
            if cleaned:
                sentences.append(cleaned)

    return sentences

def scrape_all_articles(category_url: str, output_csv: str = "final_sentences.csv"):
    article_links = get_article_links(category_url)
    all_sentences = []

    for link in article_links:
        sentences = extract_sentences_from_article(link)
        all_sentences.extend(sentences)
        time.sleep(1) 
    file_exists = os.path.isfile(output_csv)

    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for sentence in all_sentences:
            writer.writerow([sentence])

    print(f"Done. {len(all_sentences)} sentences saved to '{output_csv}'.")

if __name__ == "__main__":
    scrape_all_articles(CATEGORY_URL)
