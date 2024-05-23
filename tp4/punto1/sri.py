import pickle
import struct #utilizo el formato de 4 bytes ('i') 
import os
import sys
import matplotlib.pyplot as plt# graficos
from indexer import Indexer
from constantes import LEN_POSTING,PATH_POSTINGLIST,PATH_VOCABULARY,MIN_LEN_TOKEN,MAX_LEN_TOKEN,PATH_PLOTS,PATH_INDEX_FILES,PATH_MAP_FILESIDS,TRUE_STATS
from posting_list import PostingList
import time
from merger import Merger
from special_functions import binary_search

class SRI:
    indexer = Indexer() # Instanciando indexador
    merger=Merger()
    list_postings_terms: list[PostingList]# Lista de todas las posting_lists de cada termino
    vocabulary={}# Tabla Term - DF - Puntero
    cant_files=0
    list_filenames_to_docid={}
    inverted_index={}

    def __init__(self):
        pass

    def start(self,dirname):
        start = time.time()
        print("Indexando Corpus....")
        list_chunks,list_terms = self.indexer.indexar(dirname) # Indexado de documentos
        end = time.time()
        print("Tiempo Indexado : {} seconds.".format(end - start))

        start = time.time()
        print("Mergeando Indice....")
        # Merge de todos los chunks, le paso los terminos del vocabulario y la lista de chunks
        # Retorna el vocabulario final luego de la generacion del archivo binario final
        self.vocabulary,self.inverted_index = self.merger.merger_chunk(list_terms, list_chunks) 
        end = time.time()
        print("Tiempo Merge : {} seconds.".format(end - start))

        #Se guarda en disco el vocabulario
        self.save_vocabulary()

        self.list_filenames_to_docid = self.indexer.get_filesids() #Obtener cantidad de documentos indexado
        #Se guarda en el mapeo de paths con docid
        self.save_map_files()

        if TRUE_STATS:
            #Exportado de distribucion de posting
            self.ploting_distribution()
            # Calculo Overhead del indice respecto de la coleccion
            self.overhead_collection(dirname)
            # Exportado de distribucion de Overhead documentos
            self.overhead_documents()



    def save_vocabulary(self):
        with open(PATH_VOCABULARY, "wb") as archivo:
            pickle.dump(self.vocabulary, archivo)

    def save_map_files(self):
        with open(PATH_MAP_FILESIDS,"w",encoding="utf-8") as f:
            f.write("{}\t{}\r\n".format("id", "doc_path"))
            for doc_id,doc_path in self.list_filenames_to_docid.items():
                f.write("{}\t{}\r\n".format(doc_id, doc_path))

    
    def get_posting_list(self):
        list_docs=[]
        list_freqs=[]
        if os.path.exists(PATH_POSTINGLIST):
            if len(self.vocabulary)==0:
                self.load_vocabulary() # Cargarmos la tabla de postingslists

            if len(self.vocabulary) > 0:
                print("\n\n--------------------------------------------------------")
                token = input("Ingrese termino: ")
                if(len(token)<1 or token.isspace()):
                    print("\n\n (!)Error termino vacio, no valido.\n\n")
                else:
                    term = self.indexer.normalize(token)
                    term_long_acept = MIN_LEN_TOKEN<= len(term) <= MAX_LEN_TOKEN #longitud del term aceptable?
                    if term_long_acept:
                        if term in self.vocabulary:
                            list_docs,list_freqs = self.get_posting(term)
                        else:
                            print("\n\n (!)Error termino inexsitente.\n\n")
                    else:
                        print("\n\n (!)Error termino con longitud insuficiente.\n\n")
        else:
            print("(!)ERROR: El archivo'{}' no fue encontrado, porfavor indexar.".format(PATH_POSTINGLIST))
        return list_docs,list_freqs,token
    

    def load_vocabulary(self):
        try:
            with open(PATH_VOCABULARY, "rb") as archivo:
                self.vocabulary = pickle.load(archivo)
        except FileNotFoundError:
            print("(!)ERROR: El archivo'{}' no fue encontrado, porfavor indexar.".format(PATH_VOCABULARY))
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON, porfavor indexar.")
        

    def get_posting(self,term):

        posting_start,df = self.vocabulary[term]
        with open(PATH_POSTINGLIST, 'rb') as f:
            # Mover el puntero de lectura al inicio de la posición deseada
            f.seek(posting_start)

            # Leer los datos binarios desde esa posición
            _bytes = f.read(df * LEN_POSTING)

            # Desempaquetar los datos binarios en enteros
            term_posting = struct.unpack(f'>{df * 2}I', _bytes)
            docids = list(term_posting[::2])
            freqs = list(term_posting[1::2])
            
        return docids,freqs

    def convert_array_in_dic(self,array_keys,array_values):
            # Verificar que los dos arrays tengan la misma longitud
        if len(array_keys) != len(array_values):
            raise ValueError("Los arrays deben tener la misma longitud")
        # Crear el diccionario combinando los dos arrays
        result_dict = dict(zip(array_keys, array_values))
        return result_dict


    def ploting_distribution(self):
        distribution = {}
        for term in self.vocabulary.keys():
            size_posting_list = self.vocabulary[term][1]*LEN_POSTING
            if size_posting_list in distribution:
                distribution[size_posting_list]+=1 # key: Document_frecuency*CantBytes por posting
            else:
                distribution[size_posting_list]=1 # se crea el valor en el dic de distribucion

        sizes = sorted(distribution.keys())
        freqs = [int(distribution[key]) for key in distribution.keys()]

        
        plt.figure(2,figsize=(10, 8))  # Establecer el tamaño de la figura
        plt.plot(sizes, freqs, color='green')
        plt.xlabel("Tamaño de los postings (Bytes)")
        plt.ylabel("Frecuencia")
        plt.savefig(f'{PATH_PLOTS}/postings_distribution.png')
    

    # Retorna el tamaño total en bytes de todos los archivos de un directorio
    def get_size_directory(self,directory):
        total_bytes = 0
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                total_bytes += os.path.getsize(filepath)
        return total_bytes

    # Se Calcula el overhead del índice respecto de la colección
    def overhead_collection(self,dirname):
        # Calculo cantidad total en bytes de todos los documentos usados para la indexacion
        size_index = self.get_size_directory(PATH_INDEX_FILES)
        # Caclulo cantidad total de bytes de todos los documentos indexados
        size_collection = self.get_size_directory(dirname)

        print("Tamaño Coleccion: {} bytes, Tamaño Indice: {} bytes".format(size_collection, size_index))
        print("Overhead: {}".format(size_index / (size_collection + size_index)))

    # Exportado de distribucion de Overhead documentos
    def overhead_documents(self):
        overhead_sizes = {}
        for docid,doc_path in self.list_filenames_to_docid.items():
            file_size = os.path.getsize(doc_path)
            freq_in_postinglist = 0

            for term in self.vocabulary.keys():
                # Obtengo los doc_id de cada termino
                dic_docs=self.convert_array_in_dic(list(self.inverted_index[term][::2]),list(self.inverted_index[term][1::2]))
                
                if dic_docs.get(docid) is not None:
                    freq_in_postinglist += 1 # Si existe incrementamos la frecuencia del doc
                    
            # Cantidad en bytes del id+path, almacenado en el archivo de mapeo
            map_filesids_size = sys.getsizeof(doc_path)+sys.getsizeof(docid) 
            
            # Obtenemos el tamaño en bytes del doc (Tamaño byes en Indice + tamaño total en mapeo id-path)
            total_size = (freq_in_postinglist * LEN_POSTING) + map_filesids_size 
            
            overhead = total_size / (total_size + file_size)

            overhead = round(overhead, 2) #Redondeo

            if overhead in overhead_sizes:
                overhead_sizes[overhead] += 1 # Si el tamaño ya existia se le aumenta la frecuencia
            else:
                overhead_sizes[overhead]=1 # se crea el tamaño en el dic de tamaños de overhead
    
        sizes = sorted(overhead_sizes.keys()) #Ordenamos por tamaños
        cant_docs = [overhead_sizes[key] for key in sizes]

        plt.figure(1)
        plt.plot(sizes, cant_docs)
        plt.xlabel("Overhead")
        plt.ylabel("Cantidad de documentos")
        plt.savefig(f'{PATH_PLOTS}/overhead_documentos.png')

