from flask import Blueprint,render_template,request,render_template,redirect
from models.rentalmodel import db,Mobil
from datetime import datetime
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import os



mobilBlueprint = Blueprint('mobilBlueprint',(__name__))


UPLOAD_FOLDER = 'static\img'
ALLOWED_EXTENSIONS={'jpg','jpeg','png','HEIC'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#tambah mobil
@mobilBlueprint.route('/tambah_mobil')
@login_required
def tambah_mobil():
    return render_template('tambah_mobil.html')

# save   mobil
@mobilBlueprint.route('/simpan_mobil', methods =['POST'])
@login_required
def simpan_mobil():
    if request.method == 'POST':
        merk= request.form.get('merk')
        plat= request.form.get('plat')
        tahun= request.form.get('tahun')
        a_harga=request.form.get('harga')
        denda=request.form.get('denda')
        status = 'Tersedia' 
        gambar=request.files['img']

        harga = int(a_harga)
        if gambar and allowed_file(gambar.filename):
            filename= secure_filename(gambar.filename)
            gambar.save(os.path.join(UPLOAD_FOLDER,filename)) 

            f_gambar = os.path.join('static\img',filename)
            dateNow=datetime.now().strftime("%Y-%m-%d")
            m=Mobil(merk =merk,platNomor=plat,tahun=tahun,harga=harga,denda = denda,gambar=f_gambar,mobil_status = status,last_updated = dateNow)
            db.session.add(m)
            db.session.commit()
            return redirect('/list_mobil')

@mobilBlueprint.route('/edit_mobil/<int:id>')
@login_required
def edit_mobil(id):
    mobilList = []
    mobil = Mobil.query.filter_by(id=id).first()
    mobilList.append(mobil)
    return render_template('edit_mobil.html',mobil = mobilList)

@mobilBlueprint.route('/save_mobil',methods = ['POST'])
@login_required
def save_mobil():
    if request.method == 'POST':
        id = request.form.get('id')
        mobil = Mobil.query.filter_by(id=id).first()
        n_nama_mobil = request.form.get("nama")
        n_plat_mobil = request.form.get("plat")
        n_harga_mobil = request.form.get('harga')
        n_denda_mobil = request.form.get('denda')
        n_gambar = request.files['img']

        if n_gambar and allowed_file(n_gambar.filename):
            filename = secure_filename(n_gambar.filename)
            n_gambar.save(os.path.join(UPLOAD_FOLDER,filename))
        dateNow=datetime.now().strftime("%Y-%m-%d")

        f_gambar = os.path.join('static\img',filename)
        mobil.merk = n_nama_mobil
        mobil.platNomor = n_plat_mobil
        mobil.harga = n_harga_mobil
        mobil.denda = n_denda_mobil
        mobil.last_updated = dateNow
        mobil.gambar = f_gambar
        mobil.edited_by = current_user.username


        db.session.add(mobil)
        db.session.commit()
        return redirect('/list_mobil')
    
@mobilBlueprint.route('/delete_mobil/<id>')
@login_required
def delete_mobil(id):
    mobil = Mobil.query.filter_by(id=id).first()
    db.session.delete(mobil)
    db.session.commit()
    return redirect('/list_mobil')

#list mobil
@mobilBlueprint.route('/list_mobil')
@login_required
def listmobil():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Jumlah item per halaman
    # mobil2 = Mobil.query.all()
    # for a in mobil2 :
    #     print(a.gambar)

    mobil = Mobil.query.paginate(page=page, per_page=per_page)
    
    return render_template('list_mobil.html', mobil=mobil)