import requests
from bs4 import BeautifulSoup
import csv
import re
from typing import List

url = "https://makedonskijazik.mk/2015/05/%d0%bf%d0%b8%d1%81%d0%bc%d0%b5%d0%bd%d0%b0-%d1%80%d0%b0%d0%b1%d0%be%d1%82%d0%b0-%d0%b7%d0%b0-%d1%83%d0%bb%d0%b8%d1%86%d0%b0-%d0%be%d0%b4-%d1%81%d0%bb%d0%b0%d0%b2%d0%ba%d0%be-%d1%98.html"

page = requests.get(url)

if page.status_code == 200:
    soup = BeautifulSoup(page.text, 'html.parser')
    p_elements = soup.find_all('p')

    all_sentences: List[str] = []

    for p in p_elements:
        if p.find('strong'):
            continue

        text = p.get_text()
        sentences = re.split(r'[.!?]', text) 

        for s in sentences:
            cleaned = s.strip()
            if cleaned:
                all_sentences.append(cleaned)

    with open('sentences.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Correct sentence']) 
        for sentence in all_sentences:
            writer.writerow([sentence])

    print("Sentences saved to sentences.csv")

else:
    print("Failed to load the page. Status code:", page.status_code)
