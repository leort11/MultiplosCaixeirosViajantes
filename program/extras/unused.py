
# Coisas que descartamos, algumas funcionam ainda parcialmente
# Em geral two_opt da resultados piores que o three_opt
# O lado bom do two_opt é que é um algoritimo muito mais rapido
# Esse arquivo só funciona no arquivo main.py
# E não funciona com multiplos caixeiros viajantes porque nunca terminamos o two_opt
def two_opt(tours, iterations):
    print(f"Quantidade de swaps: {iterations * sum(len(tour) - 1 for tour in tours)}")

    def lerp(A, B, t):
        return A * (1 - t) + B * t

    # Configuração
    initial_temperature = 0.5 #0.75 # 1 = Apenas decisões ruim, # 0.5 Meio termo, # 0 Nunca aceita decições ruim
    #temperature_decay = 0.005
    bad_threshold = 0.5 # Se for X porcento pior que a melhor distancia, entao volta pra melhor distancia 0.01 = 1%

    # Configuração (EXTRA)
    final_temperature = 0.00001

    # Codigo
    temperature = initial_temperature

    # Distancia total da melhor rota encontrada (começa valendo a distancia da rota inicial)
    total_distance = 0

    # Pega a distância do tour (incluindo multiplos caixeiros) e adiciona a variavel
    for tour in tours:
        distance = get_total_distance(tour)
        total_distance += distance

    print(f"Distancia total inicial: {total_distance}m")
    
    # Melhor rota encontrada
    best_tour = tours[0].copy()

    # Rota atual
    current_tour = tours[0].copy() # Por enquanto só

    # Quantidade de melhorias
    times_improved = 0
    distance = total_distance

    for count in range(iterations):
        # Se a distância estiver muito ruim (X% pior, então volta pra melhor distância que ja foi encontrada)
        result = 1 - (total_distance / distance)
        if result >= bad_threshold:
            current_tour = best_tour.copy()

        # Diminui a temperatura
        temperature = lerp(initial_temperature, final_temperature, (count/iterations))

        for i in range(1, len(tour) -1):
            # Diminui a temperatura
            # temperature = max(temperature - temperature_decay, final_temperature)

            # Pega a cidade com qual essa vai criar uma nova rota (Não incluindo cidade inicial e final)
            # Também devemos impedir de que o valor a ser trocado seja o mesmo que a cidade que estamos modificando agora
            sort = i
            while sort == i:
                sort = random.randint(1, len(tour) - 2)

            # Faz a troca de rotas
            current_tour[i], current_tour[sort] = current_tour[sort], current_tour[i]

            distance = get_total_distance(current_tour)
            
            if distance < total_distance:
                times_improved += 1

                # Atualiza a melhor distância
                total_distance = distance
                best_tour = current_tour.copy()
            else:
                # Aleatoriamente aceita soluções piores
                if (random.random() < temperature):
                    continue

                # Caso a distância tenha piorado, destroca
                current_tour[i], current_tour[sort] = current_tour[sort], current_tour[i]
    
    print(f"Melhorado {times_improved} vezes!")

    return total_distance, [best_tour]

