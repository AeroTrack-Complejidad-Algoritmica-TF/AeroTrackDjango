from django.db import models

from django.db import models

class AirportRoute(models.Model):
    airline = models.CharField(max_length=100)
    airline_id = models.CharField(max_length=50)
    source_airport = models.CharField(max_length=100)
    source_airport_id = models.CharField(max_length=50)
    destination_airport = models.CharField(max_length=100)
    destination_airport_id = models.CharField(max_length=50)
    codeshare = models.CharField(max_length=10, null=True, blank=True)
    stops = models.IntegerField()
    equipment = models.CharField(max_length=100, null=True, blank=True)
    source_coords = models.CharField(max_length=100)
    destination_coords = models.CharField(max_length=100)

