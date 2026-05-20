# -*- coding: utf-8 -*-
from odoo import models, fields

class TenderJadwal(models.Model):
    _name = 'sadaya_lelang.jadwal'
    _description = 'Jadwal Tahapan SadayaLelang'
    _order = 'date_start asc'

    name = fields.Char(string='Nama Tahapan', required=True)
    paket_id = fields.Many2one('sadaya_lelang.paket', string='Paket SadayaLelang', required=True, ondelete='cascade')
    date_start = fields.Datetime(string='Waktu Mulai', required=True)
    date_end = fields.Datetime(string='Waktu Selesai', required=True)
