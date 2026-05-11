# -*- coding: utf-8 -*-
from odoo import models, fields

class SadayaLelangDokumen(models.Model):
    _name = 'sadaya_lelang.dokumen'
    _description = 'Dokumen Lelang'

    name = fields.Char(string='Nama Dokumen', required=True)
    paket_id = fields.Many2one('sadaya_lelang.paket', string='Paket Tender', ondelete='cascade')
    file_dokumen = fields.Binary(string='File Dokumen', required=True)
    file_name = fields.Char(string='Nama File')
    description = fields.Text(string='Keterangan')
