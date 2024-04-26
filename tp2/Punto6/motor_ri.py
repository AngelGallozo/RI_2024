import re
import math
from os import listdir
from os.path import join, isdir
from nltk import LancasterStemmer

class MotorRI:
    
    regex_alpha_words = re.compile(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ]') # Cadenas alfanumericas
    cant_docs = 0
    
    # Stats Docs
    list_terms = {}
    list_idfs  = {}
    list_terms_tf_idfs = {}
    docs_normas ={}
    
    # guarda momentaneamente los paths
    paths_docs = []
    
    # Vincula los paths con un id_documento
    documentos_procesados={}
    
    def __init__(self):
        pass
    
    # Stemming
    def stemming(self,term):
        stemmer = LancasterStemmer()
        return stemmer.stem(term)
    
    
    # Normalizacion a minusculas de los terminos
    def normalize(self,token):
        return token.lower()
    
    # Extrae los tokens en una lista
    def tokenizer(self,line):
        result = []
        initial_list_split = line.split()
        for token in initial_list_split:
            word = re.sub(self.regex_alpha_words,'',token)
            if word != '':
                result.append(word)
        return result
    
    # Indexa los terminos de una linea a una determinada lista
    # Si se procesa un query por defecto su file_index = 0 identificando a la query
    def indexado(self,line,list_terms,file_index=0):
        terms_list = self.tokenizer(line)
        for term in terms_list:
            term = self.normalize(term)
            term = self.stemming(term)
            if term in list_terms:
                if file_index in list_terms[term]:
                    list_terms[term][file_index] +=1
                else:
                    list_terms[term][file_index] = 1 
            else:
                list_terms[term]={}
                list_terms[term][file_index] = 1
        
    # Agrega los archivos en las subcarpetas a una lista de docs
    def add_file_in_list_paths(self,dirname):
        if (isdir(dirname)):
            for filename in listdir(dirname):
                filepath = join(dirname, filename)
                self.add_file_in_list_paths(filepath)
        else:
            self.paths_docs.append(dirname)
    
    
    #Se leen los documentos y se guardan los terminos y sus frecuencias
    def leer_directorio(self,dirname):
        file_index = 1
        self.add_file_in_list_paths(dirname)
        
        for filepath in self.paths_docs:
            with open(filepath,'r',encoding='utf-8') as f:
                print(f"Processing file: {filepath}")
                for line in f:
                    self.indexado(line,self.list_terms,file_index)
            
            # Guardando vinculo entre id_docs y paths
            self.documentos_procesados[file_index] = filepath
            file_index += 1
    
        self.cant_docs = file_index-1
        return self.list_terms

    def clean_terms(self,query_terms):
        return {k: v for k, v in query_terms.items() if k in self.list_terms}
    
    # Procesamiento de la query
    def procesar_query(self,query):
        # Stats Querys
        query_terms = {}
        query_terms_idf = {}
        query_terms_tf_idf = {}
        query_norma = -1
        
        # Indexacion de los terminos de la query
        self.indexado(query,query_terms)
        
        # Elimino los terminos que no esten en la coleccion
        query_terms = self.clean_terms(query_terms)
        
        # Obteniendo los idfs de cada termino de la coleccion
        query_terms_idf = self.obtener_idfs(query_terms)
        
        # Calculando los tf-idf para el vector de la query
        query_terms_tf_idf = self.calcular_TF_IDF(query_terms, query_terms_idf)
        
        # Calculando la norma del vector query
        query_norma = self.query_calcular_normas(query_terms_tf_idf)
        
        # Calculo del ranking usando Coseno
        docs_ranking = self.generar_ranking(self.list_terms_tf_idfs, query_terms_tf_idf,self.docs_normas,query_norma)
        
        docs_relevantes = []
        # Adjuntando paths de los documentos del ranking
        for doc_rank in docs_ranking:
            id_doc = doc_rank[0]
            docs_relevantes.append([id_doc,doc_rank[1],self.documentos_procesados[id_doc]])
        
        return docs_relevantes
        
    
    #se calculan los idfs de cada termino
    def calcular_idfs(self, list_terms):
        list_idfs = {}
        for term,value in list_terms.items():
            list_idfs[term] = math.log(self.cant_docs/len(value),10)
        return list_idfs
    
    # Obtiene los IDFs de cada termino de la query almacenados de la coleccion
    def obtener_idfs(self, query_terms):
        list_idfs = {}
        for term in query_terms:
            list_idfs[term] = self.list_idfs[term]

        return list_idfs
    
    #se calculan la estructura TF_IDF
    def calcular_TF_IDF(self, list_terms,list_idfs):
        list_tf_idfs = {}
        for term,values in list_terms.items():
            for doc,value in values.items():
                if term in list_tf_idfs:
                    list_tf_idfs[term][doc] = value*list_idfs[term]
                else:    
                    list_tf_idfs[term]={}
                    list_tf_idfs[term][doc] = value*list_idfs[term]
                

        return list_tf_idfs
    
    #Calcular las normas de cada documento
    def calcular_normas(self,list_terms_tf_idfs, docs_normas):
        for term,values in list_terms_tf_idfs.items():
            for doc,value in values.items():
                if doc in docs_normas:
                    docs_normas[doc] = docs_normas[doc] + (value*value)
                else:
                    docs_normas[doc] = (value*value)
    
        
        #calculo de la raiz
        for doc,value in self.docs_normas.items():
            self.docs_normas[doc] = math.sqrt(value)
            
    #calcular norma de la query
    def query_calcular_normas(self,query_terms_tf_idfs):
        norma = 0
        for term,values in query_terms_tf_idfs.items():
            for doc,value in values.items():
                    norma += value*value
                    
        return math.sqrt(norma)
    
    
    # Ubicar los documentos donde estan los terminos
    def ubicar_documentos(self,query_terms_tf_idf,list_terms_tf_idfs):
        docs =[]
        for term in query_terms_tf_idf:
            for doc,value in list_terms_tf_idfs[term].items():
                if not (doc in docs):
                    docs.append(int(doc))
        return docs
    
    # Calcular el producto escalar de cada documento
    def calcular_prod_escal_docs(self, docs,query_terms_tf_idf,list_terms_tf_idfs):
        docs_prod_esc = []
        for doc in docs:
            suma_producto = 0
            for query_term in query_terms_tf_idf:
                
                # obtengo el tf-idef del termino en el documento, si no existe es 0
                term_tf_idf = list_terms_tf_idfs[query_term].get(doc,0)
                
                # Obtengo el tf-idf de cada termino de la query
                qry_term_tf_idf = query_terms_tf_idf[query_term][0]
                
                suma_producto += term_tf_idf * qry_term_tf_idf
                
            
            # Guardo el producto escalar del documento
            docs_prod_esc.append([doc,suma_producto])
        
        return docs_prod_esc
    
    # Calcular coseno para cada documento
    def calcular_cos_docs(self,docs_prod_esc,docs_normas,query_norma):
        ranking = []
        for doc in docs_prod_esc:
            id_doc = doc[0]
            doc_value = doc[1]
            coseno = doc_value/(docs_normas[id_doc]*query_norma)
            ranking.append([id_doc,coseno])
        
        return ranking
    
    
    # Generar ranking de documentos usando el metodo del Coseno
    def generar_ranking(self,list_terms_tf_idfs, query_terms_tf_idf,docs_normas,query_norma):
        result = []
        
        # Ubicar los documentos donde estan los terminos
        docs = self.ubicar_documentos(query_terms_tf_idf,list_terms_tf_idfs)
      
        # Buscamos el tf-idf de cada termino en cada documento de la coleccion, para multiplicarlo por el vector tf-idf de la query
        docs_prod_esc = self.calcular_prod_escal_docs(docs,query_terms_tf_idf,list_terms_tf_idfs)
        
        # Calcular coseno para cada documento        
        result = self.calcular_cos_docs(docs_prod_esc,docs_normas,query_norma)
        
        # Ordenar por relevancia
        ranking = sorted(result, key=lambda x: x[1], reverse=True)
            
        return ranking
    
    # Iniciar motor de RI
    def start(self,dirname):
        cant_docs = 0
        self.paths_docs = []
        self.documentos_procesados={}
    
        # Restart Stats Docs
        list_terms = {}
        list_idfs  = {}
        list_terms_tf_idfs = {}
        docs_normas = {}
        
        self.list_terms = self.leer_directorio(dirname)
        self.list_idfs = self.calcular_idfs(self.list_terms)
        self.list_terms_tf_idfs = self.calcular_TF_IDF(self.list_terms, self.list_idfs)
        self.calcular_normas(self.list_terms_tf_idfs, self.docs_normas)