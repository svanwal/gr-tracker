from app.models import User

class UserManager():
    def __init__(self, session, user: User=None):
        self.user = user
        self.session = session

    def list_users(self, username=""):
        if username:
            try:
                return User.query.where(User.username==username).one()
            except:
                return None
        return User.query.order_by(Trail.name).all()
        