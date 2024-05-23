import sys
import os
from os.path import isdir
from sri import SRI
#Instancia el SRI
sist_ri=SRI()

def request_query():
    print("\n\n\n--------------------------------------------------------\n")
    query = input('Ingrese la query: ')
    list_docs = sist_ri.query_procesing(query)
    if len(list_docs)>0:
        print("\n\n--------------------------------------------------------")
        print(f'PostingList: {query}')
        for doc in list_docs:
            print(f'{doc}')
    else:
        print("\n(!)Terminos inexsitentes.\n")

def menu_get_postlits():
    opcion = ""
    while (opcion!="0"):
        print("------------------------------")
        print("1)_Escribir Query")
        print("0)_SALIR")
        print("------------------------------")
        opcion = input("Elige una opcion: ")

        if opcion == "1":
            request_query()
        else:
            return None

def main():
    sist_ri.start()
    menu_get_postlits()

if __name__ == '__main__':
    main()



    