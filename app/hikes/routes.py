from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import csv
import math
from langdetect import detect, LangDetectException
from app import db
from app.hikes import bp
from app.hikes.forms import HikeForm, TrailSelectionForm
from app.hikes.manager import HikeManager
from app.trails.manager import TrailManager
from app.models import User, Trail, Hike
from app.analysis import calculate_stats
from app.auth.manager import UserManager
import json
from markupsafe import escape


# View all hikes
@bp.route('/hikes', methods=['GET', 'POST'])
def show_all_hikes():
    hm = HikeManager(session=db.session,user=current_user)
    hikes = hm.list_hikes()
    form = TrailSelectionForm()
    if form.validate_on_submit():
        tm = TrailManager(session=db.session,user=current_user)
        trail = tm.list_trails(name=form.trail.data)
        return redirect(url_for('hikes.add_hike', name=trail.name))
    return render_template('hikes.html', title='Hike', hikes=hikes, form=form)


# View all hikes by a specific user
@bp.route('/hikes/user/<username>', methods=['GET', 'POST'])
@login_required
def show_user_hikes(username):
    hm = HikeManager(session=db.session,user=current_user)
    hikes = hm.list_hikes(username=username)
    form = TrailSelectionForm()
    if form.validate_on_submit():
        tm = TrailManager(session=db.session,user=current_user)
        trail = tm.list_trails(name=form.trail.data)
        return redirect(url_for('hikes.add_hike', name=trail.name))
    return render_template('hikes.html', title='Hike', hikes=hikes, username=username, form=form)


# View a single hike
@bp.route('/hikes/<id>', methods=['GET'])
@login_required
def show_single_hike(id):
    hm = HikeManager(session=db.session,user=current_user)
    hike = hm.list_hikes(id=id)
    trail = hike.path
    geometry = trail.get_geometry()
    hike_coordinates = trail.get_coordinate_range(km_start=hike.km_start,km_end=hike.km_end)
    return render_template(
        'hike.html',
        title='Hike',
        hike=hike,
        trail=trail,
        raw_coordinates=geometry.coordinates, # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry.distances,
        raw_center_coordinate=geometry.center,
        raw_hike_coordinates=hike_coordinates,
    )


# View a user's hikes on a specific trail, with stats
@bp.route('/hikes/<trailname>/<username>', methods=['GET'])
@login_required
def show_trail_hikes(trailname,username):
    tm = TrailManager(session=db.session,user=current_user)
    trail = tm.list_trails(name=trailname)
    um = UserManager(session=db.session,user=current_user)
    user = um.list_users(username=username)
    hm = HikeManager(session=db.session,user=current_user)
    hikes = hm.list_hikes_by_user_on_trail(user.id, trail.id)
    stats = calculate_stats(hikes)
    geometry = trail.get_geometry()
    hikes_coordinates = []
    for hike in hikes:
        hikes_coordinates.append(trail.get_coordinate_range(km_start=hike.km_start,km_end=hike.km_end))
    return render_template(
        'hikes_trail.html',
        title='User hikes on a particular trail',
        trail=trail,
        user=user,
        hikes=hikes,
        raw_coordinates=geometry.coordinates, # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry.distances,
        raw_center_coordinate=geometry.center,
        raw_hike_coordinates=hikes_coordinates,
        stats=stats,
    )


# Add a new hike
@bp.route('/hikes/new/<name>', methods=['GET', 'POST'])
@login_required
def add_hike(name):
    tm = TrailManager(session=db.session,user=current_user)
    trail = tm.list_trails(name=name)
    geometry = trail.get_geometry()
    form = HikeForm(trail_id=trail.id)
    if form.validate_on_submit():
        hm = HikeManager(session=db.session,user=current_user)
        hm.add_hike(trail_id=trail.id, km_start=form.km_start.data, km_end=form.km_end.data, timestamp=form.timestamp.data)
        flash(f"Successfully registered a new hike on trail {trail.dispname}")
        return redirect(url_for('hikes.show_user_hikes', username=current_user.username))
    raw_geometry = escape(json.dumps(geometry.__dict__))
    return render_template(
        'hike_new.html',
        title='Add new hike',
        form=form,
        trail=trail,
        raw_coordinates=geometry.coordinates, # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry.distances,
        raw_center_coordinate=geometry.center,
    )


# Edit a hike
@bp.route('/hikes/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_hike(id):
    hm = HikeManager(session=db.session,user=current_user)
    hike = hm.list_hikes(id=id)
    trail = hike.path
    geometry = trail.get_geometry()
    hike_coordinates = trail.get_coordinate_range(km_start=hike.km_start,km_end=hike.km_end)
    form = HikeForm(trail_id=trail.id)
    if request.method == "POST" and form.validate_on_submit(): # Post edits to the hike
        hm.edit_hike(
            id=hike.id,
            new_timestamp=form.timestamp.data,
            new_km_start=form.km_start.data,
            new_km_end=form.km_end.data,
        )
        flash(f"The edits to hike {hike.id} have been saved.")
        return redirect(url_for('hikes.show_single_hike', id=hike.id))
    elif request.method == 'GET': # Display the form to edit the trail
        form.fill_from_hike(hike=hike)
    return render_template(
        'hike_edit.html',
        title='Edit Hike',
        form=form,
        hike=hike,
        trail=trail,
        raw_coordinates=geometry.coordinates, # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry.distances,
        raw_center_coordinate=geometry.center,
    )


# Delete a hike
@bp.route('/hikes/<id>/delete', methods=['POST'])
@login_required
def delete_hike(id):
    hm = HikeManager(session=db.session,user=current_user)
    hike = hm.delete_hike(id=id)
    flash(f"Your hike has been deleted.")
    return redirect(url_for('hikes.show_all_hikes'))
