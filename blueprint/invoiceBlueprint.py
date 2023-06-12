from flask import Blueprint,request,render_template,redirect,flash,send_file,jsonify,send_from_directory,url_for
from extensions import PdfWriter, PdfReader
from flask_login import login_required
from models.rentalmodel import Mobil,Transaksi
from datetime import timedelta,datetime,date

import os,pdfkit,webbrowser
invoiceBlueprint = Blueprint('invoiceBlueprint',(__name__))


@invoiceBlueprint.route('/invoice/<int:id>')
@login_required
def invoice(id):
    transaksi = Transaksi.query.filter_by(id=id).first()
    m = Mobil.query.filter_by(id=transaksi.id_mobil).first()
    dateNow = date.today()

    invoice_data = {
        'id': transaksi.id,
        'namaPeminjam': transaksi.namaPeminjam,
        'tanggalPinjam': transaksi.tanggalPinjam,
        'tanggalKembali': transaksi.tanggalKembali,
        'totalHarga': transaksi.totalHarga,
        'date': dateNow,
        'nomorPolisi': transaksi.plat,
        'merk': transaksi.merk
    }

    rendered_template = render_template('invoice_template.html', data=invoice_data)

    # Simpan file HTML pada direktori invoices
    html_file_path = f'invoices/invoice_{transaksi.id}.html'
    with open(html_file_path, 'w') as file:
        file.write(rendered_template)

    # Konversi HTML menjadi PDF dan simpan di direktori temporary
    pdf_file_path = f'invoices/invoice_{transaksi.id}.pdf'
    pdfkit.from_file(html_file_path, pdf_file_path)

    # Buka file PDF yang sudah ada
    with open(pdf_file_path, 'rb') as file:
        pdf = PdfReader(file)
        num_pages = len(pdf.pages)

        writer = PdfWriter()

        for page_number in range(num_pages):
            page = pdf.pages[page_number]
            annotations = page['/Annots']

            if annotations:
                for annotation in annotations:
                    annotation.update({
                        '/AA': {'/N': f'this.print({page_number + 1});'}
                    })

            writer.add_page(page)

        # Simpan file PDF yang telah diperbarui
        updated_pdf_file_path = f'invoices/invoice_updated_{transaksi.id}.pdf'
        with open(updated_pdf_file_path, 'wb') as output_file:
            writer.write(output_file)

    # Hapus file HTML dan PDF awal setelah konversi ke PDF selesai
    os.remove(html_file_path)
    os.remove(pdf_file_path)

    return send_from_directory('invoices', f'invoice_updated_{transaksi.id}.pdf')

@invoiceBlueprint.route('/invoice/pdf/<int:id>')
def get_invoice_pdf(id):
    # pdf_file_path = f'invoices/invoice_{id}.pdf'
    return webbrowser.open_new_tab(f'invoices/invoice_{id}.pdf')