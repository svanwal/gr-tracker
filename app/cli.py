import os
import click
import re
from csv import writer
from app.geometry import Coordinate, calculate_cumulative_distances
from app.models import User, Trail
from app import db
from config import Config
from pathlib import Path


def register(app):

    ## GPX File processing
    @app.cli.group()
    def gpx():
        """Commands for processing GPX files."""
        pass

    @gpx.command()
    @click.argument('trailname')
    def process(trailname):
        """Process a GPX file into the format used by GR-tracker."""
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

    ## User management
    @app.cli.group()
    def users():
        """Commands for controlling user rights."""
        pass

    @users.command()
    @click.argument('username')
    def make_admin(username):
        user = User.query.where(User.username==username).one_or_none()
        if user:
            user.is_admin = True
            db.session.commit()

    @users.command()
    @click.argument('username')
    def unmake_admin(username):
        user = User.query.where(User.username==username).one_or_none()
        if user:
            user.is_admin = False
            db.session.commit()

    ## Trail management
    @app.cli.group()
    def trails():
        """Commands for trail management."""
        pass

    @trails.command()
    def init():
        config = Config()
        for input_trail in config.DEFAULT_TRAILS:
            name = input_trail[0]
            trail = Trail.query.where(Trail.name==name).one_or_none()
            if not trail:
                path = Path(f"app/data/{name}.csv")
                if path.is_file():
                    new_trail = Trail(
                        name=input_trail[0],
                        dispname=input_trail[1],
                        fullname=input_trail[2],
                    )
                    db.session.add(new_trail)
                    print(f"Initialized trail {name}.")
                else:
                    print(f"Attempted to initialize trail {name}, but the GPX file {path} was not found.")
            else:
                print(f"Trail {name} already exists.")
        db.session.commit()