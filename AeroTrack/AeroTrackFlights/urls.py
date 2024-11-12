from django.contrib import admin
from django.urls import path
from Flights.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView)
]
