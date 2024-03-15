import sys
import numpy as np
import os
from os import listdir
from os.path import join, isdir
from scipy.stats import pearsonr

list_letters=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

def save_letters_frec(file):
    result = np.zeros(26,dtype=int)
    for lines_file in file:
        lines = lines_file.replace("\n", "").title().lower()
        for char in lines:
            for key,letter in enumerate(list_letters):
                if letter == char:
                    result[key] +=1
    return result
    

def main():
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumentos: directorio_entrenamiento y archivo de testeo.')        
        sys.exit(0)
    dir_entrenamiento = sys.argv[1]
    file_test = sys.argv[2]
    train_letters_frec = {}
    test_letters_frec =[]
    # Guardo la frecuencia de las letras en los archivos de entrenamiento
    if (isdir(dir_entrenamiento)):
        for filename in listdir(dir_entrenamiento):
            language = filename  
            filepath = join(dir_entrenamiento, filename)
            with open(filepath,'r',encoding='iso-8859-1') as f:
                train_letters_frec[language] = save_letters_frec(f)
    
    # Guardo la frecuencia de las letras del archivo de prueba
    if (os.path.exists(file_test)):
        with open(file_test,'r',encoding='iso-8859-1') as f:
            arch_salida = open(f'5a_resultados.txt', "x",encoding='utf-8')
            sentence = 0
            for line in f:
                sentence += 1
                test_letters_frec = save_letters_frec(line)
                correl_actual = -1
                language_detected = ''
                #Verificamos mediante correlacion si el idioma es el mismo
                for language,list_letters in train_letters_frec.items(): 
                    correlations = np.corrcoef(test_letters_frec,train_letters_frec[language])
                    pearsoncoef = correlations[0,1]
                    if  correl_actual < pearsoncoef:
                        correl_actual = pearsoncoef
                        language_detected = language
                
                # Guardamos resultados de cada linea
                arch_salida.write(str(sentence)+' '+language_detected+"\n")
            
            arch_salida.close()
                
if __name__ == '__main__':
    main()
    