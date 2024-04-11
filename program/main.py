from plot import plot_path
from generate_distances import generate_distances
import random
import math
from decimal import Decimal

# Essa seed força um bug a acontecer na rota "mTSP-n91-m5" (investigar)
# Especificamente quanto usa o codigo de pegar a penultima cidade como sendo a mais perto da ultima
# Por algum motivo uma função de uma linha pega a cidade 2 duas vezes, mesmo que na segunda vez a cidade 2 nao esteja na lista de unvisited
# random.seed(12556)

# Caso não seja o arquivo principal nem roda esse codigo
distances, n_traveller = None, None
n_cities = -1

if __name__ == "__main__":
    distances, n_traveller = generate_distances("mTSP-n71-m5")
    n_cities = len(distances)

def get_total_distance(tour : list):
    total_distance = 0

    # Caso tour seja uma lista de listas, quer dizer que total tour armazena o tour de varios caixeiros viajantes
    if type(tour[0]) is list:
        for t in tour:
            for i in range(len(t) - 1):
                total_distance = total_distance + distances[t[i]][t[i + 1]]
    # Caso não seja uma lista de listas, presumi que é simplesmente o tour do caixeiro viajante
    else:
        for i in range(len(tour) - 1):
            total_distance = total_distance + distances[tour[i]][tour[i + 1]]
    
    return total_distance

# Heuristica de cidade mais proxima.
def find_nearest_city(tours, unvisited, tour_index, cities_per_traveller, distances=distances): 
    return min(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])

# Heuristica de cidade mais distante.
def find_farthest_city(tours, unvisited, tour_index, cities_per_traveller, distances=distances):
    return max(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])


last = -1
def two_close_cities(tours, unvisited, tour_index, cities_per_traveller, distances=distances, return_last=False):
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

        if return_last:
            return last, last
    
        return last
    
    # Caso seja a penultima viagem, vá para a cidade mais proxima da ultima cidade
    # Este codigo esta dando algum erro por algum motivo, mas não é obrigatorio executar esta parte
    # elif (len(tours[tour_index]) == cities_per_traveller - 1):
    #     # Distancias relativas da ultima cidade, pega a cidade mais proxima da ultima e vai nela
    #     last_current_distances = [distances[last][x] for x in unvisited]

    #     # Cidades mais proximas da ultima
    #     last_closest_cities = [i for i, x in enumerate(distances[last]) if x in sorted(last_current_distances)]

    #     # DEBUG
    #     if last_closest_cities[0] == 2:
    #         print(unvisited)
    #         #print(last_closest_cities)
    #         #print(last_closest_cities)
    #         #print(last_closest_cities[0])

    #     return last_closest_cities[0]

    # Distancia entre a cidade atual e as cidades restantes
    # current_distances[0] equivale a distancia da cidade atual até a cidade unvisited[0]
    current_distances = [distances[current_city][x] for x in unvisited]

    if (len(tours[tour_index]) - 1 == 0):
        # Aqui pegamos o indice das 2 cidades mais proximas
        closest_cities = [i for i, x in enumerate(distances[current_city]) if x in sorted(current_distances)[:2]]

        random.shuffle(closest_cities)
        next = closest_cities.pop()
        last = closest_cities.pop()
    else:
        next = min(unvisited, key = lambda candidate : distances[tours[tour_index][-1]][candidate])

    if return_last:
        return next, last

    return next

def three_opt(tours, iterations, debug_print=False):
    # Este dicionario armazena informações extras sobre este processo, é retornado no final
    extra_info = {
        "times_improved": -1,
        "swaps_amount": -1
    }

    # Se tours não for uma lista de lista, então transforma em uma lista unica dentro deu uma lista para não dar erros
    is_multiple_tours = True
    if type(tours[0]) != list:
        is_multiple_tours = False
        tours = [tours]

    extra_info["swaps_amount"] =  iterations * sum(len(tour) - 1 for tour in tours)
    if debug_print:
        print(f"Quantidade de swaps: {extra_info["swaps_amount"]}")
    

    def lerp(A, B, t):
        return A * (1 - t) + B * t
    
    # Configuração
    initial_temperature = 1 #0.75 # 1 = Apenas decisões ruim, # 0.5 Meio termo, # 0 Nunca aceita decições ruim
    #temperature_decay = 0.005
    bad_threshold = 0.43 # Se for X porcento pior que a melhor distancia, entao volta pra melhor distancia 0.01 = 1%
    # 0.4-0.45 Notei que é um bom valor em geral

    # Configuração (EXTRA)
    final_temperature = 0.00001

    # Codigo
    temperature = initial_temperature

    # Distancia total da melhor rota encontrada (começa valendo a distancia da rota inicial)
    total_distance = get_total_distance(tours)

    if debug_print:
        print(f"Distancia total inicial: {total_distance}m")

    # Para que seja possivel mudar as rotas entre diferentes caixeiros viajantes, vamos subdividir as rotas dele em uma lista gigante com todas as rotas
    # excluindo a cidade 0 (com exceção da inicial e final)
    # Uma lista como [[0, 5, 4, 0], [0, 3, 2, 0], [0, 1, 6, 0]] seria [0, 5, 4, 3, 2, 1, 6, 0]
    # O primeiro caixeiro contaria com as posições 1 e 2, o segundo 3 e 4, e o terceiro 5 e 6 respectivamente
    # Na hora de testar a distância de todas as rotas, descompactamos a lista devolta no estado inicial dela
    # Então [0, 5, 4, 3, 2, 1, 6, 0] vira [[0, 5, 4, 0], [0, 3, 2, 0], [0, 1, 6, 0]]
    # Isso funcionará mesmo com tours com tamanhos diferente
    
    # Exemplo
    # Rota descompactada: [[0, 2, 3, 5, 0], [0, 1, 4, 0], [0, 7, 8, 0]]
    # Rota compactada   : [0, 2, 3, 5, 1, 4, 7, 8, 0]
    # Nota-se que os indices são pertencentes aos seguintes caixeiros: 1-3 Primeiro caixeiro, 4-5 Segundo caixeiro; e 6-7 ultimo caixeiro
    # Tiramos a cidade 0 da equação porque elas nunca são trocadas de lugar com nenhuma outra

    # Cidades por caixeiro (Não contando com as cidades 0)
    cities_per_traveller_list = [len(x) - 2 for x in tours] 

    # Funções que vão facilitar o processo de descompactar e compactar uma rota
    def merge_tours(tours):
        # Se tours nao for uma lista de lista então nem tenta fazer nada
        if type(tours[0]) != list:
            return tours

        # Começa uma lista com a cidade inicial apenas
        merged = [tours[0][0]]

        # Não armazena a cidade inicial
        for i in range(len(tours)):
            for city in range(1, len(tours[i]) - 1):
                merged.append(tours[i][city])

        # Finaliza a lista com a cidade final
        merged.append(tours[0][-1])

        return merged
    
    # Descompacta tours
    def unmerge_tours(tour, cities_per_traveller_list):
        # Gera lista vazias com com a cidade posição 0 como inicial
        unmerged = [[tour[0]] for _ in range(len(cities_per_traveller_list))]

        # Essas informações são atualizadas no começo do while
        current_traveller_index = -1 # Caixeiro atual
        current_traveller_amount = 0 # Quantidade de cidades que vão para este caixeiro

        # Indice da cidade atual
        i = 1
        while i < len(tour) - 1:
            # Quando a quantidade de cidades restante chegar a 0 ir para o proximo caixeiro (indice)
            if current_traveller_amount <= 0:
                # Adiciona cidade final para este caixeiro
                if current_traveller_index >= 0:
                    unmerged[current_traveller_index].append(unmerged[current_traveller_index][0])

                current_traveller_index += 1
                current_traveller_amount = cities_per_traveller_list[current_traveller_index]

            unmerged[current_traveller_index].append(tour[i])
            
            current_traveller_amount -= 1
            i += 1

        # Adiciona a ultima cidade para o ultimo tour (ja que o while loop para antes disso acontecer)
        unmerged[-1].append(tour[-1])

        return unmerged

    # Rota compactada
    merged_tours = merge_tours(tours)

    # Melhor rota encontrada (Compactada)
    best_tour = merged_tours.copy()

    # Rota atual (compactada)
    current_tour = merged_tours.copy() # Por enquanto só

    # Quantidade de melhorias
    times_improved = 0
    distance = total_distance

    # Divide as iterações pra cada tour
    # iterations = int(iterations/len(tours))
    
    for count in range(iterations):
        # Se a distância estiver muito ruim (X% pior, então volta pra melhor distância que ja foi encontrada)
        result = 1 - (total_distance / distance)
        if result >= bad_threshold:
            current_tour = best_tour.copy()

        # Diminui a temperatura
        temperature = lerp(initial_temperature, final_temperature, (count/iterations))

        for i in range(1, len(current_tour) -1):
            # temperature = max(temperature - temperature_decay, final_temperature)

            # Pega a cidade com qual essa vai criar uma nova rota (Não incluindo cidade inicial e final)
            # Também devemos impedir de que o valor a ser trocado seja o mesmo que a cidade que estamos modificando agora
            sort = i
            while sort == i:
                sort = random.randint(1, len(current_tour) - 2) 

            # Faz a troca de rotas
            current_tour[i], current_tour[sort] = current_tour[sort], current_tour[i]

            # Toda vez que pegamos a distância da rota, descompactamos ela, para dar o valor real da distancia
            distance = get_total_distance(unmerge_tours(current_tour, cities_per_traveller_list))
            
            if distance < total_distance:
                times_improved += 1
                # Atualiza a melhor distância
                total_distance = distance
                best_tour = current_tour.copy()
            else:
                # Caso a distância tenha piorado, sorteia outro numero para trocar
                sort2 = i
                while sort2 == i or sort2 == sort:
                    sort2 = random.randint(1, len(current_tour) - 2)

                # Faz a troca de rotas com o novo valor sorteado
                current_tour[sort], current_tour[sort2] = current_tour[sort2], current_tour[sort]
                distance = get_total_distance(unmerge_tours(current_tour, cities_per_traveller_list))

                if distance < total_distance:
                    times_improved += 1
                    
                    # Atualiza a melhor distância
                    total_distance = distance
                    best_tour = current_tour.copy()
                else:
                    # Aleatoriamente aceita soluções piores
                    if (random.random() < temperature):
                        continue

                    # Caso a distância tenha piorado, desfaz as trocas
                    current_tour[sort2], current_tour[sort] = current_tour[sort], current_tour[sort2]
                    current_tour[i], current_tour[sort] = current_tour[sort], current_tour[i]

        #print(f"{count}/{iterations}")
        count += 1

    extra_info["times_improved"] = times_improved
    if debug_print:
        print(f"Melhorou {times_improved} vezes!")

    # Caso tenha sido varios tours, descompacta a lista
    if is_multiple_tours:
        best_tour = unmerge_tours(best_tour, cities_per_traveller_list)

    # Descompacta tour e retorna
    return total_distance, best_tour, extra_info

def get_cities_per_traveller(n_cities, n_traveller):
    # Quantidade de cidade que cada caixeiro vai visitar (Tirando a 0)
    cities_per_traveller = (n_cities - 1)/n_traveller
    cities_per_traveller_list = []

    # Caso seja um numero quebrado entra nesse if
    if (not cities_per_traveller.is_integer()):
        # Pega apenas o numero decimal
        decimal_number = Decimal(f'{cities_per_traveller}') % 1

        # Caso o numero decimal seja menor que X.5, todos caixeiros viajarão X ciades e o ultimo X + 1
        if decimal_number < 0.5:
            for i in range(n_traveller):
                if i == n_traveller - 1:
                    n_cities_to_go = math.ceil(cities_per_traveller)
                else:
                    n_cities_to_go = int(cities_per_traveller)

                cities_per_traveller_list.append(n_cities_to_go)
        elif decimal_number > 0.5:
            for i in range(n_traveller):
                if i == n_traveller - 1:
                    n_cities_to_go = int(cities_per_traveller)
                else:
                    n_cities_to_go = math.ceil(cities_per_traveller)

                cities_per_traveller_list.append(n_cities_to_go)
        else: # Exatamente 0.5
            mid_point = int(n_traveller/2)
            for i in range(n_traveller):
                if i < mid_point:
                    n_cities_to_go = int(cities_per_traveller)
                else:
                    n_cities_to_go = math.ceil(cities_per_traveller)

                cities_per_traveller_list.append(n_cities_to_go)
    else:
        cities_per_traveller_list = [int(cities_per_traveller) for _ in range(n_traveller)]

    # Certifica-se de que o total de cidades está correto
    total = 0
    for qty in cities_per_traveller_list:
        total += qty

    assert(total == n_cities - 1)

    return cities_per_traveller_list

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

    cities_per_traveller_list = get_cities_per_traveller(n_cities, n_traveller)

    # Passa por cada caixeiro
    for tour_index in range(len(tours)):
        # Quantas cidades esse caixeiro irá viajar
        amount_to_travel = cities_per_traveller_list[tour_index]

        # Passa por cada cidade
        for city_index in range(amount_to_travel, 0, -1):
            # Caso por algum motivo não tenha mais cidades restantes saia desse loop
            if (len(unvisited)) == 0:
                break

            next = heuristic(tours, unvisited, tour_index, amount_to_travel)

            #print(f"next: {next}")
            #if city_index == amount_to_travel:
            #    print(tours)
            #    print(unvisited)
            #    print(f"last: {last}")

            if (type(next) is list):
                for x in next:
                    tours[tour_index].append(x)
                    unvisited.remove(x)
            else:
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

# Se não for o arquivo principal que esta sendo executado sai dele
if __name__ == "__main__":
    print("[ATENÇÃO] Existe uma chance pequena chance desse código dar erro na linha 55, caso der este erro tente rodar denovo até funcionar, estamos investigando. ")
    print("[ATENÇÃO] Existe uma chance pequena chance desse código dar erro na linha 55, caso der este erro tente rodar denovo até funcionar, estamos investigando. ")

    # ESCOLHA A HEURISTICA AQUI:             V  AQUI  V
    tours = solution_multiple_travellers(two_close_cities)

    # TUDO SOBRE A PRIMEIRA ROTA SEM OTIMIZAÇÃO:
    distancia_total = get_total_distance(tours)

    print(f"Distancia total inicial: {distancia_total}m")
    print(f"TOURS: {tours}")
    #plot_path(distances, tours)


    # Quantidade de iterações que vamos usar para melhorar as rotas
    iterations = 50000

    # TUDO SOBRE A SEGUNDA ROTA COM OTIMIZAÇÃO:
    # Primeiramente fazemos uma tentativa de otimização geral (Tentatos trocar rotas entre diferentes tours de diferentes caixeiros)
    print("Iniciando processo de melhora de rotas...")

    print(f"Melhorando rota usando three_opt: 0/{len(tours)} (O primeiro processo é mais intenso)", end="")
    _, best_tour, extra_info = three_opt(tours, iterations=iterations) 
    print(f" | Quantidade de melhorias: {extra_info["times_improved"]}")

    # Agora otimizamos individualmente o tour de cada caixeiro
    for i, tour in enumerate(tours):
        print(f"Melhorando rota usando three_opt: {i+1}/{len(tours)}", end="")
        _, best_tour[i], extra_info = three_opt(best_tour[i], iterations=int(iterations/len(tours)))
        print(f" | Quantidade de melhorias: {extra_info["times_improved"]}")

    # Por fim tentamos por uma ultima vez melhorar as rotas como um todo
    #print(f"Melhorando rota usando three_opt: {len(tours)+1}/{len(tours)+1} (O ultimo processo também é intenso)", end="")
    #_, best_tour, extra_info = three_opt(best_tour, iterations=iterations) 
    #print(f" | Quantidade de melhorias: {extra_info["times_improved"]}")

    # Agora sim pegamos a total distance do tour atualizado
    total_distance = get_total_distance(best_tour)
    print(f"{best_tour}: {total_distance}m")
    print(f"Distancia total optimizada: {total_distance}m")
    print(f"Numero de cidades: {n_cities}")
    print(f"Número de caixeiros viajantes: {n_traveller}")
    plot_path(distances, best_tour)
