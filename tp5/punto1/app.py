import sys
from html_link_extractor import *

def main():
    try:
        url = sys.argv[1]
    except:
        print("Ingrese una URL por parámetro")
    
    hle = HTMLLinkExtractor()
    links = hle.extract_links(url)

    for link in links:
        print(link)
    

if __name__ == '__main__':
    main()