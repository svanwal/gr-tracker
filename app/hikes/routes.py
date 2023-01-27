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
from app.models import User, Trail, Hike
from app.analysis import calculate_stats


# View all hikes
@bp.route('/hikes', methods=['GET', 'POST'])
@login_required
def show_all_hikes():
    hikes = Hike.query.order_by(Hike.timestamp.desc()).all()
    form = TrailSelectionForm()
    if form.validate_on_submit():
        trail = Trail.query.where(Trail.id==form.trail.data).one_or_404()
        return redirect(url_for('hikes.add_hike', name=trail.name))
    return render_template('hikes.html', title='Hike', hikes=hikes, form=form)


# View all hikes by a specific user
@bp.route('/hikes/user/<username>', methods=['GET', 'POST'])
@login_required
def show_user_hikes(username):
    user = User.query.where(User.username==username).one()
    hikes = Hike.query.where(Hike.walker==user).order_by(Hike.timestamp.desc()).all()
    form = TrailSelectionForm()
    if form.validate_on_submit():
        trail = Trail.query.where(Trail.id==form.trail.data).one_or_404()
        return redirect(url_for('hikes.add_hike', name=trail.name))
    return render_template('hikes.html', title='Hike', hikes=hikes, username=user.username, form=form)


# View a single hike
@bp.route('/hikes/<id>', methods=['GET'])
@login_required
def show_single_hike(id):
    hike = Hike.query.where(Hike.id==id).one_or_404()
    trail = hike.path
    geometry = trail.get_geometry()
    hike_coordinates = trail.get_coordinate_range(km_start=hike.km_start,km_end=hike.km_end)
    return render_template(
        'hike.html',
        title='Hike',
        hike=hike,
        trail=trail,
        raw_coordinates=geometry['coordinates'], # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry['cumulative_distances'],
        raw_center_coordinate=geometry['center_coordinate'],
        raw_hike_coordinates=hike_coordinates,
    )


# View a user's hikes on a specific trail, with stats
@bp.route('/hikes/<trailname>/<username>', methods=['GET'])
@login_required
def show_trail_hikes(trailname,username):
    trail = Trail.query.where(Trail.name==trailname).one_or_404()
    user = User.query.where(User.username==username).one_or_404()
    hikes = Hike.query.where(Hike.trail_id==trail.id).where(Hike.user_id==user.id).all()
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
        raw_coordinates=geometry['coordinates'], # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry['cumulative_distances'],
        raw_center_coordinate=geometry['center_coordinate'],
        raw_hike_coordinates=hikes_coordinates,
        stats=stats,
    )


# Add a new hike
@bp.route('/hikes/new/<name>', methods=['GET', 'POST'])
@login_required
def add_hike(name):
    trail = Trail.query.where(Trail.name==name).one_or_404()
    geometry = trail.get_geometry()
    form = HikeForm(trail_id=trail.id)
    if form.validate_on_submit():
        distance = abs(form.km_start.data - form.km_end.data)
        hike = Hike(
            trail_id=trail.id,
            walker=current_user,
            timestamp=form.timestamp.data,
            km_start=form.km_start.data,
            km_end=form.km_end.data,
            distance=distance,
        )
        db.session.add(hike)
        db.session.commit()
        flash(f"Successfully registered a new hike on trail {trail.dispname}")
        return redirect(url_for('hikes.show_user_hikes', username=current_user.username))
    return render_template(
        'hike_new.html',
        title='Add new hike',
        form=form,
        trail=trail,
        raw_coordinates=geometry['coordinates'], # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry['cumulative_distances'],
        raw_center_coordinate=geometry['center_coordinate'],
    )
    

# Edit a hike
@bp.route('/hikes/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_hike(id):
    hike = Hike.query.where(Hike.id==id).one_or_404()
    trail = hike.path
    geometry = trail.get_geometry()
    hike_coordinates = trail.get_coordinate_range(km_start=hike.km_start,km_end=hike.km_end)
    form = HikeForm(trail_id=trail.id)
    if request.method == "POST" and form.validate_on_submit(): # Post edits to the hike
        hike.fill_from_form(form)
        db.session.commit()
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
        raw_coordinates=geometry['coordinates'], # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry['cumulative_distances'],
        raw_center_coordinate=geometry['center_coordinate'],
    )


# Delete a hike
@bp.route('/hikes/<id>/delete', methods=['POST'])
@login_required
def delete_hike(id):
    hike = Hike.query.filter_by(id=id).first_or_404()
    trail = hike.path
    db.session.delete(hike)
    db.session.commit()
    flash(f"Your hike has been deleted.")
    return redirect(url_for('hikes.show_all_hikes'))
