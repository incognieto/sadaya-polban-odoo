# -*- coding: utf-8 -*-
from odoo import models, fields

class TenderDokumen(models.Model):
    _name = 'tender.dokumen'
    _description = 'Dokumen Pemilihan (Upload by Pokja)'

    name = fields.Char(string='Nama Dokumen', required=True)
    paket_id = fields.Many2one('tender.paket', string='Paket Tender', required=True, ondelete='cascade')
    file = fields.Binary(string='File', required=True)
    file_name = fields.Char(string='Nama File')
    description = fields.Text(string='Keterangan')
