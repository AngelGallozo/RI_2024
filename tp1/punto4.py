# Script de ejemplo que recorre los archivos de un directorio, lee su contenido, 
# normaliza los tokens que se encuentran dentro, y al final genera un diccionario
# de frecuencias que sera escrito en un archivo de salida
import sys
from os import listdir
from os.path import join, isdir
import re
from unidecode import unidecode
# Esto descargara los recursos necesarios para utilizar los algoritmos de stemming para español.
import nltk
from nltk import LancasterStemmer
from nltk.stem import PorterStemmer
from time import time

# vars
min_len_tokens = 3
max_len_tokens = 50
list_terms={}
# Datos de documento más largo y corto [id_archivo,cant_tokens,cant_terminos]
doc_short=[-1,0,0]
doc_long=[-1,0,0]

top_high_frec=[]
top_low_frec=[]

# Expresiones Regulares
regex_alpha_words = re.compile(r'[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]') # Cadenas alfanumericas

# Obtiene los stopwords de un archivo y los devuelven en un array.
def getStopWords(filepath):
    stopwords=[]
    with open(filepath,'r') as f:
        for line in f:
            words_list =  line.strip().split()
            for word in words_list:
                stopwords.append(word)
    return stopwords

#Proceso de reduccion morfologica de los terminos
def stemming(term,tipo_stemmer):
    if(tipo_stemmer == 'Porter'):
        stemmer = PorterStemmer()
    if(tipo_stemmer == 'Lancaster'):
        stemmer = LancasterStemmer()
    return stemmer.stem(term)

# Pasa a minusculas y elimina acentos, además de aplicar stemming
def normalize(token,tipo_stemmer):
    new_token = unidecode(token)
    term = stemming(new_token.lower(),tipo_stemmer)
    return term

# Extrae los tokens en una lista
def tokenizer(line):
    result = []
    initial_list_split = line.split()
    for token in initial_list_split:
        word = re.sub(regex_alpha_words,'',token)
        if word != '' and len(word)>min_len_tokens:
            result.append(word)
    return result

# Verifica si los documentos son el más largo o más corto, de ser alguno guarda sus datos[idarchivo,cant_tokens, cant_Terms]
def verify_short_and_log_docs(file_index,cant_tokens,cant_terminos):
    if doc_short[0] != -1:
        if doc_short[1]>cant_tokens:
            doc_short[0] = file_index
            doc_short[1] = cant_tokens
            doc_short[2] = cant_terminos
    else:
        doc_short[0] = file_index
        doc_short[1] = cant_tokens
        doc_short[2] = cant_terminos
    
    if doc_long[1]<cant_tokens:
        doc_long[0] = file_index
        doc_long[1] = cant_tokens
        doc_long[2] = cant_terminos

# Verifica si los terminos esta en la lista de los 10 mas frecuentes o menos frecuentes.
def manage_tops(term,frec):
    # Top mas frecuentes
    if len(top_high_frec)==0 and len(top_low_frec)==0: # Se insertan el primer elemento en cada top(inicializamos)
        top_high_frec.append([term,frec])
        top_low_frec.append([term,frec])
    else: # verificar e insertar los termino en los tops
        verify_insert_top('high',term,frec)
        verify_insert_top('low',term,frec)

# verificar e insertar los termino en los tops segun tipo de tops
def verify_insert_top(type_top,term,frec):
    global top_high_frec
    global top_low_frec
    inserted=False
    index=0
    length=len(top_high_frec) if type_top == 'high' else len(top_low_frec)

    while (not inserted and index<length):
        if type_top == 'high': # Mas frecuentes
            if top_high_frec[index][1]< frec:
                top_high_frec.insert(index,[term,frec]) # Inserto elemento en el lugar
                top_high_frec=top_high_frec[:10] # me quedo con los primeros 10 de ser necesario
                inserted=True

        else:  # Menos frecuentes
            if top_low_frec[index][1]> frec:
                top_low_frec.insert(index,[term,frec]) # Inserto elemento en el lugar
                top_low_frec=top_low_frec[:10] # me quedo con los primeros 10 de ser necesario
                inserted=True
        index+=1
    
    if index == length:
        if type_top == 'high':
            top_high_frec.append([term,frec]) 
            top_high_frec=top_high_frec[:10] # me quedo con los primeros 10 de ser necesario
        else:
            top_low_frec.append([term,frec])
            top_low_frec=top_low_frec[:10] # me quedo con los primeros 10 de ser necesario
           

def save_frec_infile(tipo_stemmer):
    file_frecs = open(f'frecuencias_stemming_{tipo_stemmer}.txt', "x",encoding='utf-8')
    for term_high in top_high_frec:        
        file_frecs.write(term_high[0]+" "+ str(term_high[1])+"\n")
    
    for term_low in top_low_frec:        
        file_frecs.write(term_low[0]+" "+ str(term_low[1])+"\n")

    file_frecs.close()

def procesar_docs(tipo_stemmer):
    if len(sys.argv) < 3:
        print('Es necesario pasar los argumentos: [dir_corpus] [use_stopwords (y o n)] [name_file_stopwords]')
        sys.exit(0)
    dirname = sys.argv[1]
    use_stopwords = True if sys.argv[2].lower() == 'y' else False
    tokensCounter = 0 #Contador de tokens
    termsCounter = 0 #Contador de terminos
    file_index = 0 # Identifica a cada archivo con id incremental (ademas, sirve para tener la cantidad de archivos total)
    acum_long_term = 0 # Acumula longitudes de los terminos
    # Obteniendo Stopwords
    if (isdir(dirname)):
        list_stopwords =[]
        if use_stopwords:
            stopwords_file = sys.argv[3]
            list_stopwords =[]
            #Valido uso de Stopwords
            if len(sys.argv) < 4: 
                print('Es necesario el nombre_archivo_stopwords')
                sys.exit(0)
            # Recuperos los stopwords del archivo
            list_stopwords = getStopWords(stopwords_file)     
    
    if (isdir(dirname)):
        # Se procesa cada archivo del directorio
        for filename in listdir(dirname):
            tokensCounter_forfile = 0
            termsCounter_forfile = 0
            filepath = join(dirname, filename)
            # Se procesa cada linea del archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    # Tokenizacion
                    tokens_list =  tokenizer(line)

                    for token in tokens_list:
                        
                        token_in_stopwords = token in list_stopwords #Token existe en la list de stopwords?
                        token_long_acept = min_len_tokens<= len(token) <= max_len_tokens #longitud del Token aceptable?
                        if token_long_acept and (not token_in_stopwords):
                            tokensCounter += 1 # Aumento cantidad de tokens encontrados
                            tokensCounter_forfile += 1 # Aumento cantidad de tokens encontrados para este archivo
                            # Gestion de Terminos
                            term = normalize(token,tipo_stemmer)
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
                                    termsCounter+=1 # Aumento cantidad de terminos encontrados
                                    termsCounter_forfile +=1 # Aumento cantidad de terminos encontrados para este archivo
                                    acum_long_term+= len(term)
            
            # Verificacion y guardado de archivo más corto y más largo.
            verify_short_and_log_docs(file_index,tokensCounter_forfile,termsCounter_forfile)

            file_index += 1  # Actualizamos el id del archivo al siguiente
    

    cont_terms_frec1=0 # Contador de terminos con frecuencia 1
    # Guardo las listas de terminos com su DF y TF  en el archivo "terminos.txt"
    file_terms = open(f'terminos_stemming_{tipo_stemmer}.txt', "x",encoding='utf-8')
    terms_ordered = sorted(list_terms.keys())
    for term_out in terms_ordered:
        frecuency = 0
        documents = 0
        for key, value in list_terms[term_out].items():
            frecuency += value
            documents += 1  
        
        # Contar terminos con frecuencia 1
        if frecuency==1:
            cont_terms_frec1 +=1 

        # Verificar en si el termino es el más o menos frecuente
        manage_tops(term_out,frecuency)
        # Escribir en el archivo 
        file_terms.write(term_out+" "+ str(frecuency)+" "+ str(documents)+"\n")
    file_terms.close()

    # Archivo de Estadisticas "estadisticas.txt"
    file_stats = open(f'estadisticas_stemming_{tipo_stemmer}.txt', "x",encoding='utf-8')
    file_stats.write(str(file_index)+"\n")
    file_stats.write(str(tokensCounter)+' '+str(termsCounter)+"\n")
    file_stats.write(str(round(tokensCounter/file_index, 5))+' '+ str(round(termsCounter/file_index, 5))+"\n")
    file_stats.write(str(acum_long_term/termsCounter)+"\n")
    file_stats.write(str(doc_short[1])+' '+str(doc_short[2])+' '+str(doc_long[1])+' '+str(doc_long[2])+"\n")
    file_stats.write(str(cont_terms_frec1))
    file_stats.close()

    # Archivo de frecuencias.txt
    save_frec_infile(tipo_stemmer)

def main():
    ini_time = time()
    procesar_docs('Porter')
    print("Tiempo Stemming Porter: "+ str(time()-ini_time))
    
    ini_time = time()
    procesar_docs('Lancaster')
    print("Tiempo Stemming Lancaster: "+ str(time()-ini_time))

if __name__ == '__main__':
    main()