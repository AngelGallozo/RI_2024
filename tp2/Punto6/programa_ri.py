from motor_ri import MotorRI
import sys
from os import listdir
from os.path import join, isdir

motor_ri = MotorRI()


# Mostrar los ranking de documentos
def almacenar_ranking(rank):
    
    arch_terms_salida = open("ranking.txt", "x",encoding='utf-8')
    for item in rank:
        arch_terms_salida.write(str(item[0])+" "+str(item[1])+" "+item[2]+"\n")
    arch_terms_salida.close()    
    print("\n\n--------------------------------------------------------")
    print("(*)Arhicvo Ranking creado.\n")
    print("(?)Estructura:id_doc - Score - Path")
    print("--------------------------------------------------------")

def indexar_documentos():
    print("\n\n--------------------------------------------------------")
    dirname = input("Ingrese el path del directorio de los documentos:(si esta en la carpeta local solo el nombre) ")
    if (isdir(dirname)):
        motor_ri.start(dirname)
        print("\n\n+++++++++++++++++++++++++++++++++++")
        print("+ Documentos Indexados con Exito. +")
        print("+++++++++++++++++++++++++++++++++++")
        
        
def realizar_query():
    print("\n\n--------------------------------------------------------")
    query = input("Ingrese la query: ")
    if(len(query)<1 or query.isspace()):
        print("\n\n (!)Error query vacia, no valida.\n\n")
    else:
        resultados = motor_ri.procesar_query(query)
        almacenar_ranking(resultados)
        
        
def main():
    opcion = ""
    while (opcion!="3"):
        print("\n\n------------------------------")
        print("Programa RI - 2023")
        print("------------------------------")
        print("1)_Indexar documentos")
        print("2)_Realizar Query")
        print("3)_SALIR")
        print("------------------------------")
        opcion = input("Elige una opcion: ")
        
        if opcion == "1":
            indexar_documentos()
        elif opcion == "2":
            realizar_query()
        else:
            return None










if __name__ == '__main__':
    main()
    