from crawler import *
import json
import networkx as nx
import matplotlib.pyplot as plt

def create_pageids(btree):
    pageids={}
    id_acum = 0
    for key in list(btree.keys()):
        if not key in pageids.keys():
                pageids[key] = id_acum
                id_acum += 1
    return pageids

def get_cant_overlap(list1, list2, total_length):
    intersection = list(set(list1).intersection(set(list2)))
    if len(intersection) == 0:
        return 0
    else:
        # return (len(intersection)*100)/total_length
        return len(intersection)/total_length

def plot_overlap(pageIds,btree,crawlingOrderIds):
    G = nx.DiGraph() #Instancio el grafo
    nodes = range(len(pageIds)) #Defino los nodos
    edges = []
    # Defino las aristas
    for key in list(btree.keys()):
        for value in list(btree[key]):
            if value in pageIds.keys():
                edges.append((pageIds[key], pageIds[value]))
    G.add_nodes_from(nodes) # Agrego nodos 
    G.add_edges_from(edges) # Agrego aristas

    pr = nx.pagerank(G, alpha=0.8, max_iter=100) # Obtengo el pagerank para 100 iteraciones con un alfa de 0.8
    h, a = nx.hits(G, max_iter=200) # Obtengo los hub y authorities con un maximo de 200 iteraciones 

    len_rank = len(pr)

    x = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100] # Genero los intervalos porcentuales
    authorityOrder = []
    pagerankOrder = []
    crawlingOrder = []

    authorityOrder_sorted = dict(sorted(a.items(), key=lambda item: item[1]))
    pagerankOrder_sorted = dict(sorted(pr.items(), key=lambda item: item[1]))

    for i in x:
        index = round((i * len_rank) / 100) # Separo cada porcentaje utilizando la longitud total del ranking
        authorityOrder.append(get_cant_overlap(list(authorityOrder_sorted.keys())[:index], list(authorityOrder_sorted.keys())[:index], len_rank))
        pagerankOrder.append(get_cant_overlap(list(authorityOrder_sorted.keys())[:index], list(pagerankOrder_sorted.keys())[:index], len_rank))
        crawlingOrder.append(get_cant_overlap(list(authorityOrder_sorted.keys())[:index], crawlingOrderIds[:index], len_rank))
    
    plt.clf()
    plt.figure(1)

    plt.plot(x, authorityOrder, label="Authority", linestyle='-')  
    plt.plot(x, pagerankOrder, label="PageRank", linestyle='--')  
    plt.plot(x, crawlingOrder, label="Crawling", linestyle=':') 

    plt.title("Comparacion Overlap")
    plt.xlabel("Porcentaje")
    plt.ylabel("Overlap")
    plt.legend()

    plt.savefig("Overlap_plot.png")

if __name__ == '__main__':
    print("Crawling....")
    c=Crawler()
    print("Crawling Finalizado.")
    print("Recuperando Resultados...")
    btree = {} #Obtenemos los datos del json
    with open('btree.json') as json_file:
        btree = json.load(json_file)
    with open('crawling_order.json') as json_file:
        crawling_order = json.load(json_file)
    print("Resultados Recuperados.")
    
    pageIds = create_pageids(btree)
    crawlingOrderIds = []
    for value in crawling_order:
        crawlingOrderIds.append(pageIds[value])
    print("Generando Grafico...")
    plot_overlap(pageIds,btree,crawlingOrderIds)
    print("Grafico generado.")
    