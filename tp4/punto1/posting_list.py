from special_functions import binary_search
class PostingList:
    docids: list[int]
    scores: list[float]=None
    skips: list[int]=None
    cursor: int=0
    term_id: int=0
    df: int=0
    # searche_method=Method.Naive.value

    def __init__(self,docids,scores,term_id):
        self.docids=docids
        self.scores=scores
        self.term_id=term_id
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

    # Devuelve el docid mayor o igual al recibido por parametro aca, optimizamos por skiplist o binary_Search
    def ge(self,docid:int):
        if self.cursor == -1:
            return None

        if self.search_method == "naive":
            while(self.cursor != -1) and (self.docid()<docid):
                self.next()
            return self.docids[self.cursor] if self.cursor !=-1 else None

        if self.search_method == "binary":
            raise NotImplementedError

        if self.search_method == "skip":
            raise NotImplementedError
    
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
    
    def get_termid(self):
        return self.term_id