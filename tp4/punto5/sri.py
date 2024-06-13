import struct #utilizo el formato de 4 bytes ('i') 
import pickle
import os
import matplotlib.pyplot as plt# graficos
from indexer import Indexer
from constantes import LEN_POSTING,PATH_POSTINGLIST,PATH_VOCABULARY,MIN_LEN_TOKEN,MAX_LEN_TOKEN,PATH_MAP_FILESIDS,PATH_SKIPLIST,LEN_SKIPLIST,K_SKIP
from posting_list import PostingList
from collections import deque # Cola para procesar la query
import traceback
import re

class SRI:
    indexer = Indexer() # Instanciando indexador
    list_postings_terms: list[PostingList]# Lista de todas las posting_lists de cada termino
    vocabulary={}# Tabla Term - DF - Puntero
    map_filesids={}
    inverted_index={}

    def __init__(self):
        self.retriev_index()
    

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
                self.inverted_index[term] = unpacked_data

    
    def read_map_filesids(self):
        with open(PATH_MAP_FILESIDS, 'r', encoding='utf-8') as archivo:
            next(archivo)
            for linea in archivo:
                if '\t' in linea:
                    # Dividir la línea en dos partes usando el tabulador como separador
                    docid, path = linea.strip().split('\t')
                    self.map_filesids[docid]=path
    
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
        print("Generando SkipList...")
        self.build_skiplists()
        print("SkipList Generados.")

    

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


    def query_and(self,posting_one,posting_two):
        intersection = []
        while(posting_one.cursor != -1) and (posting_two.cursor != -1):
            if posting_one.docid() == posting_two.docid():
                intersection.append(posting_one.docid())
                posting_one.next_()
                posting_two.next_()
            elif posting_one.docid() < posting_two.docid():
                posting_one.next_()
            else:
                posting_two.next_()
        return PostingList(docids=intersection)
    
    def query_and_skiplist(self,posting_one,posting_two):
        intersection = []
        while(posting_one.cursor != -1) and (posting_two.cursor != -1):
            if posting_one.docid() == posting_two.docid():
                intersection.append(posting_one.docid())
                posting_one.next_()
                posting_two.next_()
            elif posting_one.docid() < posting_two.docid():
                posting_one.next_skiplist(posting_two.docid())
                
                if posting_one.cursor!=-1:
                    while (posting_one.cursor!=-1) and (posting_one.docid() < posting_two.docid()):
                        posting_one.next_()

            else:
                posting_two.next_skiplist(posting_one.docid())
                if posting_two.cursor!=-1:
                    while (posting_two.cursor!=-1) and (posting_two.docid() < posting_one.docid()):
                        posting_two.next_()

        return PostingList(docids=intersection)



    def query_or(self,posting_one,posting_two):
        union = []
        while(posting_one.cursor != -1) and (posting_two.cursor != -1):
            if posting_one.docid() < posting_two.docid():
                union.append(posting_one.docid())
                posting_one.next_()
            elif posting_one.docid() > posting_two.docid():
                union.append(posting_two.docid())
                posting_two.next_()
            else:
                union.append(posting_one.docid())
                posting_one.next_()
                posting_two.next_()
        
        while posting_one.cursor != -1 :
            union.append(posting_one.docid())
            posting_one.next_()
        
        while posting_two.cursor != -1:
            union.append(posting_two.docid())
            posting_two.next_()
        
        return PostingList(docids=union)
    
    def query_not(self,posting_one,posting_two):
        negative=[]
        
        while posting_one.cursor != -1:
            current =  posting_one.docid()
            if current != posting_two.ge(current):
                negative.append(current)

            posting_one.next_()
    
        
        return PostingList(docids=negative)
    
    def query_two_terms(self, query,operator_type):
        postinglist_result = None
        query = query.strip("(",).strip(")")
        query = query.replace(" ","")
        term1, term2 = query.split(operator_type)
        postinglist_term1 = self.get_posting_list(term1)
        postinglist_term2 = self.get_posting_list(term2)
        if operator_type == "AND":
            # postinglist_result = self.query_and(postinglist_term1, postinglist_term2)
            postinglist_result = self.query_and_skiplist(postinglist_term1, postinglist_term2)
            
        if operator_type == "OR":
            postinglist_result = self.query_or(postinglist_term1, postinglist_term2)

        if operator_type == "NOT":
            postinglist_result = self.query_not(postinglist_term1, postinglist_term2)

        return postinglist_result

    def query_three_terms(self, query):
        
        try: # Caso donde Hay term 1 AND term2 AND term 3
            query =query.replace(" ","")
            term1, term2, term3 = query.split("AND")
            postinglist_result = self.query_and_skiplist(self.get_posting_list(term1),self.get_posting_list(term2))
            return self.query_and_skiplist(postinglist_result,self.get_posting_list(term3))
        except Exception as e:
            traceback.print_exc()
            pass


        try:
            parenthesis = re.findall(r'\((.*?)\)', query)[0]
            postinglist_result = PostingList(docids=self.query_procesing(parenthesis))
            rest = query.replace("("+parenthesis+")", "")
            rest = rest.replace(" ","")
            if "AND" in rest:
                token = rest.replace("AND", "")
                # return self.query_and(self.get_posting_list(token),postinglist_result)
                return self.query_and(self.get_posting_list(token),postinglist_result)

            if "NOT" in rest:
                token = rest.replace("NOT", "")
                return self.query_not(self.get_posting_list(token),postinglist_result)

            if "OR" in rest:
                token = rest.replace("OR", "")
                return self.query_or(self.get_posting_list(token),postinglist_result)

        except Exception as e:
            # traceback.print_exc()
            pass

    
    def query_procesing(self, query):
        cant_nots = query.count("NOT") 
        cant_ands = query.count("AND")
        cant_ors = query.count("OR")
        
        try:
            if (cant_ands+cant_ors+cant_nots) == 1: # Si solo hay: term1 Operador term2
                if cant_ands == 1:
                    operator_type = "AND"
                if cant_ors == 1:
                    operator_type = "OR"
                if cant_nots == 1:
                    operator_type = "NOT"
                
                return self.query_two_terms(query,operator_type).get_docids()
            else:
                if (cant_ands+cant_ors+cant_nots) > 1: # Si hay: term1 operador term2 operador term3
                    return self.query_three_terms(query).get_docids()

                else:# Para cuando hay solo un termino
                    return self.get_posting_list(query).get_docids()
        except Exception as e:
            traceback.print_exc()
            return []
    

    def get_posting_list(self,token):
        docids = []
        scores = []
        term_skiplist=[]
        if os.path.exists(PATH_POSTINGLIST):
            if len(self.vocabulary)==0:
                self.load_vocabulary() # Cargarmos la tabla de postingslists

            if len(self.vocabulary) > 0:

                if(len(token)<1 or token.isspace()):
                    print("\n\n (!)Error termino vacio, no valido.\n\n")
                else:
                    term = self.indexer.normalize(token)
                    term_long_acept = MIN_LEN_TOKEN<= len(term) <= MAX_LEN_TOKEN #longitud del term aceptable?
                    if term_long_acept:
                        if term in self.vocabulary:
                            posting_start,df,pointer_skip = self.vocabulary[term]
                            with open(PATH_POSTINGLIST, 'rb') as f:
                                # Mover el puntero de lectura al inicio de la posición deseada
                                f.seek(posting_start)

                                # Leer los datos binarios desde esa posición
                                _bytes = f.read(df * LEN_POSTING)

                                # Desempaquetar los datos binarios en enteros
                                term_posting = struct.unpack(f'>{df * 2}I', _bytes)
                                docids = list(term_posting[::2])
                                scores = list(term_posting[1::2])

                            if pointer_skip !=-1:
                                with open(PATH_SKIPLIST,'rb') as skips:
                                    skips.seek(pointer_skip)
                                    _bytes_skip = skips.read((df//K_SKIP) * LEN_SKIPLIST)
                                    unpacked_term_skiplist = struct.unpack(f'>{(df//K_SKIP) * 2}I', _bytes_skip)
                                    term_skiplist = list(unpacked_term_skiplist)
                             
                    else:
                        print("\n\n (!)Error termino con longitud insuficiente.\n\n")
        else:
            print("(!)ERROR: El archivo'{}' no fue encontrado, porfavor indexar.".format(PATH_POSTINGLIST))
        
        return PostingList(docids=docids,scores=scores,skips=term_skiplist)

    def build_skiplists(self):
        pointer_start = 0
        skips = open(PATH_SKIPLIST, "wb")

        with open(PATH_POSTINGLIST, "rb") as f:
            for term in self.vocabulary.keys():
                #Leer la PostingList en Disco
                posting_start, document_frequency = self.vocabulary[term]
                string_format = "{}I".format(document_frequency)
                # Mover el puntero de lectura al inicio de la posición deseada
                f.seek(posting_start)
                # Leer los datos binarios desde esa posición
                _bytes= f.read(document_frequency * LEN_POSTING)
                # Desempaquetar los datos binarios en enteros
                unpacked_data = struct.unpack(f'>{document_frequency*2}I', _bytes)
                docids = list(unpacked_data[::2])
                skiplist=[]
                # Escribiendo sobre el Archivo SkipList
                if (len(docids)//K_SKIP)>0: #Si puede tener skiplist
                    #Escribir
                    pointer_bytes = 0 # Se suma el primer posting
                    for i in range(1,len(docids)):
                        if ((i+1)%K_SKIP)==0:# Si la siguiente posicion es una skip [uso la siguiente porque mi for va de 1 a n] cuenta uno menos
                            # Guardo el docid y los bytes
                            skiplist.append(docids[i])
                            pointer_bytes+=LEN_POSTING*K_SKIP
                            skiplist.append(pointer_bytes) 

                    self.vocabulary[term].append(pointer_start) # Se almacena el punto donde comienza la Skiplist de ese termino
                    pointer_start+=(document_frequency//K_SKIP)*LEN_SKIPLIST # Multiplico la cantidad de skips * longitud de la skip
                    encoded = struct.pack(f'>{len(skiplist)}I',*skiplist)
                    skips.write(encoded)
                else: #Si no puede tener Skiplist
                    self.vocabulary[term].append(-1) # Se almacena un -1 simbolizando que no tiene

    def get_skiplist(self,token):
        term_skiplist=[]
        if os.path.exists(PATH_POSTINGLIST):
            docids_skiplist=[]
            bytes_skiplist=[]
            if len(self.vocabulary)==0:
                self.load_vocabulary() # Cargarmos la tabla de postingslists

            if len(self.vocabulary) > 0:

                if(len(token)<1 or token.isspace()):
                    print("\n\n (!)Error termino vacio, no valido.\n\n")
                else:
                    term = self.indexer.normalize(token)
                    term_long_acept = MIN_LEN_TOKEN<= len(term) <= MAX_LEN_TOKEN #longitud del term aceptable?
                    if term_long_acept:
                        if term in self.vocabulary:
                            posting_start,df,pointer_skip = self.vocabulary[term]
                            if pointer_skip !=-1:
                                with open(PATH_SKIPLIST,'rb') as skips:
                                    skips.seek(pointer_skip)
                                    _bytes_skip = skips.read((df//K_SKIP) * LEN_SKIPLIST)
                                    unpacked_term_skiplist = struct.unpack(f'>{(df//K_SKIP) * 2}I', _bytes_skip)
                                    docids_skiplist = list(unpacked_term_skiplist[::2])
                                    bytes_skiplist = list(unpacked_term_skiplist[1::2])
                             
                    else:
                        print("\n\n (!)Error termino con longitud insuficiente.\n\n")
        else:
            print("(!)ERROR: El archivo'{}' no fue encontrado, porfavor indexar.".format(PATH_POSTINGLIST))
        
        return docids_skiplist,bytes_skiplist

