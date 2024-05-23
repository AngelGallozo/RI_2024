import struct #utilizo el formato de 4 bytes ('i') 
import pickle
import os
import math
import matplotlib.pyplot as plt# graficos
from indexer import Indexer
from constantes import LEN_POSTING,PATH_POSTINGLIST,PATH_VOCABULARY,MIN_LEN_TOKEN,MAX_LEN_TOKEN,PATH_MAP_FILESIDS,TOP_K
from posting_list import PostingList
from collections import deque # Cola para procesar la query
import traceback
import re
import heapq # Para el ranking

class SRI:
    indexer = Indexer() # Instanciando indexador
    list_postings_terms: list[PostingList]# Lista de todas las posting_lists de cada termino
    vocabulary={}# Tabla Term - DF - Puntero
    map_filesids={}
    inverted_index={}
    #Para el modelo vectorial
    docs_normas={}
    cant_files = 0

    def __init__(self):
        pass
    

    def load_vocabulary(self):
        try:
            with open(PATH_VOCABULARY, "rb") as archivo:
                self.vocabulary = pickle.load(archivo)
        except FileNotFoundError:
            print("(!)ERROR: El archivo'{}' no fue encontrado, porfavor indexar.".format(PATH_VOCABULARY))
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON, porfavor indexar.")


    def read_inverted_index(self):
        with open(PATH_POSTINGLIST, "rb") as f:
            for term in self.vocabulary:
                posting_start, document_frequency = self.vocabulary[term]
                string_format = "{}I".format(document_frequency)
                # Mover el puntero de lectura al inicio de la posición deseada
                f.seek(posting_start)
                # Leer los datos binarios desde esa posición
                _bytes= f.read(document_frequency * LEN_POSTING)
                # Desempaquetar los datos binarios en enteros
                unpacked_data = struct.unpack(f'>{document_frequency*2}I', _bytes)
                docids = unpacked_data[::2]
                freqs = unpacked_data[1::2]
                self.inverted_index[term] = PostingList(docids=docids, freqs=freqs)

    
    def read_map_filesids(self):
        with open(PATH_MAP_FILESIDS, 'r', encoding='utf-8') as archivo:
            next(archivo)
            for linea in archivo:
                if '\t' in linea:
                    # Dividir la línea en dos partes usando el tabulador como separador
                    docid, path = linea.strip().split('\t')
                    self.map_filesids[docid]=path
                    self.cant_files+=1
    
    #Se Calculan los idfs de cada termino
    def calculate_idfs(self):
        for term in self.inverted_index.keys():
            idf = math.log(self.cant_files/self.inverted_index[term].get_document_frequency(),10)
            self.inverted_index[term].set_idf_term(idf) 

    # Se calculan los tf*idf para las postinglist
    def calculate_tf_idfs(self):
        for term in self.inverted_index.keys():
            scores = []
            for term_freq_in_doc in self.inverted_index[term].get_freqs():
                scores.append(term_freq_in_doc * self.inverted_index[term].get_idf_term())
                
            self.inverted_index[term].set_tf_idfs(scores)

    def retriev_index(self):
        print("Recuperando Vocabulario...")
        self.load_vocabulary()
        print("Vocabulario Recuperado.")
        print("Reconstruyendo Indice...")
        self.read_inverted_index()
        print("Indice Recuperado.")
        print("Mapeando Archivos...")
        self.read_map_filesids()
        print("Mapeo de Archivos Recuperado.")
        print("Genrando Modelo Vectorial...")
        self.calculate_idfs()
        self.calculate_tf_idfs()
        print("Modelo Vectorial Listo.")
    

    # Retorna una PostingList con los docids que tienen en comun las postinglists recibidas
    def binary_merge(self,postings):
        a = postings[0]
        for posting in postings[1:]:
            temp_posting = []
            current = a.docid()
            while current:
                posting.ge(current)
                if posting.docid()==current:
                    temp_posting.append(current)
                a.next_()
                current = a.docid()
            a = PostingList(docids=temp_posting)
        return a

    def index_query(self, query):
        query_terms = []
        list_tokens = self.indexer.tokenizer(query)
        for token in list_tokens:
            term = self.indexer.normalize(token)
            if term not in query_terms:
                query_terms.append(term)
        
        return query_terms


    def clean_terms(self,query_terms):
        return [k for k in query_terms if k in self.inverted_index]


    # Devuelve la posting list en memoria
    def get_posting_list(self,term):
        if(len(term)<1 or term.isspace()):
            print("\n\n (!)Error termino vacio, no valido.\n\n")
        else:
            term_long_acept = MIN_LEN_TOKEN<= len(term) <= MAX_LEN_TOKEN #longitud del term aceptable?
            if term_long_acept:
                if term in self.inverted_index:
                    return self.inverted_index[term]
        
        return PostingList(docids=[],scores=[]) 


    def DocumentAtATime(self,postings):
        top_k = [(0,0)]*TOP_K
        heapq.heapify(top_k)
        result={}
        uniques = self.binary_merge(postings).get_docids()
        for p in postings:
            p._reset()
        
        for d in uniques:
            for p in postings:
                current = p.ge(d)
                if current == d:
                    result[d] = result.get(p.docid(),0) + p.score()
                    p.next_()
            
            if result[d] > top_k[0][0]:
                heapq.heappushpop(top_k,(result[d],d))
        
        return heapq.nlargest(TOP_K,top_k)


    def query_procesing(self, query):
        # Calculos Querys
        post_list_terms = []

        # Indexacion de los terminos de la query
        query_terms = self.index_query(query)
        
        # Elimino los terminos que no esten en la coleccion
        query_terms = self.clean_terms(query_terms)
        
        for term in query_terms:
            post_list_terms.append(self.get_posting_list(term)) 
        
        return self.DocumentAtATime(post_list_terms)
