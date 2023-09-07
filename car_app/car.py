from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from car_app.customer import login_required
from car_app.db import get_db

bp = Blueprint('car', __name__)

# Home page
@bp.route('/')
#@login_required
def index():
    return render_template('home.html')

# Car list
@bp.route('/')
@login_required
def list():
    db = get_db()
    cars = db.execute(
        'SELECT id, name, seat, gearbox, image, model'
        ' FROM car'
        ' ORDER BY name ASC'
    ).fetchall()
    return render_template('car/index.html', cars=cars)

# Guest mode page, Customer can see without logging in if he wish
@bp.route('/guest_mode')
def guest_mode():
    db = get_db()
    cars = db.execute(
        'SELECT id, name, seat, gearbox, image, model, door'
        ' FROM car'
        ' WHERE status = 1'
        ' ORDER BY name ASC'
    ).fetchall()
    return render_template('car/index.html', cars=cars)

# Admin mode page, Admin can see all cars(booked and avalable)
@bp.route('/admin_mode')
@login_required
def admin_mode():
    db = get_db()
    cars = db.execute(
        'SELECT id, name, seat, gearbox, image'
        ' FROM car'
        ' ORDER BY name ASC'
    ).fetchall()
    return render_template('car/all.html', cars=cars)


## Admin can create new car entry ##
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        status = request.form['status']
        seat = request.form['seat']
        door = request.form['door']
        gearbox = request.form['gearbox']
        image = request.form['image']
        error = None

        if not name:
            error = 'Name is required.'
        if not model:
            error = 'Model is required.'
        if not status:
            error = 'Status is required.'
        if not seat:
            error = 'Seat is required.'
        if not door:
            error = 'Door is required.'
        if not gearbox:
            error = 'Gearbox is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO car (name, model, status, seat, door, gearbox, image)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, model, status, seat, door, gearbox, image)
            )
            db.commit()
            return redirect(url_for('car.index'))

    return render_template('car/create.html')

# Getting a car associated with a given id to update it
def get_car(id, check_author=True):
    car = get_db().execute(
        'SELECT id, name, model, status, seat, door, gearbox, image'
        ' FROM car'
        ' WHERE car.id = ?',
        (id,)
    ).fetchone()

    if car is None:
        abort(404, f"Car id {id} doesn't exist.")

    return car

# Admin can update car details
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    car = get_car(id)

    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        status = request.form['status']
        seat = request.form['seat']
        door = request.form['door']
        gearbox = request.form['gearbox']
        image = request.form['image']
        error = None

        if not name:
            error = 'Name is required.'
        if not model:
            error = 'Model is required.'
        if not status:
            error = 'Status is required.'
        if not seat:
            error = 'Seat is required.'
        if not door:
            error = 'Door is required.'
        if not gearbox:
            error = 'Gearbox is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE car SET name = ?, model = ?, status = ?, seat = ?, door = ?, gearbox = ?, image = ?'
                ' WHERE id = ?',
                (name, model, status, seat, door, gearbox, image, id)
            )
            db.commit()
            return redirect(url_for('car.index'))
    return render_template('car/update.html', car=car)

# Deletes the car with a given id
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_car(id)
    db = get_db()
    db.execute('DELETE FROM car WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('car.index'))
