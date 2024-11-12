from django.contrib import admin
from django.urls import path
from Flights.views import IndexView
from Flights.views import AboutView
from Flights.views import FlightsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView),
    path('about/', AboutView),
    path('flights/', FlightsView),
]
