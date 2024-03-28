from plot import plot_path

n_cities = 17 # Total possivel: 17 (Incluindo a cidade 0)
n_traveller = 2
distances = [
    [ 0,   548,  776,  696,  582,  274,  502,  194, 308,  194, 536,  502,  388,  354,  468,  776,  662  ],
    [ 548, 0,    684,  308,  194,  502,  730,  354, 696,  742, 1084, 594,  480,  674,  1016, 868,  1210 ],
    [ 776, 684,  0,    992,  878,  502,  274,  810, 468,  742, 400,  1278, 1164, 1130, 788,  1552, 754  ],
    [ 696, 308,  992,  0,    114,  650,  878,  502, 844,  890, 1232, 514,  628,  822,  1164, 560,  1358 ],
    [ 582, 194,  878,  114,  0,    536,  764,  388, 730,  776, 1118, 400,  514,  708,  1050, 674,  1244 ],
    [ 274, 502,  502,  650,  536,  0,    228,  308, 194,  240, 582,  776,  662,  628,  514,  1050, 708  ],
    [ 502, 730,  274,  878,  764,  228,  0,    536, 194,  468, 354,  1004, 890,  856,  514,  1278, 480  ],
    [ 194, 354,  810,  502,  388,  308,  536,  0,   342,  388, 730,  468,  354,  320,  662,  742,  856  ],
    [ 308, 696,  468,  844,  730,  194,  194,  342, 0,    274, 388,  810,  696,  662,  320,  1084, 514  ],
    [ 194, 742,  742,  890,  776,  240,  468,  388, 274,  0,   342,  536,  422,  388,  274,  810,  468  ],
    [ 536, 1084, 400,  1232, 1118, 582,  354,  730, 388,  342, 0,    878,  764,  730,  388,  1152, 354  ],
    [ 502, 594,  1278, 514,  400,  776,  1004, 468, 810,  536, 878,  0,    114,  308,  650,  274,  844  ],
    [ 388, 480,  1164, 628,  514,  662,  890,  354, 696,  422, 764,  114,  0,    194,  536,  388,  730  ],
    [ 354, 674,  1130, 822,  708,  628,  856,  320, 662,  388, 730,  308,  194,  0,    342,  422,  536  ],
    [ 468, 1016, 788,  1164, 1050, 514,  514,  662, 320,  274, 388,  650,  536,  342,  0,    764,  194  ],
    [ 776, 868,  1552, 560,  674,  1050, 1278, 742, 1084, 810, 1152, 274,  388,  422,  764,  0,    798  ],
    [ 662, 1210, 754,  1358, 1244, 708,  480,  856, 514,  468, 354,  844,  730,  536,  194,  798,  0    ]
]


def get_total_distance(tour : list):
    total_distance = 0

    for i in range(len(tour) - 1):
        total_distance = total_distance + distances[tour[i]][tour[i + 1]]
    
    return total_distance

# Heuristica de cidade mais proxima.
def find_nearest_city(tours, unvisited, tour_index): 
    return min(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])

# Heuristica de cidade mais distante.
def find_farthest_city(tours, unvisited, tour_index):
    return max(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])

def solution_multiple_travellers(heuristic):
    global n_traveller

    # Verifica se tem mais caixeiros do que cidades
    n_traveller_remaining = 0 # Numero de caixeiros viajantes que não farão nada
    if (n_traveller > n_cities - 1):
        n_traveller_remaining = n_traveller - (n_cities - 1)
        n_traveller = n_cities - 1 # Limita o numero de caixeiros para o numero de cidade
    
    # Cria um tour para cada caixeiro
    # Cada caixeiro vai começar com a cidade 0 já visitada
    tours = [[0] for _ in range(n_traveller)]

    # São as cidades que os caixeiros vão ter que visitar
    unvisited = list(range(1, n_cities))

    # Quantidade de cidade que cada caixeiro vai visitar (Tirando a 0)
    cities_per_traveller = (n_cities - 1)/n_traveller

    # Verifica se o numero de cidades por viajante é quebrado/decimal
    # Se sim, o ultimo caixeiro irá visitar uma cidade a mais
    decimal_number = False
    if (not cities_per_traveller.is_integer()):
        decimal_number = True
    cities_per_traveller = int(cities_per_traveller) # Converte denovo para um numero inteiro (arredondando para baixo)

    # Passa por cada caixeiro
    for tour_index in range(len(tours)):
        # Caso seja a ultima viagem e é um número quebrado, aumentar esta viajem por 1
        if (tour_index == len(tours) - 1 and decimal_number):
            cities_per_traveller += 1

        # Passa por cada cidade
        for city_index in range(cities_per_traveller, 0, -1):
            next = heuristic(tours, unvisited, tour_index)
            tours[tour_index].append(next)
            unvisited.remove(next)

        # Adiciona a cidade 0 já que tem que voltar pra ela
        tours[tour_index].append(0)

    # Adiciona os caixeiros que não vão fazer nada para a lista
    for _ in range(n_traveller_remaining):
        tours.append([0])

    # Atualiza denovo a variavel que mudou temporariamente para o numero limite.
    n_traveller += n_traveller_remaining
    
    # vai retornar: [0, 7, 5, 8, 6, 2, 10, 9], [0, 13, 12, 11, 15, 3, 4, 1] (exemplo com 2 caixeiros e 16 cidades)
    return tours


tours = solution_multiple_travellers(find_farthest_city)
total_distance = 0
for tour in tours:
    #  tour1: [0, 7, 5, 8, 6, 2, 10, 9]
    #  tour2: [0, 13, 12, 11, 15, 3, 4, 1]
    distance = get_total_distance(tour)

    print(f"{tour}: {distance}m")
    total_distance += distance

print(f"Distancia total: {total_distance}m")
print(f"Numero de cidades: {n_cities}")
print(f"Número de caixeiros viajantes: {n_traveller}")

plot_path(distances, tours)