# -*- coding: utf-8 -*-
from odoo import models, fields

class SadayaLelangJadwal(models.Model):
    _name = 'sadaya_lelang.jadwal'
    _description = 'Jadwal Lelang'

    name = fields.Char(string='Nama Tahapan', required=True)
    paket_id = fields.Many2one('sadaya_lelang.paket', string='Paket Tender', ondelete='cascade')
    start_date = fields.Datetime(string='Waktu Mulai', required=True)
    end_date = fields.Datetime(string='Waktu Selesai', required=True)
    perubahan = fields.Integer(string='Perubahan Ke-', default=0)
