# Esto descargara los recursos necesarios para utilizar el algoritmo SnowballStemmer para español.
import os
import struct #utilizo el formato de 4 bytes ('i') 
from os import listdir
from os.path import join, isdir
from unidecode import unidecode
import nltk
nltk.download('snowball_data')
from nltk.stem.snowball import SpanishStemmer
from constantes import MIN_LEN_TOKEN,MAX_LEN_TOKEN,LIMIT_DOCS,PATH_POSTINGLIST,LEN_POSTING_CHUNK,PATH_CHUNKS
from extract_entitys import ExtractEntitys
from posting_list import PostingList

class Indexer:
    paths_docs=[] # Listado de archivos
    extractor = ExtractEntitys() # Extrae las entidades segun expresiones regulares definidas en la clase
    list_chunks={} #Almacena una lista de chunk y cada uno tiene los terminos con su puntero +df (para una lectura rapida posterior)
    list_filenames_to_docid = {}

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
        list_postings_terms={}
        vocabulary={}
        self.list_filenames_to_docid = {}
        self.paths_docs=[]
        self.term2id={}
        self.list_chunks={}
        self.file_index=1 # Identifica a cada archivo con id incremental (ademas, sirve para tener la cantidad de archivos total)
        self.term_id=1 #id de terminos  
        cant_files=0
        chunkid=1 #Contador que brinda un id a cada chunk procesado

        # Agrego todos los documentos de los subdirectorios
        self.add_file_in_list_paths(dirname)
        for filepath in self.paths_docs:
            if LIMIT_DOCS==cant_files: # Si no supera la cantidad limite de comuento a procesar
                self.almacenar_chunk(chunkid,list_postings_terms)
                chunkid+=1
                cant_files=0
                list_postings_terms={}
            
            # Guardo mapeo entre id y path del documento
            self.list_filenames_to_docid[self.file_index]=filepath
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
            
                                if term in list_postings_terms: # Si el termino existe en la lista de terminos

                                    index_doc = list_postings_terms[term].search_docid(self.file_index)
                                    if -1 != index_doc: # id_doc ya existe en la postinglist del termino
                                        list_postings_terms[term].update_score_posting(index_doc,1) # Suma 1 al score de la posting encontrada
                                    else:
                                        list_postings_terms[term].add_posting(self.file_index,1) # Se agrega docid a la lista de postings
                        
                                else: # Si el termino NO existe en la lista de posting
                                    if not(term in self.term2id): # El termino ya existia antes ?
                                        self.term2id[term]=self.term_id #Sino se crea un nuevo registro
                                        list_postings_terms[term]= PostingList([self.file_index],[1],self.term_id) # Se instancia una nueva PostingList
                                        self.term_id+=1
                                    else:#si ya existia se le utiliza el term_id asignado previamente
                                        list_postings_terms[term]= PostingList([self.file_index],[1],self.term2id[term]) # Se instancia una nueva PostingList con el term_id previo

            self.file_index += 1  # Actualizamos el id del archivo al sigui
            cant_files+=1

        if LIMIT_DOCS>=cant_files: # Si quedo un pedazo de chunk, vuelco a disco
            self.almacenar_chunk(chunkid,list_postings_terms)

        return self.list_chunks,self.term2id
                
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


    def get_filesids(self):
        return self.list_filenames_to_docid

    # Vuelca a disco el chunk de indice ya procesado
    def almacenar_chunk(self,chunkid,list_terms):
        posting_start=0
        with open(f'{PATH_CHUNKS}/chunk-{chunkid}.bin', 'wb') as f:
            for term, posting_list in list_terms.items():
                
                data_to_pack = [item for x in zip(posting_list.get_docids(),posting_list.get_scores()) for item in x] # empaqueto cada docid+frec

                document_frec=posting_list.get_document_frequency()
                
                if not(chunkid in self.list_chunks):
                    self.list_chunks[chunkid] = {}

                self.list_chunks[chunkid][term] = [posting_start,document_frec] # Se guarda por cada termino su puntero_inicial + DF
                posting_start+=document_frec*LEN_POSTING_CHUNK
                encoded = struct.pack(f'>{len(data_to_pack)}I',*data_to_pack)
                f.write(encoded)
    