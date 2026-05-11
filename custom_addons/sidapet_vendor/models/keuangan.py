from odoo import models, fields

class DataKeuangan(models.Model):
    _name = 'sidapet.keuangan'

    penyedia_id = fields.Many2one('sidapet.penyedia', required=True)

    nama_pemilik_rekening = fields.Char()
    nomor_rekening = fields.Char()
    kode_bank = fields.Char()
    nama_bank = fields.Char()

    scan_buku_rekening = fields.Binary()
    scan_laporan_keuangan = fields.Binary()
    masa_berlaku_laporan = fields.Date()

    scan_laporan_audited = fields.Binary()
    masa_berlaku_audited = fields.Date()

    _sql_constraints = [
        ('unique_penyedia_keuangan', 'unique(penyedia_id)',
         'Satu penyedia hanya boleh punya satu data keuangan!')
    ]
