import sys
import os
from os import listdir
from os.path import join, isdir

    
def main():
    if len(sys.argv) < 3:
        print('Es necesario pasar como argumentos: archivo1 y archivo 2.')        
        sys.exit(0)
    file_one = sys.argv[1]
    file_two = sys.argv[2]
    if (os.path.exists(file_one) and os.path.exists(file_two)):
        # Leo los archivos y giardo sus lineas
        archivo_one = open(file_one,'r',encoding='iso-8859-1')
        lineas_archivo_one = archivo_one.readlines()
        archivo_one.close()
        
        archivo_two = open(file_two,'r',encoding='iso-8859-1')
        lineas_archivo_two = archivo_two.readlines()
        archivo_two.close()

        if len(lineas_archivo_one) != len(lineas_archivo_two):
            print("ERROR!!!! : Los archivos no tienen la misma cantidad de lineas.")
        else:
            indice = 0
            diferencias=0
            for line in lineas_archivo_one:
                num_line_one,lang_one = line.split()
                num_line_two,lang_two = lineas_archivo_two[indice].split()

                if(lang_one != lang_two):
                    print("Oracion: ["+str(indice+1)+"] Lang_1: "+lang_one+" Lang_2: "+lang_two)
                    diferencias+=1
                
                indice += 1
            
            print(f'Cantidad de Diferencias: {diferencias}')
            print(f'De un total de {indice} casos un {round(diferencias/indice*100,2)}% tuvo clasificacion diferente.')
                
if __name__ == '__main__':
    main()
    
