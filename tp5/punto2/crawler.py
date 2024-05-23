from constantes import LIMIT_SEEDS,LIMIT_PAGES,LIMIT_DEPTH_LOGIC,LIMIT_DEPTH_PHYSICAL,URL_SEEDS
from html_link_extractor import *

class Crawler():
    
    def __init__(self):
        self.seeds = self.getSeeds()
    

    # Obtengo las semillas
    def getSeeds(self):
        html = requests.get(URL_SEEDS,headers={'User-agent':'Mozilla/5.0'})
        soup = BeautifulSoup(html.text, "html5lib")
        table = soup.find_all("table", {'class':"table-topsites"})[0]
        top_links = []

        for tr in table.find_all("tr")[1:]:
            top_links.append(tr.find_all("td")[1].find("a").get('href'))
        return top_links[:LIMIT_SEEDS]
