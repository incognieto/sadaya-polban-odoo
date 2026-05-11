# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_vendor_tender = fields.Boolean(string='Vendor SadayaLelang/SPSE', default=False)
    vendor_status = fields.Selection([
        ('draft', 'Belum Lengkap'),
        ('waiting', 'Menunggu Verifikasi'),
        ('verified', 'Terverifikasi'),
        ('rejected', 'Ditolak')
    ], string='Status Verifikasi Vendor', default='draft', tracking=True)

    nib_number = fields.Char(string='Nomor NIB')
    npwp_number = fields.Char(string='NPWP')
    
    file_nib = fields.Binary(string='Dokumen NIB')
    file_nib_name = fields.Char(string='Nama File NIB')
    
    file_npwp = fields.Binary(string='Dokumen NPWP')
    file_npwp_name = fields.Char(string='Nama File NPWP')
