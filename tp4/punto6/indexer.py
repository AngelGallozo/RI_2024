# Esto descargara los recursos necesarios para utilizar el algoritmo SnowballStemmer para español.
from constantes import PATH_DUMP_10K
from posting_list import PostingList

class Indexer:
    vocabulary = {}
    inverted_index = {}
    
    def __init__(self):
        pass
    
    def indexar(self):
        self.vocabulary = {}
        self.inverted_index = {}
        with open(PATH_DUMP_10K, "r") as f:
            for line in f.readlines():
                term, df, doc_ids = line.split(":")
                doc_ids = doc_ids.strip().split(",")
                if doc_ids[len(doc_ids)-1] == "":
                    doc_ids = doc_ids[:len(doc_ids)-1]

                self.vocabulary[term] = int(df)
                self.inverted_index[term] =  PostingList(docids=sorted(list(map(int, doc_ids))))

    def get_inverted_index(self):
        return self.inverted_index
    
    def get_vocabulary(self):
        return self.vocabulary