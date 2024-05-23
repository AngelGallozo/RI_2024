import os
import struct #utilizo el formato de 4 bytes ('i') 
from os import listdir
from os.path import join, isdir
from constantes import PATH_CHUNKS,PATH_POSTINGLIST,LEN_POSTING_CHUNK,LEN_POSTING

class Merger:

    def __init__(self):
        pass 


    # Hace el merge de todos los chunks
    def merger_chunk(self,terms2id,list_chunks):
        vocabulary = {}
        final_posting_list_start=0
        if isdir(PATH_CHUNKS):
            cant_chunks = len(listdir(PATH_CHUNKS))
            with open(PATH_POSTINGLIST, 'wb') as f:
                inverted_index={}
                for term in terms2id:
                    if not(term in inverted_index):
                        inverted_index[term]={} # genero un indice invertido para el calculo de overhead

                    final_document_frequency=0
                    final_posting_list=[]
                    for chunkid,terms_chunk in list_chunks.items():
                        if not(term in terms_chunk):
                            continue # Si el termino no esta en la chunk continua al siguiente chunk
                        #Si existe en el chunk, obtengo puntero_inicial y df
                        posting_start,document_frequency= list_chunks[chunkid][term]
                        # Acumulo lode df totales del termino
                        final_document_frequency+=document_frequency
                        # Agrego la posting del chunk a la posting final                        
                        final_posting_list.extend(list(self.read_posting_in_chunk(chunkid,posting_start,document_frequency)))
                    
                    inverted_index[term]= final_posting_list
                    # Insertamos la postinglist final en disco    
                    encoded = struct.pack(f'>{len(final_posting_list)}I',*final_posting_list)
                    f.write(encoded)
                    # Guardamos la postinglist final del termino en el vocabulario
                    vocabulary[term]=[final_posting_list_start,final_document_frequency]
                    # Recalculo el puntero para la siguiente escritura
                    final_posting_list_start+=final_document_frequency*LEN_POSTING

        return vocabulary,inverted_index
                
    # Lee una posting segun el chunk y la ubicacion en el archivo
    def read_posting_in_chunk(self,chunkid,posting_start,document_frequency):
        filepath_chunk = join(PATH_CHUNKS,f'chunk-{chunkid}.bin') 
        with open(filepath_chunk, "rb") as f:
            
            # Mover el puntero de lectura al inicio de la posición deseada
            f.seek(posting_start)

            # Leer los datos binarios desde esa posición
            _bytes= f.read(document_frequency * LEN_POSTING_CHUNK)

            # Desempaquetar los datos binarios en enteros
            unpacked_data = struct.unpack(f'>{document_frequency*2}I', _bytes)
    
            return unpacked_data
