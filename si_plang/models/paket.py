from odoo import models, fields

class SIPlangPaket(models.Model):
    _name = 'si_plang.paket'
    _description = 'Paket Penyedia'
    _order = 'tanggal desc, id desc'

    name = fields.Char(string='Nama Paket', required=True)
    unit_pengusul = fields.Char(string='Unit Pengusul')
    jenis_pengadaan = fields.Selection([
        ('barang', 'Barang'),
        ('jasa_lainnya', 'Jasa Lainnya'),
        ('konstruksi', 'Konstruksi'),
        ('jasa_konsultansi', 'Jasa Konsultansi'),
    ], string='Jenis Pengadaan')
    status_paket = fields.Selection([
        ('proses_penawaran', 'Proses Penawaran Penyedia'),
        ('negosiasi_penyedia', 'Negosiasi (Penyedia)'),
        ('negosiasi_pp', 'Negosiasi (PP)'),
        ('negosiasi_selesai', 'Negosiasi Selesai'),
        ('proses_ba_negosiasi', 'Proses Berita Acara Negosiasi'),
        ('acara_negosiasi', 'Acara Negosiasi'),
        ('persiapan_kontrak', 'Persiapan Kontrak'),
        ('selesai_kontrak', 'Selesai Kontrak'),
        ('proses_kontrak', 'Proses Kontrak'),
        ('revisi', 'Revisi'),
        ('addendum_kontrak', 'Addendum Kontrak'),
        ('batal', 'Batal'),
    ], string='Status Paket')
    tanggal = fields.Date(string='Tanggal')
    tanggal_mulai = fields.Date(string='Tanggal Mulai')
    tanggal_selesai = fields.Date(string='Tanggal Selesai')
    nilai_hps = fields.Float(string='Nilai HPS')
    keterangan = fields.Text(string='Keterangan')

    kontrak_ids = fields.One2many(
    'si_plang.kontrak',
    'paket_id',
    string='Kontrak'
)
