from odoo import models, fields

class SIPlangKontrak(models.Model):
    _name = 'si_plang.kontrak'
    _description = 'Kontrak'
    _order = 'tanggal desc, id desc'

    name = fields.Char(string='Nama Paket', required=True)
    pejabat_pembuat = fields.Char(string='Pejabat Pembuat')
    penyedia = fields.Char(string='Penyedia')
    jenis_pengadaan = fields.Selection([
        ('barang', 'Barang'),
        ('jasa_lainnya', 'Jasa Lainnya'),
        ('konstruksi', 'Konstruksi'),
        ('jasa_konsultansi', 'Jasa Konsultansi'),
    ], string='Jenis Pengadaan')
    status_kontrak = fields.Selection([
        ('persiapan_kontrak', 'Persiapan Kontrak'),
        ('proses_kontrak', 'Proses Kontrak'),
        ('selesai_kontrak', 'Selesai Kontrak'),
        ('revisi', 'Revisi'),
        ('addendum_kontrak', 'Addendum Kontrak'),
    ], string='Status Kontrak')
    nilai_hps = fields.Float(string='Nilai HPS')
    tanggal = fields.Date(string='Tanggal')
    tanggal_mulai = fields.Date(string='Tanggal Mulai')
    tanggal_selesai = fields.Date(string='Tanggal Selesai')
    paket_id = fields.Many2one('si_plang.paket', string='Paket')
    keterangan = fields.Text(string='Keterangan')
