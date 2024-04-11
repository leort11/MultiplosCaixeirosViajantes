import pygame
import numpy as np
from sklearn import manifold
from generate_distances import generate_distances
from main import get_total_distance
from main import two_close_cities
from main import three_opt
from main import get_cities_per_traveller
pygame.init()

WIDTH, HEIGHT = 750, 750
screen = pygame.display.set_mode([WIDTH, HEIGHT])

# É O MESMO CODIGO DA MAIN.PY SÓ QUE UM POUCO MODIFICADO
# ESTE ARQUIVO FOI FEITO APENAS COMO UM EXTRA

# SÒ FUNCIONA NA PASTA MAIN E COM 1 CAIXEIRO
# E NÃO TEM O ALGORITIMO DE OPT THREE SWAP
# SERVE APENAS PARA DEMONSTRAR O TWO_CLOSE_CITIES

class TSMSolution:

    def __init__(self, distances, n_traveller, heuristic) -> None:
        self.distances = distances
        self.n_traveller = n_traveller
        self.heuristic = heuristic
        self.n_cities = len(distances)

        # Verifica se tem mais caixeiros do que cidades
        self.n_traveller_remaining = 0 # Numero de caixeiros viajantes que não farão nada
        if (n_traveller > self.n_cities - 1):
            self.n_traveller_remaining = n_traveller - (self.n_cities - 1)
            n_traveller = self.n_cities - 1 # Limita o numero de caixeiros para o numero de cidade
        
        # Cria um tour para cada caixeiro
        # Cada caixeiro vai começar com a cidade 0 já visitada
        self.tours = [[0] for _ in range(n_traveller)]

        # São as cidades que os caixeiros vão ter que visitar
        self.unvisited = list(range(1, self.n_cities))

        # Verifica se tem mais caixeiros do que cidades
        self.n_traveller_remaining = 0 # Numero de caixeiros viajantes que não farão nada
        if (n_traveller > self.n_cities - 1):
            self.n_traveller_remaining = n_traveller - (self.n_cities - 1)
            self.n_traveller = self.n_cities - 1 # Limita o numero de caixeiros para o numero de cidade

        self.cities_per_traveller_list = get_cities_per_traveller(self.n_cities, self.n_traveller)

        # Indices
        self.tour_index = -1

        # Quantas cidades esse caixeiro irá viajar
        self.amount_to_travel = -1

        # Cidade atual
        self.city_index = -1
        self.last = -1

        self.next_tour()

    def next_tour(self):
        if self.tour_index != -1:
            # Adiciona a cidade 0 já que tem que voltar pra ela
            self.tours[self.tour_index].append(0)

        self.tour_index += 1

        # Verifica se acabou o tour
        if self.tour_index >= len(self.tours):
            # Adiciona os caixeiros que não vão fazer nada para a lista
            for _ in range(self.n_traveller_remaining):
                self.tours.append([0])

            # Atualiza denovo a variavel que mudou temporariamente para o numero limite.
            self.n_traveller += self.n_traveller_remaining
            
            return False

        self.amount_to_travel = self.cities_per_traveller_list[self.tour_index]
        self.city_index = self.amount_to_travel
        return True

    def next_city(self):
        self.city_index -= 1

        # Caso por algum motivo não tenha mais cidades restantes retorna false
        if (len(self.unvisited)) == 0:
            return False

        return True

    # Da um passo com a heuristica, retorna as mudanças
    def step(self):

        # Verifica se acabou os tour
        if self.tour_index >= len(self.tours):
            return False

        # Vai para o proximo tour
        if self.city_index == -1:
            self.next_tour()
            return True

        # Passa por cada caixeiro
        if not self.next_city():
            self.next_tour()
            return True
        
        next, self.last = self.heuristic(self.tours, self.unvisited, self.tour_index, self.amount_to_travel, self.distances, return_last=True)

        if (type(next) is list):
            for x in next:
                self.tours[self.tour_index].append(x)
                self.unvisited.remove(x)
        else:
            self.tours[self.tour_index].append(next)
            self.unvisited.remove(next)

        return True

# Gera coordenadas a partir de uma matriz de distancias
def get_coords(distances):
    dists = []
    for i, d in enumerate(distances):
        dists.append(list(map(float, d)))

    adist = np.array(dists)
    amax = np.amax(adist)
    adist /= amax

    mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)
    results = mds.fit(adist)

    coords = results.embedding_
    return coords


def main():
    running = True

    # Tempo desde que iniciou o programa
    start_time = pygame.time.get_ticks()
    time_elapsed = pygame.time.get_ticks() - start_time

    # Gera distâncias
    distances, n_travellers = generate_distances("mTSP-n31-m3")
    n_travellers = 1 # Ainda nao funciona com multiplo caixeiros viajante

    # Gera coordenadas de cada cidade
    normalized_coords = get_coords(distances)

    # Normaliza coordenadas para um valor entre 0 e 1
    for coord in normalized_coords:
        coord[0] += 0.5
        coord[1] += 0.5
    
    # Coordenadas na tela
    screen_coords = []

    screen_edge = 300
    for i, coord in enumerate(normalized_coords):
        screen_coords.append(((coord[0] * WIDTH), coord[1] * HEIGHT))

    route = [0, 4, 2, 0]

    # Coordenada de cada rota
    route_coords = []

    def add_route(city1, city2):
        city1_coords = screen_coords[city1]
        city2_coords = screen_coords[city2]
        route_coords.append((city1_coords, city2_coords))

    tsm_solution = TSMSolution(distances, n_travellers, two_close_cities)

    run_step = False
    first_time = True
    while running:
        time_elapsed = pygame.time.get_ticks() - start_time

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass
                    #run_step = True
                
        # run_step
        if ((time_elapsed/1000) >= 0.25):
            start_time = pygame.time.get_ticks()
            time_elapsed = start_time
            run_step = True

        # Limpa a tela
        screen.fill((25, 25, 25))

        # Desenha a rota atual
        line_color = (255, 0, 0)
        for coord in route_coords:
            pygame.draw.line(screen, line_color, coord[0], coord[1], 4)

        # Desenha as cidades
        for coord in screen_coords:
            city_color = (200, 200, 200)
            pygame.draw.circle(screen, city_color, coord, 8)

        # Da um passo com a heuristica
        if run_step:
            if tsm_solution.step():
                add_route(tsm_solution.tours[0][-2], tsm_solution.tours[0][-1])

                if first_time:
                    add_route(tsm_solution.last, tsm_solution.tours[tsm_solution.tour_index][0])
                    first_time = False

        # Atualiza a tela
        pygame.display.flip()

        run_step = False

    pygame.quit()

if __name__ == "__main__":
    main()