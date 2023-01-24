import os
import click
import re
from csv import writer
from app.geometry import Coordinate, calculate_cumulative_distances


def register(app):
    @app.cli.group()
    def gpx():
        """Commands for processing GPX files."""
        pass

    @gpx.command()
    @click.argument('trailname')
    def process(trailname):
        """Process a GPX file into the format used by GR-tracker"""
        filename_in = f"app/data/{trailname.lower()}.gpx"
        with open(filename_in) as file:
            filestream = file.read()
            pattern = re.compile(r'<trkpt lat="(?P<lat>\d+.\d+)" lon="(?P<lon>\d+.\d+)">\n\s+<ele>(?P<ele>(?:-?\d+)?)</ele>')
            matches = pattern.findall(filestream)

        coordinates = []
        for match in matches:
            coordinate = Coordinate(
                latitude_deg=float(match[0]),
                longitude_deg=float(match[1]),
                elevation_meter=float(match[2]),
            )
            coordinates.append(coordinate)
        cumulative_distances = calculate_cumulative_distances(coordinates)

        filename_out = f"app/data/{trailname.lower()}.csv"
        with open(filename_out, "w") as file:
            csv_writer = writer(file)
            csv_writer.writerow(['latitude[deg]','longitude[deg]','elevation[m]','cumulativedistance[km]'])
            for i, coordinate in enumerate(coordinates):
                newrow = [
                    coordinate.latitude_deg,
                    coordinate.longitude_deg,
                    coordinate.elevation_meter,
                    cumulative_distances[i]
                ]
                csv_writer.writerow(newrow)

        print(f"Trail {trailname} has been processed.")