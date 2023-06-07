from flask import Blueprint,render_template,request,render_template,redirect,flash
from flask_login import login_required
from models.rentalmodel import db,Mobil,Pinjaman,Transaksi
from datetime import timedelta,datetime,date
from extensions import and_
import os


transaksiBlueprint = Blueprint('transaksiBlueprint',(__name__))


# list transaksi 
ROWS_PER_PAGE = 5
@transaksiBlueprint.route('/transaksi/<int:page>', methods=['GET', 'POST'])
@login_required
def list_transaksi(page):
    tr = Transaksi.query.all()
    for a in tr:
        if a.sisa != 0 and not a.status_transaksi.endswith('Belum lunas'):
            a.status_transaksi += 'Belum lunas'
            db.session.add(a)
            db.session.commit()

    status_mobil = request.args.get('status_mobil')
    status_transaksi = request.args.get('status_transaksi')
    filter_date = request.args.get('filter_date')

    transaksi_query = Transaksi.query

    if status_mobil:
        transaksi_query = transaksi_query.filter(Transaksi.status_mobil == status_mobil)
    
    if status_transaksi:
        transaksi_query = transaksi_query.filter_by(status_transaksi=status_transaksi)

    if filter_date:
        filter_date = datetime.strptime(filter_date, '%Y-%m-%d')
        transaksi_query = transaksi_query.filter(and_(Transaksi.tanggalPinjam <= filter_date, Transaksi.tanggalKembali >= filter_date))

    transaksi_paginated = transaksi_query.paginate(page=page, per_page=ROWS_PER_PAGE)

    return render_template('list_transaksi.html', transaksi=transaksi_paginated, page=page)


# simpan transaksi 
@transaksiBlueprint.route('/save/transaksi/', methods = ['POST'])
@login_required
def save_transaksi():
    if request.method == 'POST':
        id_transaksi = request.form.get('id')
        tanggal_kembali_a = datetime.strptime(request.form['tanggal_kembali_aktual'], '%Y-%m-%d').date()
        add_payment= request.form.get('add_payment')
        data = Transaksi.query.filter_by(id =id_transaksi).first()
        mobil = Mobil.query.filter_by(id = data.id_mobil).first()
        mobil.mobil_status = 'Tersedia'
        selisih = (tanggal_kembali_a - data.tanggalKembali).days 
        total_denda = int(max(selisih,0) *mobil.denda) 
        totalSisa = total_denda + data.sisa - int(add_payment)

        data.totalHarga += total_denda
        data.sisa = totalSisa
        data.dibayarkan = data.dibayarkan + int(add_payment)
        data.mobil_kembali = tanggal_kembali_a
        data.status_mobil = 'Selesai'
        if data.sisa == 0 :
            data.status_transaksi = 'lunas'
        else:
            data.status_transaksi = 'Belum lunas'

        dateNow=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.last_updated = dateNow

        db.session.add(data)
        db.session.add(mobil)
        db.session.commit()
        return redirect('/transaksi/1')

# fitur delete transaksi 
# @transaksiBlueprint.route('/delete/transaksi/1')
# def del_transaksi():
#     transaksi_to_delete = Transaksi.query.filter_by(id=1).first()  # Mengambil entitas Transaksi dengan ID 4
#     db.session.delete(transaksi_to_delete)
#     db.session.commit()
#     # for a in transaksi_to_delete:
#     #     db.session.delete(a)
#     #     db.session.commit()
#     return redirect('/transaksi/1')

# mengembalikan mobil 
@transaksiBlueprint.route('/transaksi/kembali/<int:id>')
@login_required
def data_transaksi(id):
    data = Transaksi.query.filter_by(id = id).first()
    data2 = Mobil.query.filter_by(id=data.id_mobil).first()
    return render_template('form_transaksi.html',id = id,transaksi=data,mobil = data2)

# cancel booking 
@transaksiBlueprint.route('/transaksi/cancel/<int:id>')
@login_required
def cancel_booking(id):
    tr = Transaksi.query.filter_by(id=id).first()
    tr.status_mobil = 'Dibatalkan'
    tr.status_transaksi = 'Transaksi dibatalkan'


    db.session.add(tr)
    db.session.commit()

    return redirect('/transaksi/1')