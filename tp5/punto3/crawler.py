# crawler.py
from constantes import LIMIT_PAGES, URL_AMAZON
from pyvis.network import Network
from html_link_extractor import *
from BTrees.OOBTree import OOBTree
import json

class Crawler():
    
    def __init__(self):
        self.hle = HTMLLinkExtractor()
        self.btree = OOBTree()
        self.count_pages = 0
        self.queue = [[URL_AMAZON, 0]]
        self.error_urls = []
        self.startCrawling()

    # Iniciar el crawling
    def startCrawling(self):
        while self.queue and self.count_pages < LIMIT_PAGES:
            try:
                # Obtengo link y profundidad de la url
                link, depth = self.queue.pop(0)
                if link in self.btree:
                    continue
                print("Cant. de Pags. Recolectadas: {}, URL: {}".format(self.count_pages, link))
                # Obtengo los Links que estan dentro del HTML
                extracted_links = self.hle.extract_links(link)
                
                self.btree[link] = [depth,extracted_links]
            except Exception as e:
                print(e)
                self.error_urls.append(link)
            
            self.count_pages += 1

            links_inside = [[link, depth + 1] for link in extracted_links]
            self.queue.extend(links_inside)  # Unificamos con la cola principal

            if abs(self.count_pages % 30) == 0:  # Persistimos en porciones el btree
                self.persist_btree()

        # Guardamos al finalizar
        self.persist_btree()

    def persist_btree(self):
        dict_btree = {}
        for key in self.btree:
            dict_btree[key] = {}
            dict_btree[key]["depth"] = list(self.btree[key])[0]
            dict_btree[key]["links"] = list(self.btree[key])[1]

        with open("stats_btree.json", "w") as outfile:
            json.dump(dict_btree, outfile)
