from django.shortcuts import render

import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math
from django.conf import settings

def generate_graph():
    file_path = os.path.join(settings.BASE_DIR, 'Flights', 'routes.csv')
    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()
    df = df.rename(columns={"destination apirport": "destination airport"})
    df = df.sort_values(by=['source airport', 'destination airport'])

    G = nx.DiGraph()

    def heuristic(a, b):
        x1, y1 = G.nodes[a]['coordinates']
        x2, y2 = G.nodes[b]['coordinates']
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    for _, row in df.iterrows():
        source = row['source airport']
        destination = row['destination airport']
        source_coords = int(row['source airport'], base=36), int(row['source airport'], base=36) / 2
        destination_coords = int(row['destination airport'], base=36), int(row['destination airport'], base=36) / 2

        if G.has_edge(source, destination):
            G[source][destination]['weight'] += 1
            continue

        if not G.has_node(source):
            G.add_node(source, coordinates=source_coords)
        if not G.has_node(destination):
            G.add_node(destination, coordinates=destination_coords)
        G.add_edge(source, destination, weight=1)

    def RutaAstar(grafo, nodo_inicio, nodo_final):
        return nx.astar_path(grafo, source=nodo_inicio, target=nodo_final, heuristic=heuristic, weight='weight')

    origen = 'AER'
    target = 'POS'
    ruta_mas_corta = RutaAstar(G, origen, target)

    GNEW = nx.DiGraph()
    for nodes in ruta_mas_corta:
        GNEW.add_node(nodes)
        if nodes == target:
            break
        GNEW.add_edge(nodes, ruta_mas_corta[ruta_mas_corta.index(nodes) + 1], weight=G.get_edge_data(nodes, ruta_mas_corta[ruta_mas_corta.index(nodes) + 1])['weight'])

    #pos = nx.kamada_kawai_layout(GNEW)
    #plt.figure(figsize=(12, 12))
    #nx.draw_networkx(GNEW, with_labels=True, node_size=100, node_color="skyblue", font_size=5, font_color="black", font_weight="normal", edge_color="gray", pos=pos)
    #labels = nx.get_edge_attributes(GNEW, 'weight')
    #nx.draw_networkx_edge_labels(GNEW, pos, edge_labels=labels)
    
    pos = nx.kamada_kawai_layout(GNEW)
    plt.figure(figsize=(14, 14))  # Tamaño del gráfico más grande
    nx.draw_networkx(
        GNEW,
        pos=pos,
        with_labels=True,
        node_size=500,  # Tamaño de los nodos incrementado
        node_color="green",  # Color de los nodos en verde
        font_size=10,  # Tamaño de la fuente mayor para mejor visibilidad
        font_color="white",  # Color de las letras en blanco
        font_weight="bold",  # Letras en negrita para mayor visibilidad
        edge_color="gray"  # Color de las aristas en gris
    )

    # Agregar etiquetas de peso a las aristas
    labels = nx.get_edge_attributes(GNEW, 'weight')
    nx.draw_networkx_edge_labels(GNEW, pos, edge_labels=labels, font_size=8, font_color="black")  # Tamaño de fuente para etiquetas de aristas


    # Guardar la imagen en el directorio 'graphs'
    static_dir = os.path.join(settings.BASE_DIR, 'Flights', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Guardar la imagen en la carpeta de medios
    image_path = os.path.join(static_dir, 'graphs' ,'graph.png')
    plt.savefig(image_path)
    plt.close()

# Create your views here.
def IndexView(request):
    return render(request, "index.html")

def AboutView(request):
    return render(request, "about.html")

def FlightsView(request):
    generate_graph()
    return render(request, "flights.html")