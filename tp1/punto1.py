# Script de ejemplo que recorre los archivos de un directorio, lee su contenido, 
# normaliza los tokens que se encuentran dentro, y al final genera un diccionario
# de frecuencias que sera escrito en un archivo de salida
import sys
from os import listdir
from os.path import join, isdir
import re
from unidecode import unidecode

# Constantes 
min_len_tokens = 2
max_len_tokens = 50
list_terms={}


# Expresiones Regulares
regex_alpha_words = re.compile(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ]') # Cadenas alfanumericas sin acentos

# Obtiene los stopwords de un archivo y los devuelven en un array.
def getStopWords(filepath):
    stopwords=[]
    with open(filepath,'r') as f:
        for line in f:
            words_list =  line.strip().split()
            for word in words_list:
                stopwords.append(word)
    return stopwords

# Pasa a minusculas y elimina acentos
# Extra: Si el token es un numero lo imprime por consola
def normalize(token):
    new_token = unidecode(token)
    return new_token.lower()

# Extrae los tokens en una lista
def tokenizer(line):
    result = []
    initial_list_split = line.split()
    for token in initial_list_split:
        word = re.sub(regex_alpha_words,'',token)
        if word != '' and len(word)>min_len_tokens:
            result.append(word)
    return result

def main():
    if len(sys.argv) < 3:
        print('Es necesario pasar los argumentos: [dir_corpus] [use_stopwords (y o n)] [name_file_stopwords]')
        sys.exit(0)
    dirname = sys.argv[1]
    use_stopwords = True if sys.argv[2].lower() == 'y' else False
    stopwords_file = sys.argv[3]
    frequencies = {}
    filesCounter = 0
    tokensCounter = 0
    
    file_index = 0 # Identifica a cada archivo con id incremental (ademas, sirve para tener la cantidad de archivos total)
    
    # Obteniendo Stopwords
    if (isdir(dirname)):
        list_stopwords =[]
        #Valido uso de Stopwords
        if use_stopwords:
            if len(sys.argv) < 4: 
                print('Es necesario el nombre_archivo_stopwords')
                sys.exit(0)
            # Recuperos los stopwords del archivo
            list_stopwords = getStopWords(sys.argv[3])    
    

    if (isdir(dirname)):
        # Se procesa cada archivo del directorio
        for filename in listdir(dirname):
            filepath = join(dirname, filename)
            print(f"Procesando Archivo: {filepath}")
            # Se procesa cada linea del archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    # Tokenizacion
                    tokens_list =  tokenizer(line)

                    for token in tokens_list:
                        
                        token_in_stopwords = token in list_stopwords #Token existe en la list de stopwords?
                        token_long_acept = min_len_tokens<= len(token) <= max_len_tokens #longitud del Token aceptable?
                        if token_long_acept and (not token_in_stopwords):
                            
                            # Gestion de Terminos
                            term = normalize(token)
                            term_long_acept = (term != '') #Termino aceptable luego de Normalizacion?
                            if term_long_acept:
                                if term in list_terms: # Si el termino existe en la lista de terminos

                                    if file_index in list_terms[term]: # Si el termino ya tiene frecuencia en ese archivo(file_index)
                                        list_terms[term][file_index] +=1 # Se aumenta la frecuencia del termino del archivo(file_index)
                                    else:
                                        list_terms[term][file_index] = 1 # Se crea un diccionario que tiene el file_index y se inicia su frecuencia 

                                else: # Si el termino NO existe en la lista de terminos
                                    list_terms[term]={} # Se inicializa dic del nuevo termino
                                    list_terms[term][file_index] = 1 # Se inicializa la frecuencia del termino en ese archivo(file_index) 
            
            file_index += 1  # Actualizamos el id del archivo al siguiente
    
    # Guardo las listas de terminos com su DF y TF  en el archivo "terminos.txt"

    file_terms = open("terminos.txt", "x",encoding='utf-8')
    terms_ordered = sorted(list_terms.keys())
    for term_out in terms_ordered:
        frecuency = 0
        documents = 0
        for key, value in list_terms[term_out].items():
            frecuency += value
            documents += 1  
        file_terms.write(term_out+" "+ str(frecuency)+" "+ str(documents)+"\n")
    file_terms.close()


if __name__ == '__main__':
    main()