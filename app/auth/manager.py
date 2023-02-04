from app.models import User, Following, PrivacyOption

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
        
    def add_user(self, username, email, password, privacy=PrivacyOption.public):
        user = User(username=username, email=email, privacy=privacy)
        user.set_password(password)
        self.session.add(user)
        self.session.commit()
        return user

    def is_following(self, source_user, target_user):
        following = Following.query.where(Following.source_id==source_user.id).where(Following.target_id==target_user.id).one_or_none()
        if following:
            return True
        return False

    def is_following_accepted(self, source_user, target_user):
        following = Following.query.where(Following.source_id==source_user.id).where(Following.target_id==target_user.id).one_or_none()
        if following and following.accepted:
            return True
        return False

    def follow_user(self, target_username):
        if self.user:
            target = self.list_users(username=target_username)
            if target and target.privacy is not PrivacyOption.private and not self.is_following(source_user=self.user, target_user=target):
                accepted = False
                if target.privacy is PrivacyOption.public:
                    accepted = True
                following = Following(source_id=self.user.id, target_id=target.id, accepted=accepted)
                self.session.add(following)
                self.session.commit()

    def unfullow_user(self, target_username):
        if self.user:
            target = self.list_users(username=target_username)
            if target and self.is_following(source_user=self.user, target_user=target):
                following = Following.query.where(Following.source_id==self.user.id).where(Following.target_id==target.id).one_or_none()
                self.session.delete(following)
                self.session.commit()

    def accept_following(self, source_username):
        if self.user:
            source = self.list_users(username=source_username)
            if source and self.is_following(source_user=source, target_user=self.user):
                following = Following.query.where(Following.source_id==source.id).where(Following.target_id==self.user.id).one_or_none()
                if not following.accepted:
                    following.accepted = True
                    self.session.commit()

    def set_privacy(self, new_privacy):
        if self.user:
            if new_privacy is PrivacyOption.private: # remove all follows
                followings = Following.query.where(Following.target_id==self.user.id)
                followings.delete()
                self.session.commit()
            if new_privacy is PrivacyOption.public: # approve all follows
                followings = Following.query.where(Following.target_id==self.user.id).update({"accepted":True})
                self.session.commit()
            self.user.privacy = new_privacy
            self.session.commit()