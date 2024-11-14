import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import ast
from django.conf import settings

def generate_graph(origen, target):
    file_path = os.path.join(settings.BASE_DIR, 'Flights', 'airport_routes.csv')
    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()
    df = df.rename(columns={"destination airport": "destination airport"})
    df = df.sort_values(by=['source airport', 'destination airport'])

    df['source_coords'] = df['source coords'].apply(ast.literal_eval)
    df['destination_coords'] = df['destination coords'].apply(ast.literal_eval)

    G = nx.DiGraph()

    def heuristic(a, b):
        coords_1 = G.nodes[a]['coordinates']
        coords_2 = G.nodes[b]['coordinates']
        return geodesic(coords_1, coords_2).kilometers

    for _, row in df.iterrows():
        source = row['source airport']
        destination = row['destination airport']
        source_coords = row['source_coords']
        destination_coords = row['destination_coords']

        if G.has_edge(source, destination):
            G[source][destination]['weight'] += 1
            continue

        if not G.has_node(source):
            G.add_node(source, coordinates=source_coords)
        if not G.has_node(destination):
            G.add_node(destination, coordinates=destination_coords)
        distance = heuristic(source, destination)
        G.add_edge(source, destination, weight=distance.__round__(2))

    def RutaAstar(grafo, nodo_inicio, nodo_final):
        rutas_validas = nx.astar_path(
            grafo, source=nodo_inicio, target=nodo_final, heuristic=heuristic, weight='weight'
        )
        distancia = nx.astar_path_length(
            grafo, source=nodo_inicio, target=nodo_final, heuristic=heuristic, weight='weight'
        )
        print(f"EL minimo de saltos es {len(rutas_validas)}. Ruta corta: {rutas_validas}, distancia: {distancia} km")
        return rutas_validas, distancia

    ruta_mas_corta, distancia_total = RutaAstar(G, origen, target)

    saltos_min = len(ruta_mas_corta)
    ruta_minima = ruta_mas_corta
    distancia_kilometros = round(distancia_total, 2)

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

    pos = nx.kamada_kawai_layout(GNEW)
    plt.figure(figsize=(14, 14))
    nx.draw_networkx(
        GNEW,
        pos=pos,
        with_labels=True,
        node_size=500,
        node_color="green",
        font_size=10,
        font_color="white",
        font_weight="bold",
        edge_color="gray",
    )

    labels = nx.get_edge_attributes(GNEW, 'weight')
    nx.draw_networkx_edge_labels(GNEW, pos, edge_labels=labels, font_size=8, font_color="black")
    plt.title(f"Grafo de {origen} a {target}")

    static_dir = os.path.join(settings.BASE_DIR, 'Flights', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    image_path = os.path.join(static_dir, 'graphs', 'graph.png')
    plt.savefig(image_path)
    plt.close()

    return saltos_min, ruta_minima, distancia_kilometros



    
def upload_source_airports():
    file_path = os.path.join(settings.BASE_DIR, 'Flights', 'airport_routes.csv')
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    if 'source airport' not in df.columns:
        raise ValueError("La columna 'source airport' no se encuentra en el archivo CSV. Nombres encontrados: {}".format(df.columns))
    return df['source airport'].drop_duplicates().sort_values().tolist()


def upload_destination_airports():
    file_path = os.path.join(settings.BASE_DIR, 'Flights', 'airport_routes.csv')
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    if 'destination airport' not in df.columns:
        raise ValueError("La columna 'destination airport' no se encuentra en el archivo CSV. Nombres encontrados: {}".format(df.columns))
    return df['destination airport'].drop_duplicates().sort_values().tolist()