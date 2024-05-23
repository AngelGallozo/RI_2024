import sys
import time
import json
from sri import SRI
from posting_list import PostingList
from constantes import PATH_QUERYS_DUMP_10K
#Instancia el SRI
sist_ri=SRI()
stats = {}

def calc_query_time(query,type_retriev):
    acum = 0
    counter = 0
    for i in range(5):
        start = time.time()
        sist_ri.query_procesing(query,type_retriev)
        end = time.time()
        counter += 1
        acum += end - start

    return acum / counter


def main():
    sist_ri.start()
    print("Generando Estadisticas...")
    query_types = [
    "long_1_term_querys",
    "long_2_term_querys",
    "long_3_term_querys",
    "long_4_term_querys",
    ]

    for query_type in query_types:
        stats[query_type] = {}
        stats[query_type]["querys"] = []

    with open(PATH_QUERYS_DUMP_10K, "r") as f:
        for line in f.readlines():
            terms = line.strip().split(" ")

            query_statistics = {}
            query_statistics["query"] = line.replace("\n","")
            postingslist_sizes = []
            for term in terms:
                postingslist_sizes.append(len(sist_ri.get_posting_list(term).docids))

            query_statistics["postingslist_sizes"] = postingslist_sizes
            query_statistics["taat_time"] = calc_query_time(line, "TAAT")
            query_statistics["daat_time"] = calc_query_time(line, "DAAT")
            stats["long_{}_term_querys".format(len(terms))]["querys"].append(query_statistics)

    #guardamos Resultados
    with open('statistics.json', 'w') as fp:
        json.dump(stats, fp,  indent=4)

    print("Estadisticas Lista.")

if __name__ == '__main__':
    main()