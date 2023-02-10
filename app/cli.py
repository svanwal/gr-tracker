import os
import click
import re
from csv import writer
from app.geometry import Coordinate, calculate_cumulative_distances
from app.models import User, Trail
from app import db
from config import Config
from pathlib import Path
from app.trails.manager import TrailManager
from app.auth.manager import UserManager
from app.hikes.manager import HikeManager
from app.models import PrivacyOption, Hike
from datetime import date

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

    @users.command()
    def demo():
        # Setting up managers
        tm = TrailManager(session=db.session)
        um = UserManager(session=db.session)
        # Adding users
        if not um.list_users(username="steven"):
            steven = um.add_user(username="steven",email="steven@provider.com",password="mynameissteven",privacy=PrivacyOption.public)
        else:
            steven = um.list_users(username="steven")

        if not um.list_users(username="katherine"):
            katherine = um.add_user(username="katherine",email="katherine@provider.com",password="mynameiskatherine",privacy=PrivacyOption.public)
        else:
            katherine = um.list_users(username="katherine")

        if not um.list_users(username="jay"):
            jay = um.add_user(username="jay",email="jay@provider.com",password="mynameisjay",privacy=PrivacyOption.public)
        else:
            jay = um.list_users(username="jay")

        if not um.list_users(username="anna"):
            anna = um.add_user(username="anna",email="anna@provider.com",password="mynameisanna",privacy=PrivacyOption.friends)
        else:
            anna = um.list_users(username="anna")

        if not um.list_users(username="bart"):
            bart = um.add_user(username="bart",email="bart@provider.com",password="mynameisbart",privacy=PrivacyOption.friends)
        else:
            bart = um.list_users(username="bart")

        if not um.list_users(username="felicia"):
            felicia = um.add_user(username="felicia",email="felicia@provider.com",password="mynameisfelicia",privacy=PrivacyOption.private)
        else:
            felicia = um.list_users(username="felicia")

        # Getting trails
        grp_groenegordel = tm.list_trails(name="grp-groenegordel") # 147.7 km
        grp_heuvelland = tm.list_trails(name="grp-heuvelland") # 131.6 km 
        grp_waasreynaert = tm.list_trails(name="grp-waasreynaert") # 176.2 km
        gr5 = tm.list_trails(name="gr5") # 251.3 km
        gr5a_ronde = tm.list_trails(name="gr5a-ronde") # 586.4 km
        gr128 = tm.list_trails(name="gr128") # 483.1 km
        gr564 = tm.list_trails(name="gr564") # 167.3 km

        # Adding hikes for Steven
        hm_steven = HikeManager(session=db.session,user=steven)
        hikes = Hike.query.where(Hike.user_id==steven.id).all()
        for hike in hikes:
            db.session.delete(hike)
        db.session.commit()
        hm_steven.add_hike(
            trail_id=grp_groenegordel.id,
            km_start=2.3,
            km_end=14.5,
            timestamp=date(year=2022,month=2,day=5),
        )
        hm_steven.add_hike(
            trail_id=grp_groenegordel.id,
            km_start=23.7,
            km_end=40.2,
            timestamp=date(year=2022,month=2,day=12),
        )
        hm_steven.add_hike(
            trail_id=grp_groenegordel.id,
            km_start=66.8,
            km_end=84.2,
            timestamp=date(year=2022,month=2,day=18),
        )
        hm_steven.add_hike(
            trail_id=grp_groenegordel.id,
            km_start=122.3,
            km_end=146.1,
            timestamp=date(year=2022,month=2,day=23),
        )
        hm_steven.add_hike(
            trail_id=gr5.id,
            km_start=210.3,
            km_end=221.7,
            timestamp=date(year=2019,month=7,day=23),
        )
        hm_steven.add_hike(
            trail_id=gr5.id,
            km_start=154.3,
            km_end=173.0,
            timestamp=date(year=2020,month=9,day=17),
        )
        hm_steven.add_hike(
            trail_id=gr5.id,
            km_start=33.9,
            km_end=45.3,
            timestamp=date(year=2020,month=9,day=30),
        )

        # Adding hikes for Katherine
        hm_katherine = HikeManager(session=db.session,user=katherine)
        hikes = Hike.query.where(Hike.user_id==katherine.id).all()
        for hike in hikes:
            db.session.delete(hike)
        db.session.commit()
        hm_katherine.add_hike(
            trail_id=gr128.id,
            km_start=202.3,
            km_end=222.5,
            timestamp=date(year=2021,month=7,day=1),
        )
        hm_katherine.add_hike(
            trail_id=gr128.id,
            km_start=252.6,
            km_end=281.0,
            timestamp=date(year=2021,month=7,day=10),
        )
        hm_katherine.add_hike(
            trail_id=gr128.id,
            km_start=12.3,
            km_end=24.8,
            timestamp=date(year=2021,month=7,day=20),
        )
        hm_katherine.add_hike(
            trail_id=gr128.id,
            km_start=101.5,
            km_end=130.4,
            timestamp=date(year=2021,month=7,day=30),
        )
        hm_katherine.add_hike(
            trail_id=gr128.id,
            km_start=88.0,
            km_end=67.3,
            timestamp=date(year=2021,month=8,day=10),
        )
        hm_katherine.add_hike(
            trail_id=grp_waasreynaert.id,
            km_start=102.0,
            km_end=124.7,
            timestamp=date(year=2020,month=5,day=4),
        )
        hm_katherine.add_hike(
            trail_id=grp_waasreynaert.id,
            km_start=124.7,
            km_end=138.3,
            timestamp=date(year=2020,month=5,day=10),
        )
        hm_katherine.add_hike(
            trail_id=gr564.id,
            km_start=56.4,
            km_end=76.3,
            timestamp=date(year=2020,month=6,day=22),
        )
        hm_katherine.add_hike(
            trail_id=gr564.id,
            km_start=78.4,
            km_end=90.7,
            timestamp=date(year=2020,month=6,day=27),
        )








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