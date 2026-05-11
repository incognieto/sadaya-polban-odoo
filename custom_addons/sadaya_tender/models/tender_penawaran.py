# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TenderPenawaran(models.Model):
    _name = 'tender.penawaran'
    _description = 'Dokumen Penawaran (Upload by Vendor)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nomor Penawaran', default='New', readonly=True)
    paket_id = fields.Many2one('tender.paket', string='Paket Tender', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Penyedia (Vendor)', required=True, domain=[('vendor_status', '=', 'verified')])
    
    nilai_penawaran = fields.Monetary(string='Harga Penawaran', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(related='paket_id.currency_id', readonly=True)
    
    file_penawaran = fields.Binary(string='File Dokumen Penawaran', required=True)
    file_name = fields.Char(string='Nama File')
    
    status = fields.Selection([
        ('submitted', 'Terkirim'),
        ('evaluated', 'Dievaluasi'),
        ('won', 'Menang'),
        ('lost', 'Kalah')
    ], string='Status', default='submitted', tracking=True)

    # Field untuk Evaluasi
    skor_teknis = fields.Float(string='Skor Teknis', tracking=True)
    skor_harga = fields.Float(string='Skor Harga', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tender.penawaran') or 'New'
        return super(TenderPenawaran, self).create(vals_list)
