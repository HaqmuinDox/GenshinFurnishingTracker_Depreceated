import requests
from bs4 import BeautifulSoup

url = 'https://genshin-impact.fandom.com/wiki/Category:Gift_Sets'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

headings = soup.find_all('h2')
links = soup.find_all('a', href=True)

for heading in headings:
    print("Heading:", heading.get_text())

print("Links:")

for link in links:
    if link['href'].startswith('/wiki/') and link['href'] != '/wiki/':
        print("Link:", link['href'])
    elif link['href'] == '/wiki/':
        break
