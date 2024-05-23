import json
import matplotlib.pyplot as plt
import numpy as np

list_stats = {}
with open('stats.json', 'r') as fp:
    list_stats = json.load(fp)

def main():
    
    # Tiempos promedios totales
    average_times = {}
    for stat in list_stats:
        average_times[stat] = list_stats[stat]["execution_time"]

    average_times = dict(sorted(average_times.items(), key=lambda item: item[1]))

    plt.figure(0, figsize=(20, 8)) 
    plt.plot(average_times.keys(), average_times.values())
    plt.xlabel("Tipo de consultas")
    plt.ylabel("Tiempo de respuesta promedio")
    plt.savefig("times_average")

    # Ploting de Tamaños de las postings vs tiempo de respuesta
    figure_number = 1
    for stat in list_stats:
        execution_time_values = {}
        for query in list_stats[stat]["querys"]:
            execution_time_values[round(query["execution_time"], 5)] = sum(query["postingslist_sizes"])/len(query["postingslist_sizes"])
        
        execution_time_values = dict(sorted(execution_time_values.items(), key=lambda item: item[1]))
        
        plt.figure(figure_number, figsize=(13, 7))
        figure_number += 1
        plt.plot(list(execution_time_values.keys()), list(execution_time_values.values()))
        plt.title(f'{stat}')
        plt.xlabel("Tiempo de respuesta")
        plt.ylabel("Tamaño de las postings")
        plt.savefig(stat)



if __name__ == '__main__':
    main()