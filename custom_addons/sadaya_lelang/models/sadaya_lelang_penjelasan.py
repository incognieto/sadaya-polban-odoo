# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SadayaLelangPenjelasan(models.Model):
    _name = 'sadaya_lelang.penjelasan'
    _description = 'Forum Pemberian Penjelasan (Tanya Jawab)'
    _order = 'create_date asc'

    paket_id = fields.Many2one('sadaya_lelang.paket', string='Paket Lelang', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    
    pertanyaan = fields.Text(string='Isi Pertanyaan', required=True)
    jawaban_pokja = fields.Text(string='Jawaban POKJA')
    
    status_penjelasan = fields.Selection([
        ('masuk', 'Pertanyaan Masuk'),
        ('dijawab', 'Sudah Dijawab')
    ], string='Status', default='masuk')
