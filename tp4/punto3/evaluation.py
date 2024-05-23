import sys
import time
import json
sys.path.append('../punto2/')
from sri import SRI
from posting_list import PostingList
#Instancia el SRI
sist_ri=SRI()
main_stats = {}


query_to_eval = [
    "two_term_querys_AND",
    "two_term_querys_OR",
    "two_term_querys_NOT",
    "tree_term_querys_type_ANDS", 
    "tree_term_querys_type_OR_NOT", 
    "tree_term_querys_type_AND_OR"]

#Inicializar tiempos
for query in query_to_eval:
    main_stats[query] = {}
    main_stats[query]["querys"] = []
    main_stats[query]["execution_time"] = None
    main_stats[query]["query_count"] = None

# Obtiene los stopwords de un archivo y los devuelven en un array.
def getStopWords(filepath):
    stopwords=[]
    with open(filepath,'r') as f:
        for line in f:
            words_list =  line.strip().split()
            for word in words_list:
                stopwords.append(word)
    return stopwords



def create_query_two_terms(list_terms):
    for symbol in ["AND","OR","NOT"]:
        stats = {}
        stats["query"] = "{} {} {}".format(list_terms[0], symbol, list_terms[1])
        stats["postingslist_sizes"] = [
            sist_ri.get_posting_list(list_terms[0]).get_document_frequency(), 
            sist_ri.get_posting_list(list_terms[1]).get_document_frequency()]
        stats["execution_time"] = None
        main_stats["two_term_querys_{}".format(symbol)]["querys"].append(stats)

def create_query_three_terms(list_terms):
    stats = {}

    stats["query"] = "{} AND {} AND {}".format(list_terms[0], list_terms[1], list_terms[2])
    stats["postingslist_sizes"] = [
        sist_ri.get_posting_list(list_terms[0]).get_document_frequency(), 
        sist_ri.get_posting_list(list_terms[1]).get_document_frequency(), 
        sist_ri.get_posting_list(list_terms[2]).get_document_frequency()]

    stats["execution_time"] = None
    main_stats["tree_term_querys_type_ANDS"]["querys"].append(stats)

    stats = {}
    stats["query"] = "({} OR {})NOT {}".format(list_terms[0], list_terms[1], list_terms[2])
    stats["postingslist_sizes"] = [
        sist_ri.get_posting_list(list_terms[0]).get_document_frequency(), 
        sist_ri.get_posting_list(list_terms[1]).get_document_frequency(), 
        sist_ri.get_posting_list(list_terms[2]).get_document_frequency()]
    stats["execution_time"] = None
    main_stats["tree_term_querys_type_OR_NOT"]["querys"].append(stats)

    stats = {}
    stats["query"] = "({} AND {})OR {}".format(list_terms[0],list_terms[1], list_terms[2])
    stats["postingslist_sizes"] = [
        sist_ri.get_posting_list(list_terms[0]).get_document_frequency(), 
        sist_ri.get_posting_list(list_terms[1]).get_document_frequency(), 
        sist_ri.get_posting_list(list_terms[2]).get_document_frequency()]
    stats["execution_time"] = None
    main_stats["tree_term_querys_type_AND_OR"]["querys"].append(stats)


def calc_query_time(query):
    acum = 0
    counter = 0
    for i in range(10):
        start = time.time()
        sist_ri.query_procesing(query)
        end = time.time()
        counter += 1
        acum += end - start

    return acum / counter




def main():
    stopswords = getStopWords("stopwords.txt")
    sist_ri.retriev_index()
    # Creando querys
    with open("queries.txt", "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            _,query = line.split(":")
            terms = query.split(" ")
            query_terms=[]
            for term in terms:
                if term not in stopswords:
                    query_terms.append(term)
                      
            if len(query_terms) == 2:
                create_query_two_terms(query_terms)
            else:
                if len(query_terms) == 3:
                    create_query_three_terms(query_terms)
    
    print("Querys Procesadas.")

    print("Calculando Stats...")

    #Calcular Stats
    for stat in main_stats:
        counter = 0
        acumulator = 0
        for query in main_stats[stat]["querys"]:
            query_time = calc_query_time(query["query"])
            counter += 1
            acumulator += query_time
            query["execution_time"] = query_time

        main_stats[stat]["execution_time"] = acumulator/counter
        main_stats[stat]["query_count"] = counter
    
    print("Stats Calculados.")
    print("Creando archivo stats...")

    # guardar stats
    with open('stats.json', 'w') as fp:
        json.dump(main_stats, fp,  indent=4)
    print("Archivo stats creado.")

if __name__ == '__main__':
    main()