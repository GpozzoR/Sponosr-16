import requests
from bs4 import BeautifulSoup
website= 'https://www.bcv.org.ve/'
response = requests.get(website)
content = response.text
soup = BeautifulSoup(content,'lxml')
box = soup.find('div',id='dolar')
print(box.find('strong').get_text().replace(",","."))

x='29.500'
print(float(x))