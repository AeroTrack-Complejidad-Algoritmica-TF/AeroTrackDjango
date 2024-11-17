import networkx as nx
from geopy.distance import geodesic
from Flights.models import AirportRoute
from django.conf import settings
import os
import folium


def generate_graph(origen, target):
    G = nx.DiGraph()

    routes = AirportRoute.objects.all()

    def heuristic(a, b):
        coords_1 = G.nodes[a]['coordinates']
        coords_2 = G.nodes[b]['coordinates']
        return geodesic(coords_1, coords_2).kilometers

    CAPACIDAD_MAXIMA = 10

    for route in routes:
        source = route.source_airport
        destination = route.destination_airport
        source_coords = eval(route.source_coords)
        destination_coords = eval(route.destination_coords)

        if G.has_edge(source, destination):
            G[source][destination]['weight'] += 1
            G[source][destination]['capacity'] += 1
            continue

        if not G.has_node(source):
            G.add_node(source, coordinates=source_coords)
        if not G.has_node(destination):
            G.add_node(destination, coordinates=destination_coords)

        distance = geodesic(source_coords, destination_coords).kilometers
        G.add_edge(source, destination, weight=distance, capacity=1)

    if origen not in G or target not in G:
        raise ValueError(f"No hay rutas disponibles entre {origen} y {target}")

    rutas_validas = nx.astar_path(G, source=origen, target=target, heuristic=heuristic, weight="weight")
    distancia = nx.astar_path_length(G, source=origen, target=target, heuristic=heuristic, weight="weight")
    saltos_min = len(rutas_validas) - 1
    print(f"Ruta mínima: {rutas_validas}, Saltos mínimos: {saltos_min}, Distancia: {distancia} km")        
    
    flow_value, flow_dict = nx.maximum_flow(G, origen, target, capacity="capacity")
    for u, v in G.edges():
        if flow_dict[u][v] > 0:
            print(f"Flujo de {u} a {v}: {flow_dict[u][v]} / {G[u][v]['capacity']}")

    print(f"Flujo máximo: {flow_value}, Ruta aproximada: {rutas_validas}, Distancia: {distancia} km")
    
    GNEW = nx.DiGraph()
    for i in range(len(rutas_validas) - 1):
        source = rutas_validas[i]
        destination = rutas_validas[i + 1]
        GNEW.add_node(source, coordinates=G.nodes[source]['coordinates'])
        GNEW.add_node(destination, coordinates=G.nodes[destination]['coordinates'])
        if G.has_edge(source, destination):
            GNEW.add_edge(source, destination, weight=G.get_edge_data(source, destination).get('weight', 1))

    m = folium.Map(location=[20, 0], zoom_start=1)

    icon_url = 'https://i.imgur.com/JrTNVat.png'

    for node in GNEW.nodes(data=True):
        coords = node[1]['coordinates']
        iconCustom = folium.CustomIcon(icon_url, icon_size=(30, 30))

        if node[0] == origen:
            folium.Marker(location=coords, popup=f"{node[0]}: {coords}", icon=folium.Icon(color='green')).add_to(m)
        elif node[0] == target:
            folium.Marker(location=coords, popup=f"{node[0]}: {coords}", icon=folium.Icon(color='red')).add_to(m)
        else:
            folium.Marker(location=coords, popup=f"{node[0]}: {coords}", icon = folium.Icon()).add_to(m)

    for edge in GNEW.edges(data=True):
        coords_1 = GNEW.nodes[edge[0]]['coordinates']
        coords_2 = GNEW.nodes[edge[1]]['coordinates']
        folium.PolyLine(locations=[coords_1, coords_2], color='blue', weight=2.5, opacity=1).add_to(m)
        
    static_dir = os.path.join(settings.BASE_DIR, 'Flights', 'static', 'maps')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        
    map_path1 = os.path.join(static_dir, "ruta_minima.html")
    m.save(map_path1)
        
        
    GNEW_FLOW = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        if flow_dict[u][v] > 0:
            if not GNEW_FLOW.has_node(u):
                GNEW_FLOW.add_node(u, coordinates=G.nodes[u]['coordinates'])
            if not GNEW_FLOW.has_node(v):
                GNEW_FLOW.add_node(v, coordinates=G.nodes[v]['coordinates'])
            GNEW_FLOW.add_edge(u, v, weight=data['weight'], flow=flow_dict[u][v])
            
    m_flow = folium.Map(location=[20, 0], zoom_start=1)
    
    for node in GNEW_FLOW.nodes(data=True):
        coords = GNEW_FLOW.nodes[node[0]]['coordinates']
        if node[0] == origen:
            capacity_info = f"{sum(G[u][v]['capacity'] for u, v in G.edges(node[0]) if flow_dict[u][v] > 0)}"  # Suma de las capacidades de las aristas salientes del nodo origen
            folium.Marker(location=coords, popup=f"{node[0]}: {coords}<br>{flow_value}/{capacity_info}", icon=folium.Icon(color='green')).add_to(m_flow)
        elif node[0] == target:
            flow_info = f"Flujo: {sum(flow_dict[u][node[0]] for u in G.predecessors(node[0]) if flow_dict[u][node[0]] > 0)}"  # Suma de los flujos entrantes del nodo destino
            capacity_info = f"{sum(G[u][v]['capacity'] for u, v in G.in_edges(node[0]) if flow_dict[u][v] > 0)}"  # Suma de las capacidades de las aristas entrantes del nodo destino
            folium.Marker(location=coords, popup=f"{node[0]}: {coords}<br>{flow_info}/{capacity_info}", icon=folium.Icon(color='red')).add_to(m_flow)
        else:
            flow_info = f"Flujo: {sum(flow for flow in flow_dict[node[0]].values() if flow > 0)}"  # Suma de los flujos salientes del nodo intermedio
            capacity_info = f"{sum(G[u][v]['capacity'] for u, v in G.edges(node[0]) if flow_dict[u][v] > 0)}"  # Suma de las capacidades de las aristas salientes del nodo intermedio
            folium.Marker(location=coords, popup=f"{node[0]}: {coords}<br>{flow_info}/{capacity_info}", icon=folium.Icon()).add_to(m_flow)
        
    for u, v, data in GNEW_FLOW.edges(data=True):
        coords_1 = GNEW_FLOW.nodes[u]['coordinates']
        coords_2 = GNEW_FLOW.nodes[v]['coordinates']
        color = 'red' if data['flow'] >= G[u][v]['capacity'] else 'blue'
        folium.PolyLine(locations=[coords_1, coords_2], color=color, weight=2.5, opacity=1).add_to(m_flow)


    """Guardar el mapa"""
    map_path2 = os.path.join(static_dir, "flujo_maximo.html")
    m_flow.save(map_path2)

    return saltos_min, rutas_validas, round(distancia, 2), flow_value, "maps/ruta_minima.html", "maps/flujo_maximo.html"


def upload_source_airports():
    return AirportRoute.objects.values_list('source_airport', flat=True).distinct()


def upload_destination_airports():
    return AirportRoute.objects.values_list('destination_airport', flat=True).distinct()
