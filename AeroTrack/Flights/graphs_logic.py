import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import geodesic
from Flights.models import AirportRoute
from django.conf import settings
import os


def generate_graph(origen, target):
    # Crear el grafo
    G = nx.DiGraph()

    # Consultar todas las rutas de la base de datos
    routes = AirportRoute.objects.all()

    def heuristic(a, b):
        coords_1 = G.nodes[a]['coordinates']
        coords_2 = G.nodes[b]['coordinates']
        return geodesic(coords_1, coords_2).kilometers

    # Construir el grafo desde la base de datos
    for route in routes:
        source = route.source_airport
        destination = route.destination_airport
        source_coords = eval(route.source_coords)  # Convertir de string a tuple
        destination_coords = eval(route.destination_coords)

        if G.has_edge(source, destination):
            G[source][destination]['weight'] += 1
            continue

        if not G.has_node(source):
            G.add_node(source, coordinates=source_coords)
        if not G.has_node(destination):
            G.add_node(destination, coordinates=destination_coords)

        distance = geodesic(source_coords, destination_coords).kilometers
        G.add_edge(source, destination, weight=distance.__round__(2))

    # Algoritmo de A* para encontrar la ruta más corta
    def RutaAstar(grafo, nodo_inicio, nodo_final):
        rutas_validas = nx.astar_path(
            grafo, source=nodo_inicio, target=nodo_final, heuristic=heuristic, weight='weight'
        )
        distancia = nx.astar_path_length(
            grafo, source=nodo_inicio, target=nodo_final, heuristic=heuristic, weight='weight'
        )
        print(f"EL mínimo de saltos es {len(rutas_validas)}. Ruta corta: {rutas_validas}, distancia: {distancia} km")
        return rutas_validas, distancia

    if origen not in G or target not in G:
        raise ValueError(f"No hay rutas disponibles entre {origen} y {target}")

    ruta_mas_corta, distancia_total = RutaAstar(G, origen, target)

    saltos_min = len(ruta_mas_corta)
    ruta_minima = ruta_mas_corta
    distancia_kilometros = round(distancia_total, 2)

    # Crear un nuevo grafo para la ruta mínima
    GNEW = nx.DiGraph()
    for nodes in ruta_mas_corta:
        GNEW.add_node(nodes)
        if nodes == target:
            break
        GNEW.add_edge(
            nodes,
            ruta_mas_corta[ruta_mas_corta.index(nodes) + 1],
            weight=G.get_edge_data(nodes, ruta_mas_corta[ruta_mas_corta.index(nodes) + 1])['weight'],
        )

    # Dibujar el grafo de la ruta mínima
    pos = nx.kamada_kawai_layout(GNEW)
    plt.figure(figsize=(14, 14))
    nx.draw_networkx(
        GNEW,
        pos=pos,
        with_labels=True,
        node_size=7000,
        node_color="green",
        font_size=30,
        font_color="white",
        font_weight="bold",
        edge_color="gray",
        width=2.5 
    )

    labels = nx.get_edge_attributes(GNEW, 'weight')
    nx.draw_networkx_edge_labels(
        GNEW,
        pos,
        edge_labels=labels,
        font_size=15,  
        font_color="blue" 
    )
    
    static_dir = os.path.join(settings.BASE_DIR, 'Flights', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    image_path = os.path.join(static_dir, 'graphs', 'graph.png')
    plt.savefig(image_path)
    plt.close()

    return saltos_min, ruta_minima, distancia_kilometros


def upload_source_airports():
    return AirportRoute.objects.values_list('source_airport', flat=True).distinct()


def upload_destination_airports():
    return AirportRoute.objects.values_list('destination_airport', flat=True).distinct()
