# Esto descargara los recursos necesarios para utilizar el algoritmo SnowballStemmer para español.
import os
from os import listdir
from os.path import join, isdir
from unidecode import unidecode
import nltk
nltk.download('snowball_data')
from nltk.stem.snowball import SpanishStemmer
from constantes import MIN_LEN_TOKEN,MAX_LEN_TOKEN
from extract_entitys import ExtractEntitys
from special_functions import binary_search
from posting_list import PostingList

class Indexer:
    paths_docs=[] # Listado de archivos
    extractor = ExtractEntitys() # Extrae las entidades segun expresiones regulares definidas en la clase
    
    def __init__(self):
        pass
    
    # Agrega los archivos en las subcarpetas a una lista de docs
    def add_file_in_list_paths(self,dirname):
        if (isdir(dirname)):
            for filename in listdir(dirname):
                filepath = join(dirname, filename)
                self.add_file_in_list_paths(filepath)
        else:
            self.paths_docs.append(dirname)

    def indexar(self,dirname):
        #reiniciamos terminos y contador de archivos
        self.list_postings_terms={}
        self.file_index=1 # Identifica a cada archivo con id incremental (ademas, sirve para tener la cantidad de archivos total)
        self.term_id=1 #id de terminos  
        
        # Agrego todos los documentos de los subdirectorios
        self.add_file_in_list_paths(dirname)

        for filepath in self.paths_docs:
            print(f"Procesando Archivo: {filepath}")
            # Se procesa cada linea del archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    # Tokenizacion
                    tokens_list =  self.tokenizer(line)
                    for token in tokens_list:
                        token_long_acept = MIN_LEN_TOKEN<= len(token) <= MAX_LEN_TOKEN #longitud del Token aceptable?
                        if token_long_acept:
                            # Gestion de Terminos
                            term = self.normalize(token)
                            term_long_acept = (term != '') #Termino aceptable luego de Normalizacion?
                            if term_long_acept:
            
                                if term in self.list_postings_terms: # Si el termino existe en la lista de terminos

                                    index_doc = self.list_postings_terms[term].search_docid(self.file_index)
                                    if -1 != index_doc: # id_doc ya existe en la postinglist del termino
                                        self.list_postings_terms[term].update_score_posting(index_doc,1) # Suma 1 al score de la posting encontrada
                                    else:
                                        self.list_postings_terms[term].add_posting(self.file_index,1) # Se agrega docid a la lista de postings
                        
                                else: # Si el termino NO existe en la lista de posting
                                    self.list_postings_terms[term]= PostingList([self.file_index],[1],self.term_id) # Se instancia una nueva PostingList
                                    self.term_id+=1
                                    
            self.file_index += 1  # Actualizamos el id del archivo al sigui



    # Extrae los tokens en una lista
    def tokenizer(self,line):
        result = []
        
        #Proceso las URL y email
        line,result = self.extractor.proc_urls_emails(line,result)

        #Proceso Abreviaturas
        line,result = self.extractor.proc_abrev(line,result)

        # Proceso los nombres propios
        line,result = self.extractor.proc_nombres_propios(line,result)

        # Genero lista de tokens
        initial_list_split = line.split() 

        # Analisis otros patrones, se agregan los tokens a la lista final y luego se quitan para la revisión de los siguientes patrones
        for token in initial_list_split:
            #Proceso Cantidad (Numero y telefonos)
            token, result = self.extractor.proc_cantidades(token,result)

            #Procesa alphanumericos
            result = self.extractor.proc_alphanum(token,result)

        return result

    #Proceso de reduccion morfologica de los terminos
    def stemming(self,token):
        spanish_stemmer = SpanishStemmer()
        return spanish_stemmer.stem(token)

    # Pasa a minusculas y elimina acentos
    def normalize(self,token):
        new_token = unidecode(token)
        new_token = self.stemming(new_token.lower())
        return new_token    
    
    def get_terms_index(self):
        return self.list_postings_terms
    
    def get_cant_files_indexed(self):
        return self.file_index
    
