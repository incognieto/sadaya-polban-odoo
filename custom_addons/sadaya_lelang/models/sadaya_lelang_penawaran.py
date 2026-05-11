# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SadayaLelangPenawaran(models.Model):
    _name = 'sadaya_lelang.penawaran'
    _description = 'Dokumen Penawaran Vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nomor Penawaran', default='New', readonly=True)
    paket_id = fields.Many2one('sadaya_lelang.paket', string='Paket Tender', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    
    file_kualifikasi = fields.Binary(string='File Kualifikasi')
    file_penawaran = fields.Binary(string='File Harga/Teknis')
    
    harga_penawaran = fields.Monetary(string='Harga Penawaran', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', related='paket_id.currency_id', readonly=True)
    
    status = fields.Selection([
        ('submitted', 'Terkirim'),
        ('evaluated', 'Sedang Dievaluasi'),
        ('passed', 'Lulus Kualifikasi'),
        ('failed', 'Gagal Kualifikasi'),
        ('winner', 'Pemenang Lelang')
    ], string='Status', default='submitted', tracking=True)

    # Field untuk Evaluasi
    skor_teknis = fields.Float(string='Skor Teknis', tracking=True)
    skor_harga = fields.Float(string='Skor Harga', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('sadaya_lelang.penawaran') or 'New'
        return super(SadayaLelangPenawaran, self).create(vals_list)
