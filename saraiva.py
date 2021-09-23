import requests
import json
from bs4 import BeautifulSoup

content = requests.get('https://www.saraiva.com.br/livros/administracao?promo_id=administracao&promo_name=administracao-menuexp-livros&promo_creative=link&promo_position=slot8').content
site = BeautifulSoup(content, 'html.parser')
livros = site.find('div', attrs={'class': 'vitrine', 'class': 'prateleira'})
ul = livros.find('ul')
lis = ul.findAll('li', attrs={'class': 'livros'})

headers = {
    'origin': 'https://www.saraiva.com.br',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
}



for li in lis:
    pid = li.find('div', attrs={'class': '_lazy'})['pid']
    url = li.find('a', attrs={'class': 'productImage'})['href']
    url = url[8:len(url)]
    res = requests.get('https://recs.chaordicsystems.com/v0/pages/recommendations?name=product&source=desktop&deviceId=ff5bc017-797b-4bae-8a68-1742d87e01fe&productFormat=complete&url='+url+'&productId='+pid+'', headers=headers)
    res = json.loads(str(res.text))
    print(res['middle'][0]['displays'][0]['references'][0])
    # print(pid)
    # print(url)