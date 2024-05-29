from crawler import *
import matplotlib.pyplot as plt


def is_dinamic_link(link):
    response = False
    for ch in ["?", "&", "%", "+", "=", "$", "cgi-bin", ".cgi"]:
        if ch in link:
            response = True
            break
    return response

def plot_distr_dinamic_and_static(btree):
    statics = 0
    dinamics = 0
    for key_link in btree:
        if is_dinamic_link(key_link):
            dinamics += 1
        else:
            statics += 1
        for link_inside in btree[key_link]["links"]:
            if is_dinamic_link(link_inside):
                dinamics += 1
            else:
                statics += 1
    
    # Realizamos grafico 
    plt.clf()
    plt.figure(1)
    labels = 'Dinamicas', 'Estaticas'
    sizes = [dinamics, statics]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    plt.savefig("Ditribucion_paginas_dinamicas_y_estaticas.png")

def plot_distr_freqs_logical_depth(btree):
    depths = []
    for key_link in btree:
        depths.append(btree[key_link]["depth"])

    plt.clf()
    plt.figure(2)
    plt.hist(depths, range=(min(depths), max(depths)))
    plt.xlabel("Profundidad_Logica")
    plt.ylabel("Frecuencias")
    plt.savefig("Distribucion_frecuencias_profundidad_logica.png")


def get_physical_depth(link):
        path = urlparse(link).path
        return path.count("/")

def plot_distr_freqs_physical_depth(btree):
    depth_dict = {}
    depths = []
    for key_link in btree:
        try:
            depth_dict[get_physical_depth(key_link)] += 1
        except:
            depth_dict[get_physical_depth(key_link)] = 1
        depths.append(get_physical_depth(key_link))
        for value in btree[key_link]["links"]:
            depths.append(get_physical_depth(value))
            try:
                depth_dict[get_physical_depth(value)] += 1
            except:
                depth_dict[get_physical_depth(value)] = 1

    plt.clf()
    plt.figure(4)
    plt.hist(depths, bins=len(depth_dict.keys()))
    plt.xlabel("Profundidad_Fisica")
    plt.ylabel("Frecuencias")
    plt.savefig("Distribucion_frecuencias_profundidad_fisica.png")



if __name__ == '__main__':
    print("Crawling....")
    c=Crawler()
    print("Crawling Finalizado.")
    print("Recuperando Resultados...")
    btree = {} #Obtenemos los datos del json
    with open('stats_btree.json') as json_file:
        btree = json.load(json_file)
    print("Resultados Recuperados.")
    #Plots
    print("Exportando Graficos...")
    plot_distr_dinamic_and_static(btree)
    plot_distr_freqs_logical_depth(btree)
    plot_distr_freqs_physical_depth(btree)
    print("Graficos Exportados.")
