import sys
import numpy as np
import os
from os import listdir
from os.path import join, isdir
from scipy.stats import pearsonr

list_pairs={}
index_pair = 0

def save_pairs_letters(file):
    global index_pair
    for lines_file in file:
        lines = lines_file.replace("\n", "").title().lower()
        for index in range(0, len(lines)):
            pair = lines[index:index+2]
            if (not (pair in list_pairs)) and (pair != ' ') and (pair !=' .')and (pair !='. '):
                list_pairs[pair]= index_pair
                index_pair += 1

def save_pairs_frec_files(long_array,file):
    result = np.zeros(long_array,dtype=int)
    for lines_file in file:
        lines = lines_file.replace("\n", "").title().lower()
        for index in range(0, len(lines)):
            pair_test = lines[index:index+2]
            for pair,index in list_pairs.items():
                if pair == pair_test:
                    result[index] +=1
    return np.array(result)

def save_test_frec(long_array,lines_file):
    result = np.zeros(long_array,dtype=int)
    lines = lines_file.replace("\n", "").title().lower()
    for index in range(0, len(lines)):
        pair_test = lines[index:index+2]
        for pair,index in list_pairs.items():
            if pair == pair_test:
                result[index] +=1
    return np.array(result)




def main():
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumentos: directorio_entrenamiento y archivo de testeo.')        
        sys.exit(0)
    dir_entrenamiento = sys.argv[1]
    file_test = sys.argv[2]
    train_letters_frec = {}
    test_letters_frec =[]
    # Guardo todos los pares de letras en los archivos de entrenamiento
    if (isdir(dir_entrenamiento)):
        global list_pairs
        print(f"Generando lista de pares...")
        for filename in listdir(dir_entrenamiento): 
            filepath = join(dir_entrenamiento, filename)
            with open(filepath,'r',encoding='iso-8859-1') as f:       
                save_pairs_letters(f)
        
    # Guardo la frecuencia de los pares de letras en los archivos de entrenamiento por idioma
        for filename in listdir(dir_entrenamiento):
            language = filename  
            filepath = join(dir_entrenamiento, filename)
            print(f"Procesando archivo: {language}")
            with open(filepath,'r',encoding='iso-8859-1') as f:
                train_letters_frec[language] = save_pairs_frec_files(len(list_pairs),f)
    
    
    # Guardo la frecuencia de las letras del archivo de prueba
    if (os.path.exists(file_test)):
        arch_salida = open(f'5b_resultados.txt', "x",encoding='utf-8')
        with open(file_test,'r',encoding='iso-8859-1') as f:
            print(f"Procesando archivo de Testeo.")
            sentence = 0
            for line in f:
                sentence += 1
                test_letters_frec = save_test_frec(len(list_pairs),line)
                correl_actual = -1
                language_detected = ''
                #Verificamos mediante correlacion si el idioma es el mismo
                for language,list_pairs_lang in train_letters_frec.items(): 
                    correlations = np.corrcoef(test_letters_frec,train_letters_frec[language])
                    pearsoncoef = correlations[0,1]
                    if  correl_actual < pearsoncoef:
                        correl_actual = pearsoncoef
                        language_detected = language
                
                # Guardamos resultados de cada linea
                arch_salida.write(str(sentence)+' '+language_detected+"\n")
            
        arch_salida.close()
        print(f"Archivo resultado generado.")
                
if __name__ == '__main__':
    main()