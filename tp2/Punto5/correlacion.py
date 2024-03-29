import sys
import pathlib
import numpy as np
from os import listdir
from os.path import join, isdir


def initialize(vector_dict,tag):
    vector_dict[tag] = {}    
    for i in range(1, 6):
        vector_dict[tag][i] = []

def procesar_files(dirname):
    retrieved_documents = {}
    for filename in listdir(dirname):
        filepath = join(dirname, filename)
        tag = filename.replace("_RANK.txt","")
        print(f"Processing file: {filepath}")
        with open(filepath,'r',encoding='utf-8') as f:
            initialize(retrieved_documents,tag)
            for line in f:
                query_number, doc_id, doc_no, rank, score, *query = line.split()
                retrieved_documents[tag][int(query_number)].append([int(doc_id),float(score)])
            
    return retrieved_documents

def main():
    if len(sys.argv) < 1:
        print('Es necesario pasar como argumento: dir_resultados')        
        sys.exit(0)
    dirname= sys.argv[1]
    ranking_docs = procesar_files(dirname)
    tag_1,tag_2 = ranking_docs.keys()
    rank_1 = []
    rank_2 = []
    print("Procesando: Rank_"+tag_1+"    Rank_"+tag_2)
    for i in range(1, 6):
        rank_1 = ranking_docs[tag_1][i][:50]
        rank_2 = ranking_docs[tag_2][i][:50]
        rank_1 = np.array(rank_1)[:, 1]
        rank_2 = np.array(rank_2)[:, 1]
        
        print("Query["+str(i)+"]: ")
        print("--------------------------------------")
        print("Correlacion: 10 resultados")
        correlation_matrix = np.corrcoef(rank_1[:10], rank_2[:10])
        correlation = correlation_matrix[0, 1]
        print("Coe: "+ str(correlation)+"\n")
        print("Correlacion: 25 resultados")
        correlation_matrix = np.corrcoef(rank_1[:25], rank_2[:25])
        correlation = correlation_matrix[0, 1]
        print("Coe: "+ str(correlation)+"\n")
        print("Correlacion: 50 resultados")
        correlation_matrix = np.corrcoef(rank_1[:50], rank_2[:50])
        correlation = correlation_matrix[0, 1]
        print("Coe: "+ str(correlation))
        print("--------------------------------------")

    print("Diferencias en rankings: Docs id y sus scores")
    index = 0
    rank_1 = ranking_docs[tag_1][i][:50]
    rank_2 = ranking_docs[tag_2][i][:50]
    print("Pos - Doc_1 <> Doc_2 - score_Doc_1 <> score_Doc_2")
    print("-------------------------------------------------")
    for rank in rank_1:
        if(rank[0] != rank_2[index][0]):
            id_doc_1 = rank[0]
            score_doc_1= rank[1]
            id_doc_2 = rank_2[index][0]
            score_doc_2= rank_2[index][1]
            
            print("["+str(index+1)+"] "+str(id_doc_1)+" "+str(id_doc_2)+" "+str(score_doc_1)+" "+str(score_doc_2))
        index +=1
        

if __name__ == '__main__':
    main()
    