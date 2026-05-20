# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TenderPaket(models.Model):
    _name = 'sadaya_lelang.paket'
    _description = 'Paket Pengadaan/SadayaLelang'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama Paket', required=True, tracking=True)
    kode_tender = fields.Char(string='Kode SadayaLelang', readonly=True, copy=False, default='New')
    description = fields.Text(string='Deskripsi Singkat')
    
    hps = fields.Monetary(string='Nilai HPS (Harga Perkiraan Sendiri)', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('announced', 'Pengumuman'),
        ('registration', 'Pendaftaran'),
        ('upload', 'Upload Dokumen'),
        ('evaluation', 'Evaluasi'),
        ('awarded', 'Selesai/Diumumkan'),
        ('cancelled', 'Dibatalkan')
    ], string='Status', default='draft', tracking=True)

    metode_pemilihan = fields.Selection([
        ('sadaya_lelang', 'SadayaLelang'),
        ('seleksi', 'Seleksi'),
        ('pengadaan_langsung', 'Sadaya Langsung'),
        ('penunjukan_langsung', 'Penunjukan Langsung')
    ], string='Metode Pemilihan', default='sadaya_lelang', tracking=True)

    jadwal_ids = fields.One2many('sadaya_lelang.jadwal', 'paket_id', string='Jadwal SadayaLelang')
    dokumen_ids = fields.One2many('sadaya_lelang.dokumen', 'paket_id', string='Dokumen Pemilihan')
    penawaran_ids = fields.One2many('sadaya_lelang.penawaran', 'paket_id', string='Dokumen Penawaran')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('kode_tender', 'New') == 'New':
                vals['kode_tender'] = self.env['ir.sequence'].next_by_code('sadaya_lelang.paket') or 'New'
        return super(TenderPaket, self).create(vals_list)
