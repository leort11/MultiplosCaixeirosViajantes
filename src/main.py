from plot import plot_path
import random

n_cities = 17 # Total possivel: 17 (Incluindo a cidade 0)
n_traveller = 1
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
def find_nearest_city(tours, unvisited, tour_index, cities_per_traveller): 
    return min(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])

# Heuristica de cidade mais distante.
def find_farthest_city(tours, unvisited, tour_index, cities_per_traveller):
    return max(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])


last = -1
def two_close_cities(tours, unvisited, tour_index, cities_per_traveller):
    global last

    # Cidade que nos encontramos. 
    # Pegando a ultima cidade.
    current_city = tours[tour_index][-1]

    # Remove a cidade reservada da lista de não visitadas temporariamente
    if (len(tours[tour_index]) - 1 > 0):
        unvisited = unvisited.copy()
        unvisited.remove(last)

    # Caso seja a ultima viagem vá para a cidade reservada
    if (len(tours[tour_index]) == cities_per_traveller):
        return last
    # Caso seja a penultima viagem, vá para a cidade mais proxima da ultima cidade
    elif (len(tours[tour_index]) == cities_per_traveller - 1):
        # Distancias relativas da ultima cidade, pega a cidade mais proxima da ultima e vai nela
        last_current_distances = [distances[last][x] for x in unvisited]

        # Cidades mais proximas da ultima
        last_closest_cities = [i for i, x in enumerate(distances[last]) if x in sorted(last_current_distances)]

        return last_closest_cities[0]

    # Distancia entre a cidade atual e as cidades restantes
    # current_distances[0] equivale a distancia da cidade atual até a cidade unvisited[0]
    current_distances = [distances[current_city][x] for x in unvisited]

    if (len(tours[tour_index]) - 1 == 0):
        # Aqui pegamos o indice das 2 cidades mais proximas
        closest_cities = [i for i, x in enumerate(distances[current_city]) if x in sorted(current_distances)[:2]]

        random.shuffle(closest_cities)
        next = closest_cities.pop()
        last = closest_cities.pop()
        print(f"Last city: {last}")
    else:
        next = min(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])

    return next

def two_opt(tours):
    best_opt = []
    print("tours: ", tours)
    for tour in tours:
        best_distance = get_total_distance(tour)
        for i in range(1, len(tour) - 2):
            for j in range(i + 1, len(tour) - 1):
                new_tour = tour.copy()
                new_tour[i:j] = new_tour[j - 1:i - 1:-1]
                new_distance = get_total_distance(new_tour)

                if (new_distance < best_distance):
                    best_distance = new_distance
                    best_opt = new_tour

        tour = best_opt
        print(f"tour: {tour} - {best_distance}m")


def two_opt_v2(tours, interations):
    count = 1
    # Melhor rota encontrada
    best_tour = tours.copy()

    # Distancia total da melhor rota encontrada (começa valendo a distancia da rota inicial)
    total_distance = 0

    # Pega a distância do tour (incluindo multiplos caixeiros) e adiciona a variavel
    for tour in tours:
        distance = get_total_distance(tour)
        total_distance += distance

    print(f"Distancia total inicial: {total_distance}m")
    

    for count in range(interations):
        for i in range(1, len(tour) -1):
            # Pega a cidade com qual essa vai criar uma nova rota (Não incluindo cidade inicial e final)
            # Também devemos impedir de que o valor a ser trocado seja o mesmo que a cidade que estamos modificando agora
            sort = i
            while sort == i:
                sort = random.randint(1, len(tour) - 2)

            # best_tour = tours.copy() 

            # Faz a troca de rotas
            tour[i], tour[sort] = tour[sort], tour[i]

            distance = get_total_distance(tour)
            if distance < total_distance:
                # Atualiza a melhor distância
                total_distance = distance

            else:
                # Caso a distância tenha piorado, destroca
                tour[i], tour[sort] = tour[sort], tour[i]


        #print(f"{count}/{interations}")
        count += 1
    
    return total_distance, best_tour
            

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

        # Passa por cada cidade usando a heuristica
        for _ in range(cities_per_traveller, 0, -1):
            next = heuristic(tours, unvisited, tour_index, cities_per_traveller)
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


tours = solution_multiple_travellers(find_nearest_city)

# Para mostrar como era o caminho anteriormente:
# plot_path(distances, tours)

total_distance, best_tour = two_opt_v2(tours, interations=100000)

print(f"{best_tour}: {total_distance}m")
print(f"Distancia total optimizada: {total_distance}m")
print(f"Numero de cidades: {n_cities}")
print(f"Número de caixeiros viajantes: {n_traveller}")

plot_path(distances, best_tour)
