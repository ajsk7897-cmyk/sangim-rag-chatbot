import requests
from bs4 import BeautifulSoup
import re

url = "https://www.kimchang.com/ko/insights/index.kc?sch_keyword=부동산"
res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(res.text, 'html.parser')

results = []
for div in soup.find_all('div', class_='tit'):
    results.append(div.text.strip())
for p in soup.find_all('p', class_='desc'):
    results.append(p.text.strip())

# if none, try to find text directly
if not results:
    for a in soup.find_all('a'):
        text = a.text.strip()
        if '부동산' in text or len(text) > 20:
            results.append(text)

open('kim_parsed2.txt', 'w', encoding='utf-8').write("\n".join(results[:50]))
