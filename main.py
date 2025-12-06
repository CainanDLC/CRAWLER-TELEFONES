'''
Crawler de números de telefone que funciona no site de testes e estudos da Solyd.
Apesar de fazer acompanhando a aula, em todas as funções eu tomei a iniciativa de fazer sozinho e do meu jeito. Portanto, esse código não é idêntico ao apresentado pelo Guilherme Junqueira durante as aulas.
'''

import threading
import requests
import re
from bs4 import BeautifulSoup

dominio = "https://django-anuncios.solyd.com.br"
url = "https://django-anuncios.solyd.com.br/automoveis/"
LINKS = []
TELEFONES = []

# Função para fazer a requisição no site e retonar o texto html
def buscar_automoveis(url):
    try:
        req = requests.get(url)
    except Exception as error:
        print("Erro na requisicao")
        print(error)

    return req.text

#Deixa o texto mais fácil de se trabalhar
def parsing(html_site):
    try:
        soup = BeautifulSoup(html_site, "html.parser")
        return soup
    except Exception as error:
        print("Não foi possível fazer o parsing")
        print(error)

#Procura os anuncio de veículos (o final da URL do site)
def buscar_urls(soup):
    lista_links = []
    links = soup.find("div", class_="ui three doubling link cards")
    links_filho = links.find_all("a", class_= "card")
    for link in links_filho:
        lista_links.append(link["href"])

    return lista_links

#Concatena o dominio do site com a url do anuncio encontrada
def anuncio_veiculo(urls_final):
     for url in urls_final:
        link = dominio + url
        LINKS.append(link)



#Pega somente o texto da descrição dos anúncios e usa REGEX para pegar somente os numeros de telefone
def buscar_telefones(links_anuncios):
    while True:
        try:
         link = links_anuncios.pop(0) # define link como primeiro elemento da lista e o remove, para a próxima thread pegar o elemento seguinte
        except:
            return None  # serve para quando não tiver mais elemento na lista o pop não crashar

        soup = parsing(buscar_automoveis(link))
        descricao = soup.find_all("div",class_="sixteen wide column")[2].p.get_text().strip() # Esse tanto de parâmentro é para ser mais preciso: dentro da div com essa classe, no segundo elemento da lista, na tag <p> e pedindo apenas o texto. Depois um .strip() para tirar os espaços desnecessários
        regex = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9[ \-\.]?\d{4})[ \-\.]?(\d{4})", descricao)
        if regex:
            print(f"Telefone encontrado: {regex}")
            TELEFONES.append(regex)
            salvar_telefones(regex)
            

def salvar_telefones(telefones):
        #como meu buscar_telefones faz com que o resultao de regex seja uma lista de listas de tupla, tive que fazer esse for para percorrer todos as tuplas e garantir que nenhum numero fique de fora do save. caso contrário, se uma descricao tivesse mais de um numero de telefone, somente o primeiro seria salvo
        
        try:
            with open("telefones.csv", "a") as arquivo:
                for telefone in telefones:
                    string_telefone = "{}{}{}\n".format(telefone[0],telefone[1],telefone[2])
                    arquivo.write(string_telefone)
        except Exception as error:
            print("Erro ao salvar")
            print(error)



resposta = buscar_automoveis(url)
 
links = buscar_urls(parsing(resposta))
sites = anuncio_veiculo(links)


#Criando várias threads de uma vez, depois startando e dando join
THREADS = []
for t in range(7):
    t = threading.Thread(target=buscar_telefones, args=(LINKS,))
    THREADS.append(t)

for t in THREADS:
    t.start()

for t in THREADS:
    t.join()



