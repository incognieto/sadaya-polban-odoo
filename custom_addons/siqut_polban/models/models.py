from odoo import models, fields, api

class SiqutPaket(models.Model):
    _name = 'siqut.paket'
    _description = 'Paket Rencana Umum Pengadaan (RUP)'

    name = fields.Char(string='Nama Paket', required=True)
    nilai_hps = fields.Float(string='Nilai HPS (Rp)', required=True)
    jenis_kontrak = fields.Selection([
        ('lumsum', 'Lumsum'),
        ('harga_satuan', 'Harga Satuan')
    ], string='Jenis Kontrak', default='lumsum')
    
    # Status alur paket pengadaan
    state = fields.Selection([
        ('draft', 'Draft RUP'),
        ('published', 'Pengumuman / Masa Penawaran'),
        ('eval', 'Evaluasi / Routing')
    ], string='Status', default='draft')

class SiqutPenawaran(models.Model):
    _name = 'siqut.penawaran'
    _description = 'Dokumen Penawaran Vendor'

    # Relasi: 1 Paket bisa punya banyak Penawaran dari berbagai vendor
    paket_id = fields.Many2one('siqut.paket', string='Paket Pengadaan', required=True)
    vendor_name = fields.Char(string='Nama Vendor', required=True)
    harga_penawaran = fields.Float(string='Harga Penawaran Final (Rp)', required=True)