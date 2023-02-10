from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import csv
from langdetect import detect, LangDetectException
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Post, Trail, Hike, Following, PrivacyOption
from app.translate import translate
from app.main import bp
from app.trails.manager import TrailManager
from app.hikes.manager import HikeManager
import math
from app.auth.manager import UserManager
from flask_login import AnonymousUserMixin


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    tm = TrailManager(session=db.session)
    trails = tm.list_trails()
    trails_coordinates = []
    trails_names = []
    names = []
    for trail in trails:
        geometry = trail.get_geometry()
        trails_coordinates.append(geometry.coordinates)
        trails_names.append(trail.dispname)
        names.append(trail.name)
    return render_template('index.html', title='Home', user=current_user, ntrails=len(trails), raw_trails_coordinates=trails_coordinates, trailnames=trails_names, raw_names=names)


@bp.route('/user/<username>')
@login_required
def user(username):
    if current_user.username == username: # view own profile
        print("viewing own profile")
        um = UserManager(session=db.session,user=current_user)
        user_self = um.list_users(username=username)
        outgoing_follows = um.get_outgoing_follows()
        incoming_follows = um.get_incoming_follows()
        
        outgoing = []
        for name, accepted in outgoing_follows.items():
            user = User.query.where(User.username==name).one()
            outgoing.append((name, accepted))

        incoming = []
        for name, accepted in incoming_follows.items():
            user = User.query.where(User.username==name).one()
            incoming.append((name, accepted))

        return render_template('user_self.html', user=user_self, outgoing=outgoing, incoming=incoming, privacy=user_self.privacy.value)

    elif current_user.is_authenticated: # view someone else's profile as user
        print("viewing someone else's profile while logged in")
        um = UserManager(session=db.session,user=current_user)
        user = um.list_users(username=username)
        outgoing_follows = um.get_outgoing_follows()
        friends = um.follow_status(target_username=username)
        return render_template('user_other.html', user=user, friends=friends, target_privacy=user.privacy.value)

    else: # view someone else's profile anonymously
        print("viewing someone else's profile anonymously")
    return redirect(url_for('main.index'))

    # um = UserManager(session=db.session,user=current_user)
    # user = User.query.filter_by(username=username).first_or_404()
    # form = EmptyForm()
    # outgoing_follows = um.get_outgoing_follows()
    # incoming_follows = um.get_incoming_follows()

    # friends = None
    # if not isinstance(current_user, AnonymousUserMixin):
    #     hm = HikeManager(session=db.session,user=current_user)
    #     friends = um.follow_status(target_username=username)
    # return render_template('user.html', user=user, form=form, friends=friends)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.privacy = form.privacy.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.privacy.data = current_user.privacy.value
    return render_template('edit_profile.html', title='Edit Profile',form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    um = UserManager(session=db.session, user=current_user)
    target_user = um.list_users(username=username)
    if target_user:
        if not current_user.is_following(target_user):
            um.follow_user(target_username=target_user.username)
            flash('Follow request sent')
            return redirect(url_for('main.user', username=username))
        flash('You already sent a follow request to this user')
        return redirect(url_for('main.user', username=username))
    flash('User does not exist')
    return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    um = UserManager(session=db.session, user=current_user)
    target_user = um.list_users(username=username)
    if target_user:
        if current_user.is_following(target_user):
            um.unfollow_user(target_username=target_user.username)
            flash('Removed follower')
        return redirect(url_for('main.user', username=username))
    flash('User does not exist')
    return redirect(url_for('main.index'))


@bp.route('/accept_follow/<username>', methods=['POST'])
@login_required
def accept_follow(username):
    um = UserManager(session=db.session, user=current_user)
    source_user = um.list_users(username=username)
    if source_user and current_user.privacy is not PrivacyOption.public:
        if source_user.is_following(current_user) and not source_user.is_following_accepted(current_user):
            um.accept_following(source_username=source_user.username)
            flash('Accepted follow request')
    return redirect(url_for('main.user',username=current_user.username))


@bp.route('/remove_follow/<username>', methods=['POST'])
@login_required
def remove_follow(username):
    print('removing follow')
    um = UserManager(session=db.session, user=current_user)
    source_user = um.list_users(username=username)
    if source_user and current_user.privacy is not PrivacyOption.public:
        print('1')
        if source_user.is_following(current_user):
            print('2')
            um.remove_following(source_username=source_user.username)
            flash('Removed follower')
    return redirect(url_for('main.user',username=current_user.username))


@bp.route('/cancel_follow_request/<username>', methods=['POST'])
@login_required
def cancel_follow_request(username):
    um = UserManager(session=db.session, user=current_user)
    target_user = um.list_users(username=username)
    if target_user:
        if source_user.is_following(target_user):
            um.cancel_follow_request(target_username=target_user.username)
            flash('Removed follow request')
    return redirect(url_for('main.user',username=current_user.username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)