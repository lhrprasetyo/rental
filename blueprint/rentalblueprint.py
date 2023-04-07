from flask import Blueprint,render_template,request,render_template,redirect,Flask,flash,session
from models.rentalmodel import db,Mobil,Pinjaman,Transaksi,User
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,login_required,login_user
from extensions import and_
import os
from datetime import timedelta,datetime,date


UPLOAD_FOLDER = 'static\img'
app = Flask(__name__)
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER


ALLOWED_EXTENSIONS={'jpg','jpeg','png','HEIC'}

rentalblueprint = Blueprint('rentalblueprint',(__name__))
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@rentalblueprint.route('/')
def login_menu():
    return render_template('login.html')

@rentalblueprint.route('/signup', methods=['GET', 'POST'])
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

@rentalblueprint.route('/login', methods=['POST'])
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
            session['user_id'] = user.id
            flash('Anda berhasil login')
            return redirect("/list_mobil")
    return render_template('login.html')

@rentalblueprint.route('/logout')   
def logout_account():
    session.clear()
    flash('You have been logout.','info')
    return redirect('/')

@rentalblueprint.route('/start')
def input_tanggal():
    return render_template('tanggal.html')

@rentalblueprint.route('/start-check',methods = ['POST'])
def tanggal_input():
    if request.method == 'POST':
        tanggal = datetime.strptime(request.form['tanggalP'], '%Y-%m-%d').date()
        hari = request.form.get('hari')
        tanggalk = tanggal + timedelta(days=int(hari))

        pinjaman = db.session.query(Pinjaman.id_mobil).filter(
        (Pinjaman.tanggalPinjam <= tanggal) & (Pinjaman.tanggalKembali >= tanggal) |
        (Pinjaman.tanggalPinjam <= tanggalk) & (Pinjaman.tanggalKembali >= tanggalk) |
        (Pinjaman.tanggalPinjam >= tanggal) & (Pinjaman.tanggalKembali <= tanggalk)
        )
        mobil_tersedia = Mobil.query.filter(~Mobil.id.in_(pinjaman), Mobil.mobil_status == 'Available').all()
        return render_template('list_mobil_available.html',hari=hari,mobil_tersedia =mobil_tersedia,tanggal=tanggal)

@rentalblueprint.route('/list_mobil')
def listmobil():
    listmobil= Mobil.query.all()
    return render_template('list_mobil.html',mobil= listmobil)

@rentalblueprint.route('/tambah_mobil')
def tambah_mobil():
    return render_template('tambah_mobil.html')

@rentalblueprint.route('/simpan_mobil', methods =['POST'])
def simpan_mobil():
    if request.method == 'POST':
        merk= request.form.get('merk')
        plat= request.form.get('plat')
        tahun= request.form.get('tahun')
        a_harga=request.form.get('harga')
        denda=request.form.get('denda')
        status = 'Available' if 'Available' in request.form else 'Not Available'
        gambar=request.files['img']

        harga = int(a_harga)
        if gambar and allowed_file(gambar.filename):
            filename= secure_filename(gambar.filename)
            gambar.save(os.path.join(app.config['UPLOAD_FOLDER'],filename)) 

            f_gambar = os.path.join('static\img',filename)
            m=Mobil(merk =merk,platNomor=plat,tahun=tahun,harga=harga,denda = denda,gambar=f_gambar,mobil_status = status)
            db.session.add(m)
            db.session.commit()
            return redirect('/list_mobil')
@rentalblueprint.route('/edit_mobil/<int:id>')
def edit_mobil(id):
    mobil = Mobil.query.filter_by(id=id).first()
    return render_template('edit_mobil.html',mobil = mobil)

@rentalblueprint.route('/save_mobil',methods = ['POST'])
def save_mobil():
    if request.method == 'POST':
        id = request.form.get('id')
        mobil = Mobil.query.filter_by(id=id).first()
        n_nama_mobil = request.form.get("nama")
        n_plat_mobil = request.form.get("plat")
        mobil.merk = n_nama_mobil
        mobil.platNomor = n_plat_mobil
        db.session.add(mobil)
        db.session.commit()
        return redirect('list_mobil')



@rentalblueprint.route('/delete_mobil/<id>')
def delete_mobil(id):
    mobil = Mobil.query.filter_by(id=id).first()
    db.session.delete(mobil)
    db.session.commit()
    return redirect('/list_mobil')

@rentalblueprint.route('/list_pesanan')
def list_pesanan():
    pinjaman = Pinjaman.query.all()
    return render_template('list_pesanan.html',pesanan = pinjaman)

@rentalblueprint.route('/pinjam/<int:id>', methods = ['POST'])
def tambah_pesanan(id):
    if request.method == 'POST':
        mobil = Mobil.query.filter_by(id=id).first()
        tanggal = request.form.get('tanggal')
        hari = request.form.get('hari')
        return render_template('tambah_pesanan.html',hari=hari,tanggal=tanggal,id = id,mobil = mobil)

@rentalblueprint.route('/pesanan_mobil/<id>')
def list_pesanan_mobil(id):  
    pesanan = Pinjaman.query.filter_by(id_mobil = id).all()
    return render_template('pesanan_mobil.html', ps = pesanan)

@rentalblueprint.route('/save/<int:id>',methods=['POST'])
def simpan_pesanan(id):
    if request.method == 'POST':
        nama = request.form.get('nama')
        hari = request.form.get('hari')
        tglP = datetime.strptime(request.form['tanggal_pinjam'], '%Y-%m-%d').date()
        tglK = tglP + timedelta(days=int(hari))
        mobil = request.form.get('mobil')
        harga = request.form.get('harga')
        if int(hari) == 0:
            total = int(harga) * 1
        else:
            total = int(hari) * int(harga)
        p=Pinjaman(namaPeminjam=nama,hari = hari,id_mobil=id,tanggalPinjam = tglP,tanggalKembali=tglK,merk = mobil,totalHarga=total)
        db.session.add(p)
        db.session.commit()
        return redirect('/list_pesanan')
            

@rentalblueprint.route('/edit_pesanan/<id>', methods = ['POST'])
def edit_pesanan(id):
    pesanan = Pinjaman.query.filter_by(id=id)
    return render_template('edit_pesanan.html',pesanan = pesanan)

@rentalblueprint.route('/pesanan/<id>/save',methods = ['POST'])
def save_edit_pesanan(id):
    if request.method == 'POST':
        nama = request.form.get('nama_peminjam')
        hari = request.form.get('jumlah_hari')
        p=Pinjaman(namaPeminjam=nama,hari = hari,id_mobil=id)
        db.session.add(p)
        db.session.commit()
        return redirect('/list_mobil')

@rentalblueprint.route('/delete/<int:id>')
def delete_pesanan(id):
    pesanan = Pinjaman.query.filter_by(id=id).all()
    for o in pesanan:
        db.session.delete(o)
    db.session.commit()
    return redirect('/list_pesanan')

@rentalblueprint.route('/transaksi/<int:id>')
def data_transaksi(id):
    id = id
    pinjaman = Pinjaman.query.filter_by(id=id).first()
    return render_template('form_transaksi.html',id = id,pinjaman=pinjaman)

@rentalblueprint.route('/save/transaksi/', methods = ['POST'])

def save_transaksi():
    if request.method == 'POST':
        id_pinjaman = request.form.get('id')
        tanggal_kembali_a = datetime.strptime(request.form['tanggal_kembali_aktual'], '%Y-%m-%d').date()
        data = Pinjaman.query.filter_by(id =id_pinjaman).first()
        mobil = Mobil.query.filter_by(id = data.id_mobil).first()
        selisih = (tanggal_kembali_a - data.tanggalKembali).days 
        total_denda = int(max(selisih,0) *mobil.denda) 
        total_harga = total_denda + data.totalHarga
        
        tr = Transaksi(namaPeminjam =data.namaPeminjam,merk=data.merk,hari = data.hari,id_mobil = data.id_mobil,tanggalPinjam = data.tanggalPinjam,tanggalKembali = data.tanggalKembali,mobil_kembali = tanggal_kembali_a,totalHarga =total_harga)
        db.session.add(tr)
        db.session.delete(data)
        db.session.commit()
        return redirect('/transaksi')
    

@rentalblueprint.route('/transaksi')
def list_transaksi():
    tr = Transaksi.query.all()
    return render_template('list_transaksi.html',transaksi = tr)