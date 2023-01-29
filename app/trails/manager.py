from app.models import User, Trail, Hike, AuthorizationException, FileMissingException
from pathlib import Path
from app.analysis import calculate_stats

class TrailManager():
    def __init__(self, session, actor: User=None):
        self.actor = actor
        self.session = session

    def add_trail(self, name: str, dispname: str, fullname: str):
        if not self.actor.is_admin:
            raise AuthorizationException
        path_to_csv_file = Path(f"app/data/{name}.csv")
        if not path_to_csv_file.is_file():
            raise FileMissingException
        trail = Trail(
            name=name,
            dispname=dispname,
            fullname=fullname,
        )
        self.session.add(trail)
        self.session.commit()
        return trail

    def delete_trail(self, name: str):
        if not self.actor.is_admin:
            raise AuthorizationException
        trail = Trail.query.where(Trail.name==name).one_or_none()
        if trail:
            self.session.delete(trail)
            self.session.commit
    
    def edit_trail(self, id: int, new_name:str="", new_dispname:str="", new_fullname:str=""):
        if not self.actor.is_admin:
            raise AuthorizationException
        trail = Trail.query.where(Trail.id==id).one()
        if new_name:
            path_to_csv_file = Path(f"app/data/{new_name}.csv")
            if not path_to_csv_file.is_file():
                raise FileMissingException
            trail.name = new_name
        if new_dispname:
            trail.dispname = new_dispname
        if new_fullname:
            trail.fullname = new_fullname
        self.session.commit()

    def list_trails(self, name=""):
        if name:
            try:
                return Trail.query.where(Trail.name==name).one()
            except:
                return None
        return Trail.query.order_by(Trail.name).all()

    def get_user_statistics(self, username):
        user = User.query.where(User.username==username).one()
        trails = Trail.query.join(Hike, Hike.trail_id == Trail.id, isouter=True).where(Hike.user_id==user.id).all()
        hikes = Hike.query.where(Hike.user_id==user.id).all()
        stats = calculate_stats(hikes)
        return UserStatistics(user=user,trails=trails,hikes=hikes,stats=stats)


class UserStatistics():
    def __init__(self,user,trails,hikes,stats):
        self.user = user
        self.trails = trails
        self.hikes = hikes
        self.stats = stats