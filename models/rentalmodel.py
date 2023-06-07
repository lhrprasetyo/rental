from extensions import db,UserMixin,datetime
# model 

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(1000)) 
    email = db.Column(db.String(100),unique =  True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return f'<{self.username}>'


class Mobil(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merk = db.Column(db.String(100))
    platNomor = db.Column(db.String(20))
    tahun = db.Column(db.String(10))
    gambar = db.Column(db.String(100))
    harga = db.Column(db.Integer)
    denda = db.Column(db.Integer)
    mobil_status = db.Column(db.String(20), default="Tersedia")
    pinjaman = db.relationship('Pinjaman', back_populates='mobil')
    transaksi = db.relationship('Transaksi', back_populates='mobil')
    last_updated = db.Column(db.String(100))

    def __repr__(self) -> str:
        return f'<{self.merk}>'


class Pinjaman(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    namaPeminjam = db.Column(db.String(100))
    merk = db.Column(db.String(100))
    plat = db.Column(db.String(20))
    hari = db.Column(db.Integer)
    id_mobil = db.Column(db.Integer, db.ForeignKey('mobil.id'))
    tanggalPinjam = db.Column(db.Date)
    tanggalKembali = db.Column(db.Date)
    totalHarga = db.Column(db.Integer)
    mobil = db.relationship('Mobil', back_populates='pinjaman')
    transaksi = db.relationship('Transaksi', back_populates='pinjaman')
    last_updated = db.Column(db.String(100))


class Transaksi(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    namaPeminjam = db.Column(db.String(100))
    merk = db.Column(db.String(100))
    plat = db.Column(db.String(20))
    hari = db.Column(db.Integer)
    id_mobil = db.Column(db.Integer, db.ForeignKey('mobil.id', name='fk_transaksi_mobil_id'))
    id_pinjaman = db.Column(db.Integer, db.ForeignKey('pinjaman.id', name='fk_transaksi_pinjaman_id'))
    tanggalPinjam = db.Column(db.Date)
    tanggalKembali = db.Column(db.Date)
    mobil_kembali = db.Column(db.Date)
    status_transaksi = db.Column(db.String(20))
    status_mobil = db.Column(db.String(20)) 
    dibayarkan = db.Column(db.Integer)
    sisa = db.Column(db.Integer)
    totalHarga = db.Column(db.Integer)
    mobil = db.relationship('Mobil', back_populates='transaksi')
    pinjaman = db.relationship('Pinjaman', back_populates='transaksi')
    last_updated = db.Column(db.String(100))