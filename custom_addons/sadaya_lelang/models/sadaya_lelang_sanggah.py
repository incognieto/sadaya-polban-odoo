# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SadayaLelangSanggah(models.Model):
    _name = 'sadaya_lelang.sanggah'
    _description = 'Masa Sanggah Lelang'
    _order = 'create_date desc'

    paket_id = fields.Many2one('sadaya_lelang.paket', string='Paket Lelang', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    
    pertanyaan = fields.Text(string='Isi Sanggahan', required=True)
    jawaban_pokja = fields.Text(string='Jawaban POKJA')
    
    status_sanggah = fields.Selection([
        ('masuk', 'Sanggahan Masuk'),
        ('dijawab', 'Sudah Dijawab'),
        ('diterima', 'Sanggahan Diterima (Evaluasi Ulang)'),
        ('ditolak', 'Sanggahan Ditolak (Lanjut)')
    ], string='Status', default='masuk')
