import sys
import os
from os.path import isdir
from sri import SRI
#Instancia el SRI
sist_ri=SRI()

def mostrar_postinglist():
    list_docs,list_freqs,token = sist_ri.get_posting_list()
    if len(list_docs)>0:
        print("\n\n--------------------------------------------------------")
        print(f'PostingList de: {token}')
        for index, doc in enumerate(list_docs):
            print(f'{doc}:{list_freqs[index]}')
                    

def indexar_documentos():
    print("\n\n--------------------------------------------------------")
    dirname = input("Ingrese el path del directorio de los documentos:(si esta en la carpeta local solo el nombre):")
    if (isdir(dirname)):
        sist_ri.start(dirname)
        print("\n\n+++++++++++++++++++++++++++++++++++")
        print("+ Documentos Indexados con Exito. +")
        print("+++++++++++++++++++++++++++++++++++")
    else:
        print("\n\n (!)Error Directorio NO Valido.\n\n")


def menu_get_postlits():
    opcion = ""
    while (opcion!="0"):
        print("------------------------------")
        print("1)_Indexar & Almacenar Postings")
        print("2)_Mostrar PostingsList de un Termino")
        print("0)_SALIR")
        print("------------------------------")
        opcion = input("Elige una opcion: ")

        if opcion == "1":
            indexar_documentos()
        elif opcion == "2":
            mostrar_postinglist()
        else:
            return None

def main():
    menu_get_postlits()

if __name__ == '__main__':
    main()