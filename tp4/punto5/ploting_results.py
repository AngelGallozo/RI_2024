import json
import matplotlib.pyplot as plt
import numpy as np

list_stats = {}
list_skips_stats = {}

# Abriendo Stats de Skips
with open('stats_skips.json', 'r') as fsk:
    list_skips_stats = json.load(fsk)

# Abriendo Stats comunes del ejercicio 3
with open('../punto3/stats.json', 'r') as fp:
    list_stats = json.load(fp)

def main():
    
    # Tiempos promedios totales
    average_times={}
    average_times['two_term_querys_AND'] = []
    average_times['tree_term_querys_type_ANDS'] = []
    
    for query_data in list_stats["two_term_querys_AND"]["querys"]:
        average_times["two_term_querys_AND"].append(query_data["execution_time"])

    for query_data in list_stats["tree_term_querys_type_ANDS"]["querys"]:
        average_times["tree_term_querys_type_ANDS"].append(query_data["execution_time"])

    # Tiempos promedios totales de skiplist
    skips_average_times = {}
    skips_average_times['two_term_querys_AND'] = []
    skips_average_times['tree_term_querys_type_ANDS'] = []
    for query_data in list_skips_stats["two_term_querys_AND"]["querys"]:
        skips_average_times["two_term_querys_AND"].append(query_data["execution_time"])
        
    for query_data in list_skips_stats["tree_term_querys_type_ANDS"]["querys"]:
        skips_average_times["tree_term_querys_type_ANDS"].append(query_data["execution_time"])


    plt.figure(0, figsize=(20, 8)) 
    plt.plot(average_times["two_term_querys_AND"],label="Naive")
    plt.plot(skips_average_times["two_term_querys_AND"],label="SkipsList")
    plt.legend()
    plt.xlabel("Corridas")
    plt.ylabel("Tiempo (segundos)")
    plt.title('Comparación de tiempos - t1 AND t2')
    plt.savefig("Comparacion_tiempos_2_terms")
    
    plt.figure(1, figsize=(20, 8)) 
    plt.plot(average_times["tree_term_querys_type_ANDS"],label="Naive")
    plt.plot(skips_average_times["tree_term_querys_type_ANDS"],label="SkipsList")
    plt.legend()
    plt.xlabel("Corridas")
    plt.ylabel("Tiempo (segundos)")
    plt.title('Comparación de tiempos - t1 AND t2 AND t3')
    plt.savefig("Comparacion_tiempos_3_terms")


    # Crear el diagrama de caja y bigotes
    plt.figure(2, figsize=(12, 8)) 
    plt.boxplot([skips_average_times["two_term_querys_AND"], average_times["two_term_querys_AND"]], labels=['Skips', 'Naive'])
    plt.ylabel('Tiempo (segundos)')
    plt.ylim(0.000, 0.0030)
    plt.title('Comparación de tiempos - t1 AND t2')
    plt.grid(True)
    plt.savefig("Boxplot_Comparacion_tiempos_2_terms")


    # Crear el diagrama de caja y bigotes
    plt.figure(3, figsize=(12, 8)) 
    plt.boxplot([skips_average_times["tree_term_querys_type_ANDS"], average_times["tree_term_querys_type_ANDS"]], labels=['Skips', 'Naive'])
    plt.ylabel('Tiempo (segundos)')
    plt.ylim(0.000, 0.0030)
    plt.grid(True)
    plt.title('Comparación de tiempos - t1 AND t2 AND t3')
    plt.savefig("Boxplot_Comparacion_tiempos_3_terms")


if __name__ == '__main__':
    main()