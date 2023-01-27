from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import csv
from langdetect import detect, LangDetectException
from app import db
from app.trails.forms import TrailForm
from app.models import User, Trail, Hike
from app.trails import bp
import math
from app.analysis import calculate_stats


# Show all trails
@bp.route('/trails', methods=['GET'])
@login_required
def show_all_trails():
    trails = Trail.query.order_by(Trail.name).all()
    return render_template(
        'trails.html',
        title='List of trails',
        trails=trails
    )

# Add a new trail
@bp.route('/trails/new', methods=['GET', 'POST'])
@login_required
def add_trail():
    form = TrailForm()
    if form.validate_on_submit():
        trail = Trail(
            name=form.name.data,
            dispname=form.dispname.data,
            fullname=form.fullname.data,
        )
        db.session.add(trail)
        db.session.commit()
        flash(f'You have added the new trail {form.dispname.data}.')
        return redirect(url_for('trails.show_all_trails'))
    return render_template(
        'trail_new.html',
        title='Add new trail',
        form=form,
    )

# Show a single trail
@bp.route('/trails/<name>', methods=['GET'])
@login_required
def show_single_trail(name):
    trail = Trail.query.filter_by(name=name).first_or_404()
    geometry = trail.get_geometry()
    return render_template(
        'trail.html',
        title=f'Details of trail {name}',
        trail=trail,
        raw_coordinates=geometry['coordinates'], # TODO: can I just pass the geometry object?
        raw_cumulative_distances=geometry['cumulative_distances'],
        raw_center_coordinate=geometry['center_coordinate'],
    )

# Edit a trail
@bp.route('/trails/<name>/edit', methods=['GET', 'POST'])
@login_required
def edit_trail(name):
    trail = Trail.query.filter_by(name=name).first_or_404()
    geometry = trail.get_geometry()
    form = TrailForm()
    if request.method == "POST" and form.validate_on_submit(): # Post edits to the trail
        trail.fill_from_form(form)
        db.session.commit()
        flash(f"The edits to trail {trail.dispname} have been saved.")
        return redirect(url_for('trails.show_single_trail', name=trail.name))
    elif request.method == 'GET': # Display the form to edit the trail
        form.fill_from_trail(trail=trail)
    return render_template(
        'trail_edit.html',
        title='Edit Trail',
        form=form,
        trail=trail,
    )

# Delete a trail
@bp.route('/trails/<name>/delete', methods=['POST'])
@login_required
def delete_trail(name):
    trail = Trail.query.filter_by(name=name).first_or_404()
    db.session.delete(trail)
    db.session.commit()
    flash(f"Trail {trail.dispname} has been deleted.")
    return redirect(url_for('main.show_all_trails'))

# Show the trails on which a user has hiked
@bp.route('/trails/user/<username>', methods=['GET'])
@login_required
def show_user_trails(username):
    user = User.query.where(User.username==username).one()
    trails = Trail.query.join(Hike, Hike.trail_id == Trail.id, isouter=True).where(Hike.user_id==user.id).all()
    hikes = Hike.query.where(Hike.user_id==user.id).all()
    stats = calculate_stats(hikes)
    return render_template(
        'trails_user.html',
        title='Trails by user',
        trails=trails,
        user=user,
        stats=stats,
    )