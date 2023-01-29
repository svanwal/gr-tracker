from datetime import datetime, date
from app.models import User, Trail, Hike, LoggedInException, ExistenceException, LocationException, AuthorizationException
from app.geometry import calculate_distance

class HikeManager():
    def __init__(self, session, user: User=None):
        self.user = user
        self.session = session

    def add_hike(self, trail_id: int, km_start:float, km_end:float, timestamp: date=date.today()):
        if not self.user:
            raise LoggedInException
        trail = Trail.query.where(Trail.id==trail_id).one()
        if not trail:
            raise ExistenceException
        if not 0 <= km_start <= trail.length or not 0 <= km_end <= trail.length:
            raise LocationException
        distance = calculate_distance(km_start, km_end)
        hike = Hike(
            trail_id=trail_id,
            walker=self.user,
            timestamp=timestamp,
            km_start=km_start,
            km_end=km_end,
            distance=distance,
        )
        self.session.add(hike)
        self.session.commit()
        return hike

    def delete_hike(self, id: int):
        hike = Hike.query.where(Hike.id==id).one()
        if not hike:
            raise ExistenceException
        if hike.walker.id != self.user.id:
            raise AuthorizationException
        self.session.delete(hike)
        self.session.commit()

    def edit_hike(self, id: int, new_timestamp: datetime="", new_km_start: float="", new_km_end:float=""):
        hike = Hike.query.where(Hike.id==id).one()
        if not hike:
            raise ExistenceException
        if hike.walker.id != self.user.id:
            raise AuthorizationException
        trail = Trail.query.where(Trail.id==hike.trail_id).one()
        if new_timestamp:
            hike.timestamp = new_timestamp
        if new_km_start:
            hike.km_start = new_km_start
        if new_km_end:
            hike.km_end = new_km_end
        if not 0 <= hike.km_start <= trail.length or not 0 <= hike.km_end <= trail.length:
            raise LocationException
        hike.distance = calculate_distance(hike.km_start, hike.km_end)
        self.session.commit()
        return hike