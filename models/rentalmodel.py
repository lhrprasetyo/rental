from extensions import db,UserMixin
# model 

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(1000)) 
    email = db.Column(db.String(100),unique =  True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return f'<{self.username}>'


class Mobil(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    merk = db.Column(db.String(100))
    platNomor = db.Column(db.String(20))
    tahun = db.Column(db.String(10))
    gambar = db.Column(db.String(100))
    harga = db.Column(db.Integer)
    denda = db.Column(db.Integer)
    mobil_status = db.Column(db.String(20), default = "Available")
    

    def __repr__(self) -> str:
        return f'<{self.merk}>'


class Pinjaman(db.Model):
    id = db.Column(db.Integer,primary_key = True , autoincrement = True)
    namaPeminjam = db.Column(db.String(100))
    merk = db.Column(db.String(100))
    hari = db.Column(db.Integer)
    id_mobil= db.Column(db.Integer,db.ForeignKey('mobil.id'))
    tanggalPinjam = db.Column(db.Date)
    tanggalKembali = db.Column(db.Date)
    totalHarga = db.Column(db.Integer)
    mobil = db.relationship('Mobil',backref='pinjaman')

class Transaksi(db.Model):
    id = db.Column(db.Integer,primary_key = True , autoincrement = True)
    namaPeminjam = db.Column(db.String(100))
    merk = db.Column(db.String(100))
    hari = db.Column(db.Integer)
    id_mobil= db.Column(db.Integer,db.ForeignKey('mobil.id'))
    tanggalPinjam = db.Column(db.Date)
    tanggalKembali = db.Column(db.Date)
    mobil_kembali = db.Column(db.Date)
    totalHarga = db.Column(db.Integer)
    mobil = db.relationship('Mobil',backref='transaksi')