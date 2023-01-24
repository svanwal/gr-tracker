from csv import writer
import math


EARTH_A = 6378137 # Radius of Earth [m]
EARTH_E2 = 0.006694380004260827 # Eccentricy of Earth [-]


class Coordinate():
    def __init__(self, latitude_deg, longitude_deg, elevation_meter):
        self.latitude_deg = float(latitude_deg)
        self.longitude_deg = float(longitude_deg)
        self.latitude_rad = math.radians(self.latitude_deg) # alias phi
        self.longitude_rad = math.radians(self.longitude_deg) # alias lambda
        self.elevation_meter = float(elevation_meter) # alias h
        self.to_cartesian()

    def to_cartesian(self):
        sin_phi = math.sin(self.phi_rad)
        cos_phi = math.cos(self.phi_rad)
        sin_lam = math.sin(self.lam_rad)
        cos_lam = math.cos(self.lam_rad)
        self.chi = math.sqrt(1 - EARTH_E2*sin_phi*sin_phi)
        self.x = (EARTH_A/self.chi + self.elevation_meter)*cos_phi*cos_lam
        self.y = (EARTH_A/self.chi + self.elevation_meter)*cos_phi*sin_lam
        self.z = (EARTH_A*(1 - EARTH_E2)/self.chi + self.elevation_meter)*sin_phi

    def distance_to(self, other):
        vector_difference = [
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        ]
        return vector_norm(vector_difference)

    @property
    def phi_rad(self):
        return self.latitude_rad

    @property
    def lam_rad(self):
        return self.longitude_rad

    @property
    def xyz(self):
        return [self.x, self.y, self.z]


def vector_norm(vector):
    return math.sqrt(
        vector[0]*vector[0]
        + vector[1]*vector[1]
        + vector[2]*vector[2]
    )


def calculate_cumulative_distances(coordinates):
    cumulative_distances = [0.0]
    for i in range(1,len(coordinates)):
        previous_coordinate = coordinates[i-1]
        current_coordinate = coordinates[i]
        distance_between_coordinates = previous_coordinate.distance_to(current_coordinate)/1000 # in kilometers
        previous_cumulative_distance = cumulative_distances[-1]
        current_cumulative_distance = previous_cumulative_distance + distance_between_coordinates
        # print(f"old dcum = {previous_cumulative_distance}, new d={distance_between_coordinates}, new dcum={current_cumulative_distance}")
        cumulative_distances.append(current_cumulative_distance) 
    return cumulative_distances
