from app import app, db
from flask import render_template, redirect, flash, url_for, request, send_file
from app.forms import LoginForm, RegisterForm, Upload
from app.models import User, Image
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from cartoon_gan_master.models.generator import Generator
from cartoon_gan_master.predict import predict_images
import torch
import cv2
import numpy as np
import os
from datetime import date


@app.route('/')
@app.route('/index', methods=["GET", "POST"])
def index():
    form = Upload()
    u = User.query.filter_by(id=current_user.get_id()).first()
    if u:
        today = date.today()
        _date = '01-0' + str(today.month+1) + '-' + str(today.year)
        if form.validate_on_submit():
            file = form.upload.data
            image_bytes = file.read()
            data = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
            image = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
            netG = Generator()
            netG.eval()
            netG.load_state_dict(torch.load("cartoon_gan_master/checkpoints/trained_netG_original.pth", map_location=torch.device('cpu')))
            predicted_image = predict_images(netG, [image], 'cpu')[0]
            if not os.path.exists('app/static/'+ current_user.username + '/'):
                os.mkdir('app/static/'+ current_user.username + '/')
            path = current_user.username + '/' + file.filename
            predicted_image.save('app/static/'+ path)
            img = Image(url=path, author=current_user, status=form.status.data)
            db.session.add(img)
            db.session.commit()
            return redirect(url_for('output', path=path))
        return render_template('index.html', form=form, remaining_credits=u.remaining_credits, date=_date)
    else:
        return render_template('index.html')


@app.route('/output')
@login_required
def output():
    path = request.args.get('path')
    if path == None:
        return redirect(url_for('index'))
    u = User.query.filter_by(id=current_user.get_id()).first()
    u.remaining_credits -= 1
    db.session.commit()
    return render_template('output.html', remaining_credits=u.remaining_credits, path=path)


@app.route('/download')
def download():
    filename = request.args.get('filename')
    return send_file(path_or_file='static/'+filename, as_attachment=True)


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: # current_user found out through the client of the current request
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) # sets current_user.is_authenticated=True
        flash("Logged In Successfully!")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        u = User(username=form.username.data, email=form.email.data, remaining_credits=5)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        flash("Registered Successfully!")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/history')
@login_required
def history():
    public_imgs = Image.query.filter_by(author=current_user, status='Public').order_by(Image.timestamp.desc()).all()
    private_imgs = Image.query.filter_by(author=current_user, status='Private').order_by(Image.timestamp.desc()).all()
    return render_template('history.html', public_imgs=public_imgs, private_imgs=private_imgs)


@app.route('/discover')
def discover():
    if current_user.is_authenticated:
        imgs = Image.query.filter(Image.author!=current_user).filter_by(status='Public').all()
        return render_template('discover.html', imgs=imgs)
    imgs = Image.query.filter_by(status='Public').order_by(Image.timestamp.desc()).all()
    return render_template('discover.html', imgs=imgs)