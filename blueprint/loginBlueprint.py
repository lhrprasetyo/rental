from flask import Blueprint,render_template,request,render_template,redirect,flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, logout_user,login_required
from models.rentalmodel import db,User
import os

loginBlueprint = Blueprint('loginBlueprint',(__name__))

@loginBlueprint.route('/')
def login_menu():
    return render_template('login.html')

# fitur signup
@loginBlueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Ambil data dari form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validasi data
        if password != confirm_password:
            flash('Password tidak cocok')
            return redirect('/signup')
        elif User.query.filter_by(username=username).first():
            flash('Username sudah digunakan')
            return redirect('/signup')
        elif User.query.filter_by(email=email).first():
            flash('Email sudah digunakan')
            return redirect('/signup')
        else:
            # Hash password
            hashed_password = generate_password_hash(password)

            # Simpan data ke database
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash('Akun berhasil dibuat')
            return redirect('/')
    return render_template('signup.html')


# fitur login
@loginBlueprint.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Ambil data dari form
        email = request.form['email']
        password = request.form['password']

        # Cari user di database
        user = User.query.filter_by(email=email).first()

        # Validasi data
        if not user or not check_password_hash(user.password, password):
            flash('Email atau password salah')
            return redirect('/')
        else:
            # Set session user_id
            login_user(user)
            flash('Anda berhasil login')
            return redirect("/list_mobil")
    return render_template('login.html')

# fitur logout 
@loginBlueprint.route('/logout')  
@login_required 
def logout_account():
    logout_user()
    flash('You have been logout.','info')
    return redirect('/')