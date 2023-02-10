from datetime import datetime, date
from app.models import User, Trail, Hike, LoggedInException, ExistenceException, LocationException, AuthorizationException
from app.geometry import calculate_distance
from app.models import PrivacyOption
from app.auth.manager import UserManager
from flask_login import current_user

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

    def list_own_hikes(self, hike_id="", trail_name=""):
        if trail_name: # on a particular trail
            return ( Hike.query
                .join(User, Hike.user_id == User.id, isouter=True)
                .join(Trail, Hike.trail_id == Trail.id, isouter=True)
                .where(Hike.user_id == self.user.id)
                .where(Trail.name == trail_name)
                .all() )
        
        if hike_id: # return a particular hike by id
            hike = Hike.query.where(Hike.id == hike_id).one_or_none()
            if hike.user_id is self.user.id:
                return hike
            return None

        # list all hikes
        return Hike.query.where(Hike.user_id == self.user.id).all()

    def list_hikes_as_anonymous_user(self, username="", hike_id="", trail_name=""):
        if username: # return all hikes by a particular user
            if trail_name: # on a particular trail
                return ( Hike.query
                .join(User, Hike.user_id==User.id, isouter=True)
                .where(Hike.walker.username==username)
                .where(Hike.path.name==trail_name)
                .where(Hike.walker.privacy==PrivacyOption.public)
                .all() )
            return ( Hike.query
            .join(User, Hike.user_id==User.id, isouter=True)
            .where(User.username==username)
            .where(Hike.walker.privacy==PrivacyOption.public)
            .all() )

        if hike_id: # return a particular hike by id
            hike = Hike.query.where(Hike.id==hike_id).one_or_none()
            if hike.walker.privacy is PrivacyOption.public:
                return hike
            return None

        # list all hikes
        return (Hike.query
        .join(User, Hike.user_id==User.id, isouter=True)
        .where(User.privacy==PrivacyOption.public)
        .order_by(Hike.timestamp)
        .all())

    def list_hikes_as_regular_user(self, username="", hike_id="", trail_name=""):
        um = UserManager(session=self.session, user=self.user)

        if username: # return all hikes by a particular user
            target_user = um.list_users(username=username)
            friends = self.user.is_following_accepted(target_user)
            if friends or target_user.privacy is PrivacyOption.public:
                if trail_name: # on a particular trail
                    return (Hike.query
                    .join(User, Hike.user_id==User.id, isouter=True)
                    .join(Trail, Hike.trail_id==Trail.id, isouter=True)
                    .where(User.username==username)
                    .where(Trail.name==trail_name)
                    .all())
                # all of the user's hikes
                return Hike.query.join(User, Hike.user_id==User.id, isouter=True).where(User.username==username).all()
            return  None

        if hike_id: # return a particular hike by id
            hike = Hike.query.where(Hike.id==hike_id).one_or_none()
            friends = self.user.is_following_accepted(hike.walker)
            if friends or hike.walker.privacy==PrivacyOption.public:
                return hike
            return None
        
        # list all hikes
        raw_hikes = Hike.query.order_by(Hike.timestamp).all()
        hikes = []
        for hike in raw_hikes:
            friends = self.user.is_following_accepted(hike.walker)
            if friends or hike.walker.privacy is PrivacyOption.public or hike.user_id is self.user.id:
                hikes.append(hike)
        return hikes

    def list_hikes(self, username="", hike_id="", trail_name=""):
        if current_user.is_authenticated: # as logged in user
            # print('authenticated')
            if current_user.username == username:
                # print('listing own hikes')
                return self.list_own_hikes(hike_id=hike_id, trail_name=trail_name) # own hikes
            if hike_id: # check if own hike
                hike = Hike.query.where(Hike.id==hike_id).one_or_none()
                if hike.walker.id is self.user.id:
                    # print('listing own hikes')
                    return self.list_own_hikes(hike_id=hike_id, trail_name=trail_name) # own hike
            # print('listing someone elses hikes')
            # print(f"self username {current_user.username} username {username}")
            return self.list_hikes_as_regular_user(username=username, hike_id=hike_id, trail_name=trail_name) # someone else's hikes
        else:
            # print('lanonymously listing hikes')
            return self.list_hikes_as_anonymous_user(username=username, hike_id=hike_id, trail_name=trail_name) # as anonymous user

