from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import csv
from langdetect import detect, LangDetectException
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, EditTrailForm, HikeForm
from app.models import User, Post, Trail, Hike
from app.translate import translate
from app.main import bp
from app.main.geometry import process_gpx
import math


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    hikeform = HikeForm()
    if hikeform.validate_on_submit():
        print(f"submitted form kms are {hikeform.km_start.data} {hikeform.km_end.data}")
        hike = Hike(
            km_start=hikeform.km_start.data,
            km_end=hikeform.km_end.data,
            trail_id=hikeform.trail.data,
            walker=current_user,
            d = abs(hikeform.km_start.data - hikeform.km_end.data)
        )
        print(f"Received new hike from km {hike.km_start} to {hike.km_end}")
        db.session.add(hike)
        db.session.commit()
        flash('Hike submission received!')
        return redirect(url_for('main.index'))
    hikes = Hike.query.order_by(Hike.timestamp.desc()).all()
    return render_template('index.html', title='Home', form=hikeform, hikes=hikes)


@bp.route('/hike')
@login_required
def hike():
    hikes = Hike.query.order_by(Hike.timestamp.desc()).all()
    return render_template('hike.html', title='Hike', hikes=hikes)


@bp.route('/myhikes')
@login_required
def myhikes():
    hikes = Hike.query.where(Hike.user_id==current_user.id).order_by(Hike.timestamp.desc()).all()
    return render_template('hike.html', title='Hike', hikes=hikes)


@bp.route('/hike_detail/<hike_id>')
@login_required
def hike_detail(hike_id):
    hike = Hike.query.where(Hike.id==hike_id).one()
    trail = hike.path
    # grab trail coords
    with open(trail.filename_processed, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        data = list(reader)
    coords = [[float(row[1]),float(row[0])] for row in data]
    dcum = [float(row[3]) for row in data]
    center = coords[int(len(coords)/2)]
    # grab subset covered by hike
    dcum_start = min(dcum, key=lambda x:abs(x-hike.km_start))
    i_start = dcum.index(dcum_start)
    dcum_end = min(dcum, key=lambda x:abs(x-hike.km_end))
    i_end = dcum.index(dcum_end)
    hike_coords = coords[i_start:i_end]
    return render_template('hike_detail.html', title='Hike', hike=hike, trail=trail, coords_raw=coords, center_raw=center, dcum_raw=dcum, hike_coords_raw=hike_coords)


@bp.route('/hike_add/<displayname>')
@login_required
def hike_add(displayname):
    hikeform = HikeForm()
    trail = Trail.query.where(Trail.displayname==displayname).one()
    # grab trail coords
    with open(trail.filename_processed, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        data = list(reader)
    coords = [[float(row[1]),float(row[0])] for row in data]
    dcum = [float(row[3]) for row in data]
    center = coords[int(len(coords)/2)]
    return render_template('hike_add.html', title='Hike', form=hikeform, trail=trail, coords_raw=coords, center_raw=center, dcum_raw=dcum)


@bp.route('/trail', methods=['GET','POST'])
@login_required
def trail():
    form = EditTrailForm()
    trails = Trail.query.order_by(Trail.displayname).all()
    if form.validate_on_submit():
        new_trail = Trail(displayname=form.displayname.data, fullname=form.fullname.data, length=0)
        # first just save the gpx file raw
        form.gpx.data.save(new_trail.filename_raw)
        # now process it into what we need
        new_trail.length = process_gpx(new_trail.filename_raw, new_trail.filename_processed)
        new_trail.length = round(new_trail.length,1)
        db.session.add(new_trail)
        db.session.commit()
        flash('You have added a new trail.')
        return redirect(url_for('main.trail'))
    else:
        return render_template(
            'trail.html',
            title='Trails',
            trails=trails,
            form=form,
        )

@bp.route('/mytrails', methods=['GET'])
@login_required
def mytrails():
    trails = db.session.query(Trail).join(Hike, Hike.trail_id == Trail.id, isouter=True).where(Hike.user_id==current_user.id).all()
    return render_template(
        'mytrails.html',
        title='Trails',
        trails=trails,
    )


@bp.route('/mytrails_detail/<displayname>', methods=['GET'])
@login_required
def mytrails_detail(displayname):
    trail = db.session.query(Trail).where(Trail.displayname==displayname).one()
    hikes = db.session.query(Hike).where(Hike.trail_id==trail.id).where(Hike.user_id==current_user.id).all()
    with open(trail.filename_processed, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        data = list(reader)
    coords = [[float(row[1]),float(row[0])] for row in data]
    dcum = [float(row[3]) for row in data]
    center = coords[int(len(coords)/2)]
    hike_coords = []
    for hike in hikes:
        # grab subset covered by hike
        dcum_start = min(dcum, key=lambda x:abs(x-hike.km_start))
        i_start = dcum.index(dcum_start)
        dcum_end = min(dcum, key=lambda x:abs(x-hike.km_end))
        i_end = dcum.index(dcum_end)
        hike_coords.append(coords[i_start:i_end])
    print('n of hikes')
    print(len(hike_coords))
    return render_template(
        'mytrails_detail.html',
        title='Trails',
        trail=trail,
        raw_hikes=hike_coords,
        coords_raw=coords,center_raw=center,dcum_raw=dcum,
        username=current_user.username,
    )

@bp.route('/trail/<displayname>', methods=['GET', 'DELETE'])
@login_required
def trail_detail(displayname):
    trail = Trail.query.filter_by(displayname=displayname).first_or_404()
    emptyform = EmptyForm()
    with open(trail.filename_processed, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        data = list(reader)
    coords = [[float(row[1]),float(row[0])] for row in data]
    dcum = [float(row[3]) for row in data]
    center = coords[int(len(coords)/2)]
    if request.method == 'DELETE':
        db.session.delete(trail)
        db.session.commit()
        return redirect(url_for('main.trail'))
    return render_template('trail_detail.html',title='Trail detail',trail=trail,form=emptyform,coords_raw=coords,center_raw=center,dcum_raw=dcum)


@bp.route('/trail/<displayname>/edit', methods=['GET', 'POST'])
@login_required
def edit_trail(displayname):
    trail = Trail.query.filter_by(displayname=displayname).first_or_404()
    form = EditTrailForm(
        original_displayname=trail.displayname,
        original_fullname=trail.fullname,
    )
    if form.validate_on_submit():
        trail.displayname = form.displayname.data
        trail.fullname = form.fullname.data
        # first just save the gpx file raw
        form.gpx.data.save(trail.filename_raw)
        # now process it into what we need
        trail.length = process_gpx(trail.filename_raw, trail.filename_processed)
        trail.length = round(trail.length,1)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.trail_detail',displayname=trail.displayname))
    elif request.method == 'GET':
        form.displayname.data = trail.displayname
        form.fullname.data = trail.fullname
    return render_template('edit_trail.html', title='Edit Trail',form=form)


@bp.route('/trail/<displayname>/delete')
@login_required
def delete_trail(displayname):
    trail = Trail.query.filter_by(displayname=displayname).first_or_404()
    db.session.delete(trail)
    db.session.commit()
    flash('Trail deleted.')
    return redirect(url_for('main.trail'))














@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


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