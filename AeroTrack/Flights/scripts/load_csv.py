import csv
from Flights.models import AirportRoute
from ast import literal_eval

def load_csv_to_db(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source_coords = literal_eval(row['source coords'])
            destination_coords = literal_eval(row['destination coords'])

            AirportRoute.objects.create(
                airline=row['airline'],
                airline_id=row['airline ID'],
                source_airport=row['source airport'],
                source_airport_id=row['source airport id'],
                destination_airport=row['destination airport'],
                destination_airport_id=row['destination airport id'],
                codeshare=row['codeshare'] or None,
                stops=int(row['stops']),
                equipment=row['equipment'],
                source_coords=source_coords,
                destination_coords=destination_coords
            )
