from pymongo.message import _EMPTY
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
lis = livros.findAll('li', attrs={'class': 'livros'})

headers = {
    'origin': 'https://www.saraiva.com.br',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
}

livrosModel = []

for li in lis:
    pid = li.find('div', attrs={'class': '_lazy'})['pid']
    aux = True
    while aux: #Retry
        try:
            # Requisição para a API
            res = requests.get('https://recs.chaordicsystems.com/v0/pages/recommendations?name=product&source=mobile&productFormat=complete&productId='+pid, headers=headers)
            pprint.pprint(res)
            res = json.loads(str(res.text))
            allInfos = res['middle'][0]['displays'][0]['references'][0] #Separando a parte que me interessa

            # Formatação de array
            try: isbn = allInfos['details']['ISBN'][0]
            except: isbn = ''
            # Verificação para livros iguais
            isbnVerificacao = book.find_one({ 'isbn':  isbn})
            if(isbnVerificacao):
                print('livro cadastrado')
                break
            try: acabamento = allInfos['details']['Acabamento'][0]
            except: acabamento = ''
            
            montandoLivros = {
                "id": allInfos['id'],
                "isbn": isbn,
                "name": allInfos['name'],
                'images': allInfos['images'],
                'description': allInfos['description'],
                'tags': allInfos['tags'],
                'details': {
                    'Acabamento': acabamento
                }   
            }

            pprint.pprint(montandoLivros['name'])
            livrosModel.append(montandoLivros)
            aux = False 
        except:
            aux = True

if(livrosModel):
    x = book.insert_many(livrosModel) #Insert da lista no banco
else:
    print('vazio')

