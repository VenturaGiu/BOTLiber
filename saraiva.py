import requests
import json
import time
import pprint
from pymongo import MongoClient
from bs4 import BeautifulSoup

myclient = MongoClient("mongodb://localhost:27017/")
liber = myclient["liber"]
book = liber["book"]

content = requests.get('https://www.saraiva.com.br/livros/administracao?promo_id=administracao&promo_name=administracao-menuexp-livros&promo_creative=link&promo_position=slot8').content
site = BeautifulSoup(content, 'html.parser')
livros = site.find('div', attrs={'class': 'vitrine', 'class': 'prateleira'})
ul = livros.find('ul')
lis = ul.findAll('li', attrs={'class': 'livros'})

headers = {
    'origin': 'https://www.saraiva.com.br',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
}

livrosModel = []

a = 1

print(len(lis))

for li in lis:
    pid = li.find('div', attrs={'class': '_lazy'})['pid']
    url = li.find('a', attrs={'class': 'productImage'})['href']
    url = url[8:len(url)]
    try:
        res = requests.get('https://recs.chaordicsystems.com/v0/pages/recommendations?name=product&source=desktop&deviceId=ff5bc017-797b-4bae-8a68-1742d87e01fe&productFormat=complete&url='+url+'&productId='+pid+'', headers=headers)
        pprint.pprint(res)
        res = json.loads(str(res.text))
        if(len(res['middle']) == 0 ):
            continue
        print(len(res['middle']))
        allInfos = res['middle'][0]['displays'][0]['references'][0]
        print(a)
        a += 1

        try: acabamento = allInfos['details']['Acabamento'][0]
        except: acabamento = ''

        montandoLivros = {
            "id": allInfos['id'],
            "name": allInfos['name'],
            'images': allInfos['images'],
            'description': allInfos['description'],
            'tags': allInfos['tags'],
            'details': {
                'Acabamento': acabamento
            }   
        }
        pprint.pprint(montandoLivros)
        livrosModel.append(montandoLivros)
    except NameError:
        print(NameError)

x = book.insert(livrosModel)
