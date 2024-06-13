# app.py
from crawler import *
import matplotlib.pyplot as plt
from urllib.parse import urlparse
import json

def is_dynamic_link(link):
    return any(ch in link for ch in ["?", "&", "%", "+", "=", "$", "cgi-bin", ".cgi"])

def plot_distr_dynamic_and_static(btree):
    statics = 0
    dynamics = 0
    for key_link in btree:
        if is_dynamic_link(key_link):
            dynamics += 1
        else:
            statics += 1

    # Realizamos grafico 
    plt.clf()
    plt.figure(1)
    labels = 'Dinámicas', 'Estáticas'
    sizes = [dynamics, statics]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    plt.savefig("Distribucion_paginas_dinamicas_y_estaticas.png")

def plot_distr_freqs_logical_depth(btree):
    depths = []
    for key_link in btree:
        depths.append(btree[key_link]["depth"])
  
    plt.clf()
    plt.figure(2)
    plt.hist(depths, bins=range(min(depths), max(depths) + 1))
    plt.xlabel("Profundidad Lógica")
    plt.ylabel("Frecuencias")
    plt.savefig("Distribucion_frecuencias_profundidad_logica.png")

def get_physical_depth(link):
    path = urlparse(link).path
    return path.count("/")

def plot_distr_freqs_physical_depth(btree):
    depth_dict = {}
    for key_link in btree:
        physical_depth = get_physical_depth(key_link)
        depth_dict[physical_depth] = depth_dict.get(physical_depth, 0) + 1

    plt.clf()
    plt.figure(4)
    plt.hist(list(depth_dict.keys()), weights=list(depth_dict.values()), bins=len(depth_dict.keys()))
    plt.xlabel("Profundidad Física")
    plt.ylabel("Frecuencias")
    plt.savefig("Distribucion_frecuencias_profundidad_fisica.png")

if __name__ == '__main__':
    print("Crawling....")
    c = Crawler()
    print("Crawling Finalizado.")
    print("Recuperando Resultados...")
    with open('stats_btree.json') as json_file:
        btree = json.load(json_file)
    print("Resultados Recuperados.")
    # Plots
    print("Exportando Gráficos...")
    plot_distr_dynamic_and_static(btree)
    plot_distr_freqs_logical_depth(btree)
    plot_distr_freqs_physical_depth(btree)
    print("Gráficos Exportados.")
