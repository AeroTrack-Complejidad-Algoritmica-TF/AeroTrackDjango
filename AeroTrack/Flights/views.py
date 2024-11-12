from django.shortcuts import render

# Create your views here.
def IndexView(request):
    return render(request, "index.html")

def AboutView(request):
    return render(request, "about.html")

def FlightsView(request):
    return render(request, "flights.html")