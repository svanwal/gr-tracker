from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import csv
from langdetect import detect, LangDetectException
from app import db
from app.trails.forms import TrailForm
from app.trails.manager import TrailManager
from app.models import User, Trail, Hike
from app.trails import bp
import math
from app.analysis import calculate_stats


# Show all trails
@bp.route('/trails', methods=['GET'])
def show_all_trails():
    tm = TrailManager(session=db.session)
    trails = tm.list_trails()
    return render_template(
        'trails.html',
        title='List of trails',
        trails=trails,
        user=current_user,
    )


# Add a new trail
@bp.route('/trails/new', methods=['GET', 'POST'])
@login_required
def add_trail():
    tm = TrailManager(session=db.session,actor=current_user)
    form = TrailForm()
    if form.validate_on_submit():
        name = form.name.data
        dispname = form.dispname.data
        fullname = form.fullname.data
        trail = tm.add_trail(name=name,dispname=dispname,fullname=fullname)
        if not trail:
            flash(f"Unable to add new trail. Please contact an administrator.")
        flash(f"You have added the new trail {dispname}.")
        return redirect(url_for('trails.show_all_trails'))
    return render_template(
        'trail_new.html',
        title='Add new trail',
        form=form,
    )


# Show a single trail
@bp.route('/trails/<name>', methods=['GET'])
def show_single_trail(name):
    tm = TrailManager(session=db.session,actor=current_user)
    trail = tm.list_trails(name=name)
    geometry = trail.get_geometry()
    return render_template(
        'trail.html',
        title=f'Details of trail {name}',
        user=current_user,
        trail=trail, # TODO: can I pass geometry as part of the trail object???
        raw_coordinates=geometry.coordinates,
        raw_distances=geometry.distances,
        raw_center=geometry.center,
    )


# Edit a trail
@bp.route('/trails/<name>/edit', methods=['GET', 'POST'])
@login_required
def edit_trail(name):
    if not current_user.is_admin:
        flash(f"You are not authorized to perform that action.")
        return redirect(url_for('trails.show_all_trails'))

    tm = TrailManager(session=db.session,actor=current_user)
    trail = tm.list_trails(name=name)
    form = TrailForm()
    if not trail:
        flash(f"Trail {name} does not exist.")
        return redirect(url_for('trails.show_all_trails'))

    geometry = trail.get_geometry()
    if request.method == "POST" and form.validate_on_submit(): # Post edits to the trail
        tm.edit_trail(
            id=trail.id,
            new_name=form.name.data,
            new_dispname=form.dispname.data,
            new_fullname=form.fullname.data
        )
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
    if not current_user.is_admin:
        flash(f"You are not authorized to perform that action.")
        return redirect(url_for('trails.show_all_trails'))

    tm = TrailManager(session=db.session,actor=current_user)
    tm.delete_trail(name=name)
    flash(f"Trail {trail.dispname} has been deleted.")
    return redirect(url_for('main.show_all_trails'))


# Show the trails on which a user has hiked
@bp.route('/trails/user/<username>', methods=['GET'])
def show_user_trails(username):
    tm = TrailManager(session=db.session,actor=current_user)
    us = tm.get_user_statistics(username=username)
    return render_template(
        'trails_user.html',
        title='Trails by user',
        user=us.user,
        trails=us.trails,
        stats=us.stats,
    )