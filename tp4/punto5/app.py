import sys
import os
from os.path import isdir
from sri import SRI
#Instancia el SRI
sist_ri=SRI()


def request_skips():
    print("\n\n\n--------------------------------------------------------\n")
    term = input('Ingrese la Termino: ')
    list_docs,list_bytes = sist_ri.get_skiplist(term)
    if len(list_docs)>0:
        print("\n\n--------------------------------------------------------")
        print(f'SkipList de: {term}')
        for index, doc in enumerate(list_docs):
            print(f'{doc}:{list_bytes[index]}')
    else:
        print("\n(!) Sin Resultados.\n")


def request_query():
    print("\n\n\n--------------------------------------------------------\n")
    query = input('Ingrese la query: ')
    list_docs = sist_ri.query_procesing(query)
    if len(list_docs)>0:
        print("\n\n--------------------------------------------------------")
        print(f'PostingList de: {query}')
        for doc in list_docs:
            print(f'{doc}')
    else:
        print("\n(!) Sin Resultados.\n")

def menu_get_postlits():
    opcion = ""
    while (opcion!="0"):
        print("------------------------------")
        print("1)_Escribir Query")
        print("2)_Pedir Skiplist")
        print("0)_SALIR")
        print("------------------------------")
        opcion = input("Elige una opcion: ")

        if opcion == "1":
            request_query()
        elif opcion =="2":
            pass
            request_skips()
        else:
            return None

def main():
    menu_get_postlits()

if __name__ == '__main__':
    main()