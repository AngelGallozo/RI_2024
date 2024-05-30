from constantes import LIMIT_SEEDS,LIMIT_PAGES,LIMIT_PAGES_SITE,LIMIT_DEPTH_LOGIC,LIMIT_DEPTH_PHYSICAL,URL_SEEDS
from html_link_extractor import *
from BTrees.OOBTree import OOBTree
from pyvis.network import Network
import json

class Crawler():
    
    def __init__(self):
        self.hle = HTMLLinkExtractor()
        self.btree = OOBTree()
        self.pageids = {} #Para la creacion del grafo
        self.count_pages = 0
        self.last_persist = 0
        self.seeds = self.getSeeds()
        self.queue = []
        self.crawling_order=[]
        self.error_urls = []
        # Preparando la cola con los links de semillas
        for seed in self.seeds:
            # Almaceno el link y una profundidad default de 0
            self.queue.append([seed,0])
        
        self.startCrawling()


    # Obtengo las semillas
    def getSeeds(self):
        html = requests.get(URL_SEEDS,headers={'User-agent':'Mozilla/5.0'})
        soup = BeautifulSoup(html.text, "html5lib")
        table = soup.find_all("table", {'class':"table-topsites"})[0]
        top_links = []

        for tr in table.find_all("tr")[1:]:
            top_links.append(tr.find_all("td")[1].find("a").get('href'))
        return top_links[:LIMIT_SEEDS]

    # Retorna la profundidad fisica de la url
    def getPhysicalDepth(self, url):
        path = urlparse(url).path
        return path.count("/")


    # Iniciar el crawling
    def startCrawling(self):
        while self.queue != [] and self.count_pages < LIMIT_PAGES:
            try:
                # Obtengo link y profundidad de la url
                link,depth = self.queue.pop(0)
                print("Cant. de Pags. Recolectadas: {}, URL: {}".format(self.count_pages, link))
                
                if depth > LIMIT_DEPTH_LOGIC: # Si la profundidad logica es superior skipear
                    continue

                if self.getPhysicalDepth(link) > LIMIT_DEPTH_PHYSICAL: # Si la profundidad fisica es superior skipear
                    continue

                if link in self.btree:
                    continue
                
                # Obtengo los Links que estan dentro del HTML
                extracted_links = self.hle.extract_links(link,limit=LIMIT_PAGES_SITE)
                self.btree[link] = extracted_links
                self.crawling_order.append(link)

            except:
                self.error_urls.append(link)
            
            self.count_pages += 1

            links_inside = []
            for link in extracted_links:
                links_inside.append([link, depth+1]) #Agregamos los links y aumentamos su profundidad 
            self.queue.extend(links_inside) # Unificamos con la cola principal

            if abs(self.last_persist - self.count_pages) >= 30: #Persistimos en porciones el btree
                self.persist_btree()
                self.last_persist = self.count_pages
                self.persist_crawl_order()
    
    def persist_btree(self):
        dict_btree = {}
        for key in self.btree:
            dict_btree[key] = list(self.btree[key])

        with open("btree.json", "w") as outfile:
            json.dump(dict_btree, outfile)
    
    def persist_crawl_order(self):
        with open("crawling_order.json", "w") as outfile:
            json.dump(self.crawling_order, outfile)