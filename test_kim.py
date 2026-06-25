import requests
from bs4 import BeautifulSoup
import re

url = "https://www.kimchang.com/ko/insights/index.kc?sch_keyword=부동산"
res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html = res.text

soup = BeautifulSoup(html, 'html.parser')
items = soup.select('.list-item, li, a')
results = []
for a in soup.select('a'):
    href = a.get('href', '')
    if 'idx=' in href:
        title = a.text.strip()
        if title:
            results.append(f"Title: {title}\nLink: {href}")

open('kim_parsed.txt', 'w', encoding='utf-8').write("\n\n".join(results[:10]))
