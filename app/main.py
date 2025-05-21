import requests
from bs4 import BeautifulSoup
import re
import csv
import os
from typing import List

WIKI_URL = "https://mk.wikipedia.org/wiki/%D0%98%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0_%D0%BD%D0%B0_%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D1%81%D0%BA%D0%B0_%D0%BE%D0%BF%D1%80%D0%B5%D0%BC%D0%B0"
OUTPUT_CSV = "wikipedia.csv"

def clean_text(text: str) -> str:
    # Remove references like [1], [12][13]
    return re.sub(r'\[\d+(?:\]\[\d+)*\]', '', text).strip()

def is_valid_sentence(sentence: str) -> bool:
    words = sentence.strip().split()
    if len(words) < 5:
        return False
    if all(re.fullmatch(r'\d+', word) for word in words):
        return False
    return True

def extract_sentences_from_wikipedia(url: str) -> List[str]:
    print(f"Scraping Wikipedia article: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to load article: {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    sentences = []

    for p in soup.find_all('p'):
        if p.find('strong'):
            continue

        text = clean_text(p.get_text())
        split_sentences = re.split(r'[.!?]', text)

        for sentence in split_sentences:
            cleaned = sentence.strip()
            if cleaned and is_valid_sentence(cleaned):
                sentences.append(cleaned)

    return sentences

def save_sentences_to_csv(sentences: List[str], output_csv: str):
    file_exists = os.path.isfile(output_csv)

    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for sentence in sentences:
            writer.writerow([sentence])

    print(f"{len(sentences)} sentences saved to '{output_csv}'.")

if __name__ == "__main__":
    sentences = extract_sentences_from_wikipedia(WIKI_URL)
    save_sentences_to_csv(sentences, OUTPUT_CSV)
