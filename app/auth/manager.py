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
        return User.query.order_by(User.name).all()
        
    def add_user(self, username, email, password, privacy=PrivacyOption.public):
        user = User(username=username, email=email, privacy=privacy)
        user.set_password(password)
        self.session.add(user)
        self.session.commit()
        return user

    def list_follows(self):
        return Following.query.where(Following.source_id==self.user.id).all()

    def follow_user(self, target_username):
        if self.user:
            target = self.list_users(username=target_username)
            # print(f'privacy of target {target.username}')
            # print(target.privacy)
            if target:
                if target.privacy is not PrivacyOption.private:
                    if not self.user.username==target_username:
                        if not self.user.is_following(target_user=target):
                            accepted = False
                            if target.privacy is PrivacyOption.public:
                                accepted = True
                            # print(f"Adding following of user {self.user.username} to {target_username}")
                            following = Following(source_id=self.user.id, target_id=target.id, accepted=accepted)
                            self.session.add(following)
                            self.session.commit()

    def unfollow_user(self, target_username):
        if self.user:
            target = self.list_users(username=target_username)
            if target and self.user.is_following(target_user=target):
                following = Following.query.where(Following.source_id==self.user.id).where(Following.target_id==target.id).one_or_none()
                self.session.delete(following)
                self.session.commit()

    def accept_following(self, source_username):
        if self.user:
            source = self.list_users(username=source_username)
            if source and source.is_following(target_user=self.user):
                following = Following.query.where(Following.source_id==source.id).where(Following.target_id==self.user.id).one_or_none()
                if following and not following.accepted:
                    following.accepted = True
                    self.session.commit()

    def remove_following(self, source_username):
        if self.user:
            source = self.list_users(username=source_username)
            if source and source.is_following(target_user=self.user):
                following = Following.query.where(Following.source_id==source.id).where(Following.target_id==self.user.id).one_or_none()
                if following:
                    self.session.delete(following)
                    self.session.commit()

    def cancel_outgoing_following(self, target_username):
        if self.user:
            target = self.list_users(username=target_username)
            if target and self.user.is_following(target_user=target):
                following = Following.query.where(Following.source_id==self.user.id).where(Following.target_id==target.id).one_or_none()
                if following:
                    self.session.delete(following)
                    self.session.commit()

    def follow_status(self, target_username):
        target = self.list_users(username=target_username)
        following = Following.query.where(Following.source_id==self.user.id).where(Following.target_id==target.id).one_or_none()
        if not following:
            return None
        return following.accepted
        # if following.accepted:
        #     return "accepted"
        # return "pending"

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

    def get_outgoing_follows(self):
        followings = {}
        if self.user:
            follows = Following.query.where(Following.source_id==self.user.id)
            for follow in follows:
                user = User.query.where(User.id==follow.target_id).one()
                followings[user.username] = follow.accepted
        return followings
            
    def get_incoming_follows(self):
        followings = {}
        if self.user:
            follows = Following.query.where(Following.target_id==self.user.id)
            for follow in follows:
                user = User.query.where(User.id==follow.source_id).one()
                followings[user.username] = follow.accepted
        return followings