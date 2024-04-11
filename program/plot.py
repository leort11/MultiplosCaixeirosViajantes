import csv
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn import manifold

# Referencias:
# https://baoilleach.blogspot.com/2014/01/convert-distance-matrix-to-2d.html

def plot_path(distances, tours):
    data = distances

    dists = []
    cities = []
    for i, d in enumerate(data):
        #cities.append("City {}".format(i))  # Adicionando nomes fictícios para as cidades
        cities.append(i)
        dists.append(list(map(float, d)))  # Convertendo para lista de floats

    adist = np.array(dists)
    amax = np.amax(adist)
    adist /= amax

    mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)
    results = mds.fit(adist)

    coords = results.embedding_

    plt.subplots_adjust(bottom=0.1)
    plt.scatter(
        coords[:, 0], coords[:, 1], marker='o'
    )

    # for label, x, y in zip(cities, coords[:, 0], coords[:, 1]):
    #     plt.annotate(
    #         label,
    #         xy=(x, y), xytext=(-20, 20),
    #         textcoords='offset points', ha='right', va='bottom',
    #         bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
    #         arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
    #     )

    # Generate random colors for each tour
    tour_colors = ['#%06X' % random.randint(0, 0xFFFFFF) for _ in range(len(tours))]

    # Desenha o tour
    for i, tour in enumerate(tours):
        # Convert to a coord list based on where the cities are situated
        tour_path = [[x, y] for x, y in zip(coords[:, 0], coords[:, 1])]

        for x in range(len(tour)-1):
            city1_index = tour[x]
            city2_index = tour[x+1]
            x1, y1 = tour_path[city1_index]
            x2, y2 = tour_path[city2_index]
            plt.plot([x1, x2], [y1, y2], marker='o', linestyle='-', color=tour_colors[i])

            # Adiciona label para cada ponto do caminho
            plt.annotate(
                f'{x}',
                xy=(x1, y1), xytext=(5, 5),
                textcoords='offset points', ha='right', va='bottom'
            )

            # Mostra a distancia da linha
            # Pega o meio da linha
            x_distance = max(x2, x1) - min(x2, x1)
            y_distance = max(y2, y1) - min(y2, y1)

            coord_x = max(x1, x2) - (x_distance/2)
            coord_y = max(y1, y2) - (y_distance/2)
            line_coord = (coord_x, coord_y)

            plt.annotate(
                f'{distances[city1_index][city2_index]}',
                xy=line_coord, xytext=(5, 5),
                color=(0, 0, 1),
                textcoords='offset points', ha='right', va='bottom'
            )

    plt.show()
