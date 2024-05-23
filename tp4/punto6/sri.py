import os
import matplotlib.pyplot as plt# graficos
from indexer import Indexer
from posting_list import PostingList
from collections import deque # Cola para procesar la query
from constantes import TYPE_RETRIEVAL

class SRI:
    indexer = Indexer() # Instanciando indexador
    inverted_index: list[PostingList]# Lista de todas las posting_lists de cada termino
    map_filesids={}
    #Para el modelo vectorial
    cant_files = 0

    def __init__(self):
        pass
    
    def start(self):
        print("Indexando Collection...")
        self.indexer.indexar()
        self.inverted_index = self.indexer.get_inverted_index()
        print("Collection indexada.")


    # Devuelve la posting list en memoria
    def get_posting_list(self,term):
        if(len(term)<1 or term.isspace()):
            print("\n\n (!)Error termino vacio, no valido.\n\n")
        else:
            if term in self.inverted_index:
                return self.inverted_index[term]
        
        return PostingList(docids=[],scores=[]) 
    

    def query_procesing(self, query,type_retriev=TYPE_RETRIEVAL):
        query_terms = query.split(" ")
        
        if (query!="") and (query!=" "):
            # Si solo hay un termino solo se recupera la posting
            if len(query_terms)==1:
                return self.get_posting_list(query_terms[0]).get_docids()

            #Si hay más de un termino
            post_list_terms = []
            for term in query_terms:
                post_list_terms.append(self.get_posting_list(term)) 

            if type_retriev == "DAAT":
                return self.DocumentAtATime_AND(post_list_terms)
            else:
                return self.TermAtATime_AND(post_list_terms)
        else:
            return []

    def DocumentAtATime_AND(self,posting_lists):
        result_docs = []

        if all( len(posting_list.docids) > 0 for posting_list in posting_lists):
            # Inicializar los cursores de las listas de posteo
            for posting_list in posting_lists:
                posting_list._reset()

            while all(posting_list.cursor != -1 for posting_list in posting_lists):
                current_docids = [posting_list.docid() for posting_list in posting_lists]

                if all(docid == current_docids[0] for docid in current_docids):
                    result_docs.append(current_docids[0])
                    for posting_list in posting_lists:
                        posting_list.next_()
                else:
                    max_docid = max(current_docids)
                    for posting_list in posting_lists:
                        if posting_list.docid() < max_docid:
                            posting_list.ge(max_docid)

        return result_docs
        

    def TermAtATime_AND(self,posting_lists):
        result_docs = []

        if all( len(posting_list.docids) > 0 for posting_list in posting_lists):
            result_docs = posting_lists[0].docids  # Empezar con los docids del primer término

            for posting_list in posting_lists[1:]:
                current_docids = posting_list.docids
                result_docs = [docid for docid in result_docs if docid in current_docids]

        return result_docs