import struct #utilizo el formato de 4 bytes ('i') 
import pickle
import os
import matplotlib.pyplot as plt# graficos
import time
from constantes import USE_DGAPS,LEN_POSTING,PATH_POSTINGLIST,PATH_VOCABULARY,PATH_COMPRESSED_BLOCKIDS,PATH_COMPRESSED_BLOCKFREQS,LEN_DOCID,LEN_FREQ
from posting_list import PostingList
from bitarray import bitarray #Para la compresion
from bitstring import BitArray #Para la descompresion
import math

class SRI:
    vocabulary={}# Tabla Term - DF - Puntero
    inverted_index={}
    bytes_size_block_docids = 0
    bytes_size_block_freqs = 0

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
                if not USE_DGAPS:
                    self.inverted_index[term] = PostingList(docids=list(unpacked_data[::2]), scores=list(unpacked_data[1::2]))
                else:
                    docids = unpacked_data[::2]
                    dgaps=[docids[0]]
                    next_docid=0
                    for i in range(0,len(docids)-1):
                        dgaps.append(abs(docids[i]-docids[i+1]))

                    self.inverted_index[term] = PostingList(docids=dgaps, scores=list(unpacked_data[1::2]))
                    
                self.bytes_size_block_docids += LEN_DOCID * len(self.inverted_index[term].docids)
                self.bytes_size_block_freqs += LEN_FREQ * len(self.inverted_index[term].scores)
    
    def retriev_index(self):
        print("Recuperando Vocabulario...")
        self.load_vocabulary()
        print("Vocabulario Recuperado.\n")
        print("Reconstruyendo Indice...")
        self.read_inverted_index()
        print("Indice Recuperado.\n")
        if USE_DGAPS:
            print("D-GAPS generado.\n")

        print(f'Tamaño del Bloque Indice: {self.bytes_size_block_docids} bytes.')
        print(f'Tamaño del Bloque Frecuencias: {self.bytes_size_block_docids} bytes.\n')
        print("Comprimiendo Bloque_Docids con Variable Length...")
        start = time.time()
        self.compress_block_ids()
        end = time.time()
        print("Bloque_Docids Comprimido.")
        print("Tiempo de Compresion: {} segs.".format(end - start))
        print(f'Tamaño del Bloque: {os.path.getsize(PATH_COMPRESSED_BLOCKIDS)} bytes\n')

        print("Comprimiendo Bloque_freqs con Elias-gamma...")
        start = time.time()
        self.compress_block_freqs()
        end = time.time()
        print("Bloque_Freqs Comprimido.")
        print("Tiempo de Compresion: {} segs.".format(end - start))
        print(f'Tamaño del Bloque: {os.path.getsize(PATH_COMPRESSED_BLOCKFREQS)} bytes\n')
        
        # for pl,data in self.inverted_index.items():
        #     print(f'{pl}: {data.docids} , Scores: {data.scores}')

    # Devuelve la posting list en memoria
    def get_posting_list(self,term):
        if(len(term)<1 or term.isspace()):
            print("\n\n (!)Error termino vacio, no valido.\n\n")
        else:
            if term in self.inverted_index:
                return self.inverted_index[term]
        
        return PostingList(docids=[],scores=[]) 


    def variable_length_compress(self,n):
        final_binary = ''

        if n < 128:  # Se ajusta para un byte
            binary = bin(n)[2:]  # Convertir a binario
            # Si la longitud del binario es < 7, se agregan 0s a la izquierda.
            if len(binary) < 7:
                binary = '0' * (7 - len(binary)) + binary
            # Se agrega un bit adicional para indicar el final
            binary = '1' + binary
            final_binary = binary
        else:
            length = len(bin(n)[2:])  # Longitud del binario
            binary = bin(n)[2:]  # Convertir a binario
            lower_bits = int('1' + binary[length - 7:])  # Se toman los últimos 7 bits
            higher_bits = ''
            binary = binary[::-1]
            # Se divide en segmentos de 7 bits y se invierten
            for i in range(7, length, 7):
                higher_bits = binary[i:i + 7]
                higher_bits = higher_bits[::-1]
                if len(higher_bits) < 8:
                    higher_bits = '0' * (8 - len(higher_bits)) + higher_bits
                final_binary = higher_bits + final_binary
            final_binary += str(lower_bits)
        return final_binary

    def decompress_variable_length(self,data):
        bin_data = BitArray(data)
        binary = bin_data.bin
        doc_ids = []
        bin_acumulator = ""
        while binary != '':
            end_of_number = int(binary[0]) == 1
            bin_acumulator += binary[1:8]
            binary = binary[8:]
            if end_of_number:
                doc_ids.append(int(bin_acumulator, 2))
                bin_acumulator = ""
        return doc_ids

    def binario(self, x):
        return bin(x).replace("0b", "")

    def unario(self, x):
        return "1"*(x-1)+"0"

    def rmsb(self, bin_x):
        return bin_x[1:]

    def elias_gama_compress(self, freq):
        binario = self.binario(freq)
        len_bin = len(self.binario(freq))
        u = self.unario(len_bin)
        rmsb = self.rmsb(binario)
        return u+rmsb


    def compress_block_ids(self):
        pointer_acum = 0
        compressed_block_docids_file = open(PATH_COMPRESSED_BLOCKIDS, 'wb')
        for term, posting_list in self.inverted_index.items():
            postings_lists_encoded = ""
            
            for docid in posting_list.docids:
                docid_encoded = self.variable_length_compress(docid) 
                postings_lists_encoded += docid_encoded
            
            postings_lists_encoded = bitarray(postings_lists_encoded)
            compressed_block_docids_file.write(postings_lists_encoded)
            pointer = pointer_acum
            pointer_acum += len(postings_lists_encoded)//8
            self.vocabulary[term].extend([pointer,len(postings_lists_encoded)])


    def compress_block_freqs(self):
        pointer_acum = 0
        compressed_block_freqs_file = open(PATH_COMPRESSED_BLOCKFREQS, 'wb')
        for term, posting_list in self.inverted_index.items():
            postings_freqs_encoded = ""
            
            for freq in posting_list.scores:
                freqs_encoded = self.elias_gama_compress(freq) 
                postings_freqs_encoded += freqs_encoded
            
            len_before_padding = len(postings_freqs_encoded)
            rest = len(postings_freqs_encoded) % 8
            if rest != 0:
                padding = 8 - rest
                postings_freqs_encoded = ("0" * padding) + postings_freqs_encoded
            postings_freqs_encoded = bitarray(postings_freqs_encoded)
            compressed_block_freqs_file.write(postings_freqs_encoded)
            pointer = pointer_acum
            pointer_acum += len(postings_freqs_encoded)//8
            self.vocabulary[term].extend([pointer,len_before_padding])

    
    def decompress_unary(self, data, zero=True):
        if zero:
            acum = 0
        else:
            acum = 1
        for i in data:
            if int(i) == 1:
                acum += 1
            else:
                return acum
    
    def decompress_elias_gamma(self, compressed_bits,padding):
        freqs = []
        bin_data = BitArray(compressed_bits)
        binary = bin_data.bin

        binary = binary[padding:]

        while binary != "":
            if int(binary[0]) == 0:
                binary = binary[1:]
                unary_part = "0"
            else:
                i = 0
                unary_part = ""
                while int(binary[i]) != 0:
                    unary_part += binary[i]
                    i += 1
                binary = binary[i+1:]
                unary_part += "0"
            bits_to_read = self.decompress_unary(unary_part)
            rmsb = "1"
            for i in range(bits_to_read):
                rmsb += binary[i]
            freqs.append(int(rmsb, 2))
            binary = binary[bits_to_read:]
        return freqs

    def get_postinglist_varaible_length(self,term):
        with open(PATH_COMPRESSED_BLOCKIDS, "rb") as f:
            _, _, pointer_docid_compressed, cantbits_docid_compressed,_,_ = self.vocabulary[term]
            f.seek(pointer_docid_compressed)
            data_encode = f.read(cantbits_docid_compressed // 8)
            docids = self.decompress_variable_length(data_encode)
        return docids

    def get_postinglist_elias_gamma(self,term):
        freqs = []
        with open(PATH_COMPRESSED_BLOCKFREQS, 'rb') as compressed_file:
            _, _,_,_, pointer_freq_compressed, cantbits_freq_compressed= self.vocabulary[term]
            compressed_file.seek(pointer_freq_compressed)
            
            rest = (cantbits_freq_compressed % 8)
            if rest != 0:
                padding = 8 - rest
            else:
                padding = 0
            
            compressed_bits = compressed_file.read((cantbits_freq_compressed + padding) // 8)
            freqs = self.decompress_elias_gamma(compressed_bits,padding)

        return freqs


    def evaluation_compression(self):
        start = time.time()
        for term in self.vocabulary.keys():
            docids = self.get_postinglist_varaible_length(term)
            # print(docids)
        end = time.time()
        print("Descompresion Bloque Docids - Variable Length: {} segs.".format(end - start))

        start = time.time()
        for term in self.vocabulary.keys():
            freqs = self.get_postinglist_elias_gamma(term)
            # print(freqs)
        end = time.time()
        print("Descompresion Bloque Freqs - Elias Gamma: {} segs.".format(end - start))
