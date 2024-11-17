from django.shortcuts import render

import matplotlib
matplotlib.use('Agg')

from django.conf import settings
from .graphs_logic import *

def IndexView(request):
    return render(request, "index.html")

def AboutView(request):
    return render(request, "about.html")

def FlightsView(request, origen=None, target=None):
    
    rutas_validas = None
    distancia_kilometros = None
    map_path1 = None
    map_path2 = None
    flow_value = None
    
    source_airports = upload_source_airports()
    destination_airports = upload_destination_airports()

    saltos_min, ruta_mas_corta = 0, []

    try:
        if origen and target:
            saltos_min, rutas_validas, distancia_kilometros, flow_value , map_path1, map_path2 = generate_graph(origen, target)
    except ValueError as e:
        error_message = str(e)
    else:
        error_message = None
    
    
    if origen and target:
        
        # Historial de búsquedas
        if 'historial_busquedas' not in request.session:
            request.session['historial_busquedas'] = []
        nueva_busqueda = {
            'origen': origen,
            'target': target,
            'saltos_min': saltos_min,
            'ruta_minima': ruta_mas_corta,
            'distancia_kilometros': distancia_kilometros
        }
        if nueva_busqueda not in request.session['historial_busquedas']:
            request.session['historial_busquedas'].append(nueva_busqueda)
            request.session['historial_busquedas'] = request.session['historial_busquedas'][-5:]
            request.session.modified = True
            
    historial_invertido = request.session.get('historial_busquedas', [])[::-1]


    context = {
        "source_airports": source_airports,
        "destination_airports": destination_airports,
        "origen": origen,
        "target": target,
        "map_path1": map_path1,
        "map_path2": map_path2,
        "saltos_min": saltos_min,
        "ruta_minima": ruta_mas_corta,
        "rutas_validas": rutas_validas,
        "distancia_kilometros": distancia_kilometros,
        "flow_value": flow_value,
        "error_message": error_message,
        "historial_busquedas": historial_invertido,
    }
    return render(request, "flights.html", context)
