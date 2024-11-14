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
    source_airports = upload_source_airports()
    destination_airports = upload_destination_airports()

    saltos_min = None
    ruta_minima = None
    distancia_kilometros = None
    
    if origen and target:
        saltos_min, ruta_minima, distancia_kilometros = generate_graph(origen, target)
        
        if 'historial_busquedas' not in request.session:
            request.session['historial_busquedas'] = []
        # Agregar nueva búsqueda al historial
        nueva_busqueda = {
            'origen': origen,
            'target': target,
            'saltos_min': saltos_min,
            'ruta_minima': ruta_minima,
            'distancia_kilometros': distancia_kilometros
        }
        # Evitar duplicados
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
        "saltos_min": saltos_min,
        "ruta_minima": ruta_minima,
        "distancia_kilometros": distancia_kilometros,
        "historial_busquedas": historial_invertido,
    }
    return render(request, "flights.html", context)
