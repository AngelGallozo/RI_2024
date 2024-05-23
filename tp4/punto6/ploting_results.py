import json
import matplotlib.pyplot as plt
import numpy as np

stats = {}

with open('statistics.json', 'r') as fp:
    stats = json.load(fp)

def main():
    fig = 0
    for query_type in stats:
        taat_postingsSizes = {}
        daat_postingsSizes = {}
        taat_times = []
        daat_times = []

        for query in stats[query_type]["querys"]:
            taat_times.append(query["taat_time"])
            daat_times.append(query["daat_time"])

            #Ordenando las postinglist_size
            if min(query["postingslist_sizes"]) not in taat_postingsSizes.keys():
                taat_postingsSizes[min(query["postingslist_sizes"])] = [query["taat_time"]]
            else:
                taat_postingsSizes[min(query["postingslist_sizes"])].append(query["taat_time"])
            

            if min(query["postingslist_sizes"]) not in daat_postingsSizes.keys():
                daat_postingsSizes[min(query["postingslist_sizes"])] = [query["daat_time"]]
            else:
                daat_postingsSizes[min(query["postingslist_sizes"])].append(query["daat_time"])
            
        print("{}: TAAT-tiempo_promedio: {}, DAAT-tiempo_promedio: {}".format(query_type, sum(taat_times)/len(taat_times), sum(daat_times)/len(daat_times)))
        fig += 1
        
        plt.figure(fig, figsize=(12, 8)) 
        values = []
        keys = sorted(taat_postingsSizes.keys())
        for key in keys:
            values.append(sum(taat_postingsSizes[key])/len(taat_postingsSizes[key]))
        plt.plot(keys, values)

        values = []
        keys = sorted(daat_postingsSizes.keys())
        for key in keys:
            values.append(sum(daat_postingsSizes[key]) / len(daat_postingsSizes[key]))
        plt.plot(keys, values)

        plt.title(query_type)
        plt.xlabel("Tamaño de la posting mas chica")
        plt.ylabel("Tiempo de respuesta de la consulta")
        plt.legend(['TAAT', "DAAT"])
        # plt.show()
        plt.savefig(query_type)


if __name__ == '__main__':
    main()