from flask import Blueprint,request,render_template,redirect,flash,send_file,jsonify,send_from_directory,url_for
from models.rentalmodel import db,Mobil,Pinjaman,Transaksi
from flask_login import login_required  
from datetime import timedelta,datetime
import os

rentalblueprint = Blueprint('rentalblueprint',(__name__))

# fitur order 1 
@rentalblueprint.route('/start')
@login_required
def input_tanggal():
    return render_template('tanggal.html')

@rentalblueprint.route('/start-check', methods=['POST'])
@login_required
def tanggal_input():
    if request.method == 'POST':
        tanggal = datetime.strptime(request.form['tanggalP'], '%Y-%m-%d').date()
        tanggalk = datetime.strptime(request.form['tanggalK'], '%Y-%m-%d').date()

        mobil = Mobil.query.all()

        for a in mobil:
            a.mobil_status = 'Tersedia'
            db.session.add(a)
        db.session.commit()

        mobil_dipesan = Mobil.query.join(Pinjaman).filter(
            Pinjaman.tanggalPinjam <= tanggalk,
            Pinjaman.tanggalKembali >= tanggal
        ).all()

        mobil_tersedia_ids = [mobil.id for mobil in mobil_dipesan]

        for mobil in mobil_dipesan:
            mobil.mobil_status = 'Sudah dibooking'
            db.session.add(mobil)
        db.session.commit()

        mobil_dipesan2 = Mobil.query.join(Transaksi).filter(
            Transaksi.tanggalPinjam <= tanggalk,
            Transaksi.tanggalKembali >= tanggal,
            Transaksi.status_transaksi != 'Selesai',
            ~Mobil.id.in_(mobil_tersedia_ids)
        ).all()

        for mobil in mobil_dipesan2:
            mobil.mobil_status = 'Sudah dibooking'
            db.session.add(mobil)
        db.session.commit()

        mobil_tersedia = Mobil.query.filter(
            Mobil.mobil_status != 'Sudah dibooking'
        ).order_by(Mobil.mobil_status.desc(), Mobil.id.desc()).all()

        for mobil in mobil_tersedia:
            mobil.mobil_status = 'Tersedia'
            db.session.add(mobil)
        db.session.commit()

        semua_mobil = mobil_tersedia + mobil_dipesan + mobil_dipesan2
        semua_mobil.sort(key=lambda mobil: mobil.mobil_status, reverse=True)

        return render_template('list_mobil_available.html', semua_mobil=semua_mobil, tanggal=tanggal, tanggalk=tanggalk)


#fitur order 2
@rentalblueprint.route('/booking/<int:id>')
@login_required
def add_booking(id):
    mobil = Mobil.query.get(id)
    booking = Pinjaman.query.filter_by(id_mobil=id).all()
    tr = Transaksi.query.filter_by(id_mobil=id).all()

    booked_dates = []
    for a in booking :
        selisih = (a.tanggalKembali - a.tanggalPinjam).days 
        selisih += 1
        for i in range(selisih):
            for t in booking:
                tanggal = t.tanggalPinjam + timedelta(days=i)
                booked_dates.append(tanggal.strftime('%Y-%m-%d'))

    for i in tr:
        if i.status_mobil != 'Selesai':
            selisih = (i.tanggalKembali - i.tanggalPinjam).days
            selisih += 1
            for j in range(selisih):
                tanggal = i.tanggalPinjam + timedelta(days=j)
                booked_dates.append(tanggal.strftime('%Y-%m-%d'))

    return render_template('tambah_pesanan2.html', mobil = mobil, booked_dates=booked_dates,id = mobil.id)

#filter tanggal
@rentalblueprint.route('/get_booking_list', methods=['POST'])
@login_required
def get_booking_list():
    mobil_id = request.form.get('mobil_id')

    mobil = Mobil.query.filter_by(id = mobil_id).first()
    booking_list = Pinjaman.query.filter_by(id_mobil=mobil_id).all()

    results = []
    for booking in booking_list:
        result = {
            'nama' : booking.namaPeminjam,
            'tanggalPinjam' : booking.tanggalPinjam,
            'tanggalKembali': booking.tanggalKembali,
            'merk' : booking.merk,
            'plat' : mobil.platNomor
        }
        results.append(result)

    return jsonify({'booking_list': results})


#save pesanan
@rentalblueprint.route('/save/pesanan/<int:id>', methods = ['POST'])
@login_required
def simpan_booking(id):
    mobil = Mobil.query.filter_by(id =id).first()
    f_nama = request.form.get('namaPeminjam')
    f_merk = mobil.merk
    f_plat = mobil.platNomor
    f_tanggalP = datetime.strptime(request.form.get('tanggalP'),'%Y-%m-%d')
    f_tanggalK = datetime.strptime(request.form.get('tanggalK'),'%Y-%m-%d')
    f_dibayarkan = int(request.form.get('dibayarkan'))
    harga = mobil.harga
    hari = (f_tanggalK - f_tanggalP).days +1
    total_harga = harga * hari
    f_sisa = total_harga - f_dibayarkan
    dateNow=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    book = Pinjaman(namaPeminjam = f_nama,merk=f_merk,plat=f_plat,tanggalPinjam = f_tanggalP,tanggalKembali=f_tanggalK,totalHarga = total_harga,hari = hari,id_mobil = id,last_updated = dateNow)
    db.session.add(book)
    db.session.commit()
    id_pinjaman_baru = book.id
    statusMobil = "Dibooking" 
    statusTransaksi = "lunas" if f_sisa == 0 else "Belum lunas"
    dateNow=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts = Transaksi(namaPeminjam = f_nama,merk=f_merk,plat=f_plat,tanggalPinjam = f_tanggalP,tanggalKembali=f_tanggalK,totalHarga = total_harga,hari = hari,id_mobil = id, dibayarkan = f_dibayarkan,sisa = f_sisa, id_pinjaman = id_pinjaman_baru,status_transaksi = statusTransaksi,status_mobil=statusMobil,last_updated = dateNow)
    db.session.add(ts)
    db.session.commit()
    return redirect('/list_pesanan')


@rentalblueprint.route('/list_pesanan')
@login_required
def list_pesanan():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    pinjaman = Pinjaman.query.paginate(page= page, per_page=per_page)
    return render_template('list_pesanan.html', pesanan=pinjaman)

@rentalblueprint.route('/pinjam/<int:id>', methods = ['POST'])
@login_required
def tambah_pesanan(id):
    if request.method == 'POST':
        mobil = Mobil.query.filter_by(id=id).first()
        tanggal = request.form.get('tanggal')
        tanggalk = request.form.get('tanggalk')
        return render_template('tambah_pesanan2.html',tanggal=tanggal,id = id,mobil = mobil,tanggalk=tanggalk)

# route revisi
@rentalblueprint.route('/save/<int:id>',methods=['POST'])
@login_required
def simpan_pesanan(id):
    if request.method == 'POST':
        nama = request.form.get('nama')
        hari = request.form.get('hari')
        platN = request.form.get('plat')
        tglP = datetime.strptime(request.form['tanggal_pinjam'], '%Y-%m-%d').date()
        tglK = tglP + timedelta(days=int(hari))
        mobil = request.form.get('mobil')
        harga = request.form.get('harga')
        if int(hari) == 0:
            total = int(harga) * 1
        else:
            total = int(hari) * int(harga)
        dateNow=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p=Pinjaman(namaPeminjam=nama,hari = hari,id_mobil=id,plat = platN ,tanggalPinjam = tglP,tanggalKembali=tglK,merk = mobil,totalHarga=total,last_updated = dateNow)
        db.session.add(p)
        db.session.commit()
        return redirect('/list_pesanan')
            

@rentalblueprint.route('/edit_pesanan/<int:id>', methods = ['POST'])
@login_required
def edit_pesanan(id):
    pesanan = Pinjaman.query.filter_by(id=id)
    return render_template('edit_pesanan.html',pesanan = pesanan)

@rentalblueprint.route('/pesanan/<int:id>/save',methods = ['POST'])
@login_required
def save_edit_pesanan(id):
    if request.method == 'POST':
        nama = request.form.get('nama_peminjam')
        hari = request.form.get('jumlah_hari')
        p=Pinjaman(namaPeminjam=nama,hari = hari,id_mobil=id)
        dateNow=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p.last_updated = dateNow
        db.session.add(p)
        db.session.commit()
        return redirect('/list_mobil')
    

@rentalblueprint.route('/ongoing/<int:id>')
@login_required
def change_status_tr(id):
    tr = Transaksi.query.filter_by(id_pinjaman = id).first()
    tr.status_mobil = "Mobil dipinjam"
    dateNow=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tr.last_updated = dateNow

    db.session.add(tr) 
    db.session.commit()
    return render_template('ongoing.html',tr = tr,id = tr.id_pinjaman)

@rentalblueprint.route('/ongoing/<int:id>/pay', methods =['POST'])
@login_required
def add_payment(id):
    tr = Transaksi.query.filter_by(id_pinjaman=id).first()
    pj = Pinjaman.query.filter_by(id=id).first()
    add_payment = request.form.get('tambahan')
    add_payment = int(add_payment) 
    if tr.sisa != 0:
        new_sisa = int(tr.sisa) - add_payment 
        tr.sisa = new_sisa
        new_dibayarkan = add_payment + int(tr.dibayarkan)
        tr.dibayarkan = new_dibayarkan
        if tr.sisa == 0:
            print(tr.status_transaksi)
            tr.status_transaksi = 'lunas'    
    else:
        print(tr.status_transaksi)
        tr.status_transaksi = 'lunas'

    dateNow= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tr.last_updated = dateNow
    
    db.session.add(tr)
    db.session.commit()
    db.session.delete(pj)
    db.session.commit()
    return redirect('/transaksi/1')


@rentalblueprint.route('/delete/<int:id>')
@login_required
def delete_pesanan(id):
    pesanan = Pinjaman.query.filter_by(id=id).all()
    for o in pesanan:
        db.session.delete(o)
    db.session.commit()
    return redirect('/list_pesanan')