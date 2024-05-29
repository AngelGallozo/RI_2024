from constantes import LIMIT_PAGES,URL_AMAZON
from pyvis.network import Network
from html_link_extractor import *
from BTrees.OOBTree import OOBTree
import json

class Crawler():
    
    def __init__(self):
        self.hle = HTMLLinkExtractor()
        self.btree = OOBTree()
        self.pageids = {} #Para la creacion del grafo
        self.count_pages = 0
        self.queue = []
        self.error_urls = []
        self.queue=[[URL_AMAZON,0]]
        self.last_persist = 0
        self.startCrawling()


    # Iniciar el crawling
    def startCrawling(self):
        while self.queue != [] and self.count_pages < LIMIT_PAGES:
            try:
                # Obtengo link y profundidad de la url
                link,depth = self.queue.pop(0)
                print("Cant. de Pags. Recolectadas: {}, URL: {}".format(self.count_pages, link))

                if link in self.btree:
                    continue
                
                # Obtengo los Links que estan dentro del HTML
                extracted_links = self.hle.extract_links(link)
                self.btree[link] = [depth,extracted_links]
            except Exception as e:
                print(e)
                self.error_urls.append(link)
            
            self.count_pages += 1

            links_inside = []
            for link in extracted_links:
                links_inside.append([link, depth+1]) #Agregamos los links y aumentamos su profundidad 
            self.queue.extend(links_inside) # Unificamos con la cola principal

            if abs(self.last_persist - self.count_pages) >= 30: #Persistimos en porciones el btree
                self.persist_btree()
                self.last_persist = self.count_pages

    
    def persist_btree(self):
        dict_btree = {}
        for key in self.btree:
            dict_btree[key] = {}
            dict_btree[key]["depth"] = list(self.btree[key])[0]
            dict_btree[key]["links"] = list(self.btree[key])[1]

        with open("stats_btree.json", "w") as outfile:
            json.dump(dict_btree, outfile)