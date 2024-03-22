import sys
import re
import os
from os import listdir
from os.path import join, isdir
from unidecode import unidecode

list_terms=[]

regex_alpha_words = re.compile(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ]') # Cadenas alfanumericas
# Extrae los tokens en una lista
def tokenizer(line):
    result = []
    initial_list_split = line.split()
    for token in initial_list_split:
        word = re.sub(regex_alpha_words,'',token)
        if word != '':
            word = normalize(word)
            result.append(word)
    return result

# Normalización
def normalize(token):
    new_token = unidecode(token)
    return new_token.lower()

def main():
    if len(sys.argv) < 2:
        print('Es necesario pasar nombre del directorio')        
        sys.exit(0)
    dirname = sys.argv[1]
    print("a")
    if (isdir(dirname)):
        print("b")
        arch_salida = open(f'punto_8_heaps.txt', "x",encoding='utf-8')
        terms_total = 0
        for filename in listdir(dirname):
            filepath = join(dirname, filename)
            with open(filepath,'r',encoding='utf-8') as f:
                print(f"Processing file: {filepath}")
                for line in f:
                    terms_list = tokenizer(line)
                    for term in terms_list:
                        terms_total+=1
                        if not(term in list_terms):
                            list_terms.append(term)
                            
                    # Escribimos en el archivo
                    arch_salida.write(str(terms_total)+' '+str(len(list_terms))+"\n")
        arch_salida.close()

if __name__ == '__main__':
    main()
    