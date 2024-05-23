from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

class HTMLLinkExtractor():
    def __init__(self):
        '''self.proxies = {
            "http"  : "http://proxy.unlu.edu.ar",
            "https" : "https://proxy.unlu.edu.ar",
        }'''
    
    def is_href(self, href):
        return href is not None and not href.startswith("#")

    def is_absolute_href(self, href):
        return bool(urlparse(href).netloc) # Si existe valor si es path absoluto

    def extract_links(self, url):
        
        html_file = requests.get(url,headers={'User-agent':'Mozilla/5.0'})
        parsed_uri = urlparse(url)
        host = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        soup = BeautifulSoup(html_file.text, "html.parser")
        links = []
        for link in soup.findAll('a'):
            href = link.get('href')
            if self.is_href(href):
                if self.is_absolute_href(href):
                    links.append(href)
                else:
                    links.append(host+href)
        return links