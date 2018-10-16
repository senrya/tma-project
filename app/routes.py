'''from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import logout_user
from flask_login import current_user, login_user
from app.models import User
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from datetime import datetime
from app.forms import EditProfileForm
from app.forms import PostForm
from app.models import Post
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm'''
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, SayForm
from app.models import User, Post, Say
from app.email import send_password_reset_email
import matplotlib.pyplot as plt
import io
import base64
import random
from io import StringIO
import matplotlib.pyplot as plt
from math import erfc, sqrt, exp, log2, pi, sin
import numpy as np
import urllib

from flask import Flask, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])

def index():

    return render_template('index.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    says = user.says.order_by(Say.timestamp.desc()).paginate(
        page, app.config['SAYS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=says.next_num) \
        if says.has_next else None
    prev_url = url_for('user', username=user.username, page=says.prev_num) \
        if says.has_prev else None
    return render_template('user.html', user=user, says=says.items,
                           next_url=next_url, prev_url=prev_url)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    form = SayForm()
    if form.validate_on_submit():
        say = Say(body=form.say.data, author=current_user)
        db.session.add(say)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('explore'))
    '''posts = current_user.followed_posts().all()
    return render_template("index.html", title='Home Page', form=form,
                           posts=posts)'''
    page = request.args.get('page', 1, type=int)
    says = current_user.followed_says().paginate(
        page, app.config['SAYS_PER_PAGE'], False)
    next_url = url_for('explore', page=says.next_num) \
        if says.has_next else None
    prev_url = url_for('explore', page=says.prev_num) \
        if says.has_prev else None
    return render_template('explore.html', title='Explore', form=form,
                           says=says.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/bpsk')
def bpsk():
    img = io.BytesIO()
    EbN0_dB = []
    loi = []
    i = 0
    while i <= 24:
        EbN0_dB.append(i)
        i += 1
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        BER = 1/2*erfc(sqrt(EbN0))
        loi.append(BER)

    plt.semilogy(EbN0_dB, loi, 'c-s', label = "BPSK")
    plt.legend()
    plt.grid(True)
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')
    plt.title('Bit Error Rate for Binary Phase-Shift Keying')
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('plot.html', plot_url=plot_url)

@app.route('/dpsk')
@login_required
def dpsk():
    imga = io.BytesIO()
    EbN0_dB = []
    loi = []
    i = 0
    while i <= 24:
        EbN0_dB.append(i)
        i += 1
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        BER = 1/2*exp(-EbN0)
        loi.append(BER)

    plt.semilogy(EbN0_dB, loi,'m-s', label = "DPSK")
    plt.legend()

    plt.grid(True)
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')
    plt.title('Bit Error Rate for Differential Phase Shift Keying')
    plt.savefig(imga, format='png')
    imga.seek(0)
        
    plot_urla = base64.b64encode(imga.getvalue()).decode()

    return render_template('plot.html', plot_url=plot_urla)
@app.route('/qam')
def qam():
    form = PostForm()

    if form.validate_on_submit():
        EbN0 = 10**(form.post.data/10)
        BER = 1/2*exp(-EbN0)
        post = Post(body=round(BER,5), author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('dpsk'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('dpsk', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('dpsk', page=posts.prev_num) \
        if posts.has_prev else None

    imgb = io.BytesIO()
    EbN0_dB = []
    loi_4 = []
    loi_16 = []
    loi_64 = []
    i = 0
    while i <= 24:
        EbN0_dB.append(i)
        i += 1
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        k = log2(4)
        BER = 2/k*(1-1/sqrt(4))*erfc(sqrt(3*EbN0*k/(2*(4-1))))
        loi_4.append(BER)
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        k = log2(16)
        BER = 2/k*(1-1/sqrt(4))*erfc(sqrt(3*EbN0*k/(2*(16-1))))
        loi_16.append(BER)
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        k = log2(64)
        BER = 2/k*(1-1/sqrt(4))*erfc(sqrt(3*EbN0*k/(2*(64-1))))
        loi_64.append(BER)

    plt.semilogy(EbN0_dB, loi_4, 'k-*', label = "4-QAM")
    plt.semilogy(EbN0_dB, loi_16, 'g-o', label = "16-QAM")
    plt.semilogy(EbN0_dB, loi_64, 'r-h', label = "64-QAM")
    plt.ylim([10**-10,10])
    plt.xlim([0,21])
    plt.legend()
    plt.grid(True)
    plt.ylabel('BER')
    plt.xlabel('E_b/N_0 (dB)')
    plt.title('Bit Error Rate for Quadrature amplitude modulation')
    plt.savefig(imgb, format='png')
    imgb.seek(0)

    plot_urlb = base64.b64encode(imgb.getvalue()).decode()

    return render_template('plot.html', plot_url=plot_urlb)

@app.route('/psk8')
def psk8():   
    imgc = io.BytesIO()
    EbN0_dB = []
    loi = []
    i = 0
    while i <= 24:
        EbN0_dB.append(i)
        i += 1
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        k=log2(8)
        BER = 1/k*erfc(sqrt(EbN0*k)*sin(pi/8))
        loi.append(BER)

    plt.semilogy(EbN0_dB, loi, "k-p", label = "8-PSK")
    plt.legend()

    plt.grid(True)
    plt.ylabel('BER')
    plt.xlabel('E_b/N_0 (dB)')
    plt.title('Bit Error Rate for Quadature Phase Shift Keying')
    plt.savefig(imgc, format='png')
    imgc.seek(0)
        
    plot_urlc = base64.b64encode(imgc.getvalue()).decode()

    return render_template('plot.html', plot_url=plot_urlc)

@app.route('/pskb16')
def psk16():   
    imgd = io.BytesIO()
    EbN0_dB = []
    loi = []
    i = 0
    while i <= 24:
        EbN0_dB.append(i)
        i += 1
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        k=log2(16)
        BER = 1/k*erfc(sqrt(EbN0*k)*sin(pi/16))
        loi.append(BER)

    plt.semilogy(EbN0_dB, loi, "b:s", label = "16-PSK")
    plt.legend()

    plt.grid(True)
    plt.ylabel('BER')
    plt.xlabel('E_b/N_0 (dB)')
    plt.title('Bit Error Rate for Quadature Phase Shift Keying')
    plt.savefig(imgd, format='png')
    imgd.seek(0)
        
    plot_urld = base64.b64encode(imgd.getvalue()).decode()

    return render_template('plot.html', plot_url=plot_urld)
@app.route('/psk32')
def psk32():   
    imge = io.BytesIO()
    EbN0_dB = []
    loi = []
    i = 0
    while i <= 24:
        EbN0_dB.append(i)
        i += 1
    for item in EbN0_dB:
        EbN0 = 10**(item/10)
        k=log2(32)
        BER = 1/k*erfc(sqrt(EbN0*k)*sin(pi/32))
        loi.append(BER)

    plt.semilogy(EbN0_dB, loi, "m:d", label = "32-PSK")
    plt.legend()

    plt.grid(True)
    plt.ylabel('BER')
    plt.xlabel('E_b/N_0 (dB)')
    plt.title('Bit Error Rate for Quadature Phase Shift Keying')
    plt.savefig(imge, format='png')
    imge.seek(0)
        
    plot_urld = base64.b64encode(imge.getvalue()).decode()

    return render_template('plot.html', plot_url=plot_urld)

