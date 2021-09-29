from pymongo.message import _EMPTY
import requests
import json
import time
import pprint
from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium import webdriver
import variables
import conn

for urlAdm in variables.urlAdministracao:

    content = requests.get(variables.urlAdministracao[urlAdm]).content
    site = BeautifulSoup(content, 'html.parser')
    livros = site.find('div', attrs={'class': 'vitrine', 'class': 'prateleira'})
    lis = livros.findAll('li', attrs={'class': 'livros'})

    livrosModel = []
    estoqueModel = []

    for li in lis:
        pid = li.find('div', attrs={'class': '_lazy'})['pid']
        esgotado = li.find('div', attrs={'class': 'box-esgotado'})
        if(esgotado == None):
            aux = True
            retry = 0
            while aux and retry < 6:
                try:
                    res = requests.get('https://recs.chaordicsystems.com/v0/pages/recommendations?name=product&source=mobile&productFormat=complete&productId='+pid, headers=variables.headers)
                    pprint.pprint(res)
                    res = json.loads(str(res.text))
                    allInfos = res['middle'][0]['displays'][0]['references'][0] #Separando a parte que me interessa

                    # Formatação de array
                    try: isbn = allInfos['details']['ISBN'][0]
                    except: isbn = ''

                    # Verificação para livros iguais
                    isbnVerificacao = conn.book.find_one({ 'isbn':  isbn})
                    if(isbnVerificacao):
                        print('livro cadastrado')
                        break

                    try: acabamento = allInfos['details']['Acabamento'][0]
                    except: acabamento = ''
                    try: anoEdicao = allInfos['details']['Ano da edição'][0]
                    except: anoEdicao = ''
                    try: autor = allInfos['details']['Autor'][0]
                    except: autor = ''
                    try: foraDeLinha = allInfos['details']['Fora de Linha'][0]
                    except: foraDeLinha = ''
                    try: formatoLivroDigital = allInfos['details']['Formato Livro Digital'][0]
                    except: formatoLivroDigital = ''
                    try: idioma = allInfos['details']['Idioma'][0]
                    except: idioma = ''
                    try:  numeroEdicao = allInfos['details']['Número da edição'][0]
                    except: numeroEdicao = ''
                    try:  numeroPaginas = allInfos['details']['Número de Páginas'][0]
                    except: numeroPaginas = ''
                    try:  paisOrigim = allInfos['details']['País de Origem'][0]
                    except: paisOrigim = ''

                    try:  #ajuste das categorias
                        tags = allInfos['tags']
                        categoria = tags[1]
                        subCategoria = tags[2]
                            
                    except: 
                        paisOrigim = ''
                    
                    montandoLivros = {
                        "id": allInfos['id'],
                        "isbn": isbn,
                        "nome": allInfos['name'],
                        'imagens': allInfos['images'],
                        'descricao': allInfos['description'],
                        'categorias': {
                            'categoria': categoria,
                            'subCategoria': subCategoria,
                        },
                        'detalhes': {
                            'acabamento': acabamento,
                            'anoEdicao': anoEdicao,
                            'autor': autor,
                            'foraDeLinha': foraDeLinha,
                            'formatoLivroDigital': formatoLivroDigital,
                            'idioma': idioma,
                            'numeroEdicao': numeroEdicao,
                            'numeroPaginas': numeroPaginas,
                            'paisOrigim': paisOrigim,
                            'marca': allInfos['details']['brand']
                        }   
                    }

                    print(montandoLivros["nome"])
                    livrosModel.append(montandoLivros)
                    aux = False 
                except:
                    aux = True
                    retry += 1
        else:
            psku = li.find('div', attrs={'class': '_lazy'})['psku']
            retry = 0
            aux = True
            while aux and retry < 6:
                try:
                    resp = requests.get('https://www.saraiva.com.br/produto/sku/'+psku, headers=variables.headers)
                    pprint.pprint(resp)
                    resp = json.loads(str(resp.text))

                    montandoEstoques = {
                        'idProduto': resp[0]['IdProduct'],
                        'isbn': resp[0]['Ean'],
                        'nome': resp[0]['Name'],
                        'reference': resp[0]['Reference']
                    }

                    estoqueModel.append(montandoEstoques)
                    
                    aux = False 
                except:
                    aux = True
                    retry += 1

    print(estoqueModel)

    if(livrosModel):
        x = conn.book.insert_many(livrosModel) #Insert da lista book
    else:
        print('livrosModel vazia')
        
    if(estoqueModel):
        y = conn.stock.insert_many(estoqueModel) #Insert na lista stock
    else:
        print('estoqueModel vazia')
