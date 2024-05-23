from special_functions import binary_search
from constantes import K_SKIP,LEN_SKIPLIST

class PostingList:
    docids: list[int]
    scores: list[float]=None
    skips: list[int]=None
    cursor: int=0
    skip_cursor: int=0
    df: int=0
    search_method="naive"

    def __init__(self,docids,scores=[],skips=[]):
        self.docids=docids
        self.scores=scores
        self.skips=skips
        if (len(skips)==0):
            self.skip_cursor = -1
        else:
            self.skip_cursor = 0

        if (len(docids)==0):
            self.cursor = -1
        else:
            self.cursor = 0

        self.df=len(docids)
    
    # Devuelve el docid actual
    def docid(self):
        if self.cursor<0:
            return None
        
        return self.docids[self.cursor]
    
    # Avanza el puntero al siguiente docid(secuencialmente)
    def next_(self):
        if self.cursor < (len(self.docids)-1):
            self.cursor+=1
        else:
            self.cursor=-1
    
    # Devuelve el score que tenga el termino en el docid actual
    def score(self): 
        return self.scores[self.cursor]

    # Avanza el puntero al siguiente docid(utilizando SkipList)
    def next_skiplist(self,docid_search):
        skip_asigned = False
        if (self.skip_cursor!=-1):
            if self.cursor < (len(self.docids)-1):
                docids_skips = self.skips[::2] #Separo los ids
                bytes_positions = self.skips[1::2] #Separo las posiciones
                # Dividir cada elemento por 8 utilizando una comprensión de lista
                positions = [byte_pos // LEN_SKIPLIST  for byte_pos in bytes_positions]

                index=self.skip_cursor
                while (index < len(docids_skips)) and not skip_asigned:
                    if docids_skips[index] >= docid_search:
                        self.cursor = (positions[index]-1)-(K_SKIP-1)
                        self.skip_cursor = index
                        skip_asigned = True 
                    index+=1
                
                if not skip_asigned:
                    if len(docids_skips)>0:                    
                        self.cursor = positions[len(docids_skips)-1]-(K_SKIP-1) # Si no se encontro pero si hay skiplist, que comience desde el final de
                    else:
                        self.cursor=-1
            else:
                self.cursor=-1
        else:
            self.next_() # Si no tiene Skiplist que sume uno y continue modo naive

    # Devuelve el docid mayor o igual al recibido por parametro aca, optimizamos por skiplist
    def ge(self,docid:int):
        if self.cursor == -1:
            return None

        if self.search_method == "naive":
            while(self.cursor != -1) and (self.docid()<docid):
                self.next_()

            return self.docids[self.cursor] if self.cursor !=-1 else None

        if self.search_method == "skip":
                self.next_skiplist(docid)
                return self.docids[self.cursor] if self.cursor !=-1 else None
    
    def _reset(self):
        self.cursor = 0

    #Retorna la lista de docids
    def get_docids(self):
        return self.docids
    
     #Retorna la lista de scores
    def get_scores(self):
        return self.scores
    
    def get_document_frequency(self): 
        return self.df

    #Actualiza el score de una posting por su docid
    def update_score_posting(self,docid,score):
        self.scores[docid]+=score
    
    #Agrega una nueva posting a la lista
    def add_posting(self,docid,score):
        self.docids.append(docid)
        self.scores.append(score)
        self.df+=1

    #Retorna el indice del docid en la lista de docids
    def search_docid(self,docid):
        index = binary_search(self.docids,docid)
        return index
    