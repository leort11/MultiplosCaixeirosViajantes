import math
import os

FOLDER_PATH = "instances/"

#def calculate_euclidean_distance_prof(x1, y1, x2, y2):
#    return math.sqrt((x1 - y1)**2 + (x2 - y2)**2)

def calculate_euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Este arquivo pega uma das intancias e gera uma lista de distancias para cada cidade
def generate_distances(filename: str):
    filepath = FOLDER_PATH + filename
    print(f"Gerando distâncias do arquivo: {filename}")

    # Coordenadas de cada cidade, se usa city_coords[index_da_cidade] = coordenada
    city_coords = []

    # Lê o arquivo especificado e pega as coordenadas
    with open(filepath, "r") as f:
        for line in f:
            coords = []
            split_line = line.split(" ")

            # Trata a linha e pega as informações necessárias
            for i, word in enumerate(split_line):
                # Pula a primeira linha que não é nada demais, é o indice da cidade
                if i == 0:
                    continue

                word = word.strip()

                # Pula a linha se for vazia (espaço)
                if word == "":
                    continue

                word = int(word)

                coords.append(word)
            city_coords.append(coords)

    # Passa por cada cidade, e verifica a distância entre cada uma e todas as outras
    # E assim uma matriz simétrica de distâncias vai se formando
    distances_matrix = [[-1 for _ in range(len(city_coords))] for _ in range(len(city_coords))]

    for city_index in range(len(city_coords)):
        for city2_index in range(len(city_coords)):
            # Se for a mesma cidade então obviamente a distância é zero
            if city2_index == city_index:
                distances_matrix[city_index][city2_index] = 0
                continue

            x1, y1 = city_coords[city_index]
            x2, y2 = city_coords[city2_index]
            
            # Procura a distancia euclidiana entre a cidade 1 e 2
            # Pega a distância e converte em um número inteiro
            dist = math.ceil(calculate_euclidean_distance(x1, y1, x2, y2))
            distances_matrix[city_index][city2_index] = dist

    # Quantidade de caixeiros viajantes
    m = str(os.path.basename(filepath)) # Nome do arquivo

    # Pega a quantidade de caixeiros
    m = int(m.split("-")[-1][1:])

    print(f"Geradas com sucesso!\n")

    return distances_matrix, m
