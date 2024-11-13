from django.contrib import admin
from django.urls import path
from Flights.views import IndexView
from Flights.views import AboutView
from Flights.views import FlightsView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView),
    path('about/', AboutView),
    path('flights/', FlightsView),
    path('flights/<str:origen>/<str:target>/', FlightsView),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
