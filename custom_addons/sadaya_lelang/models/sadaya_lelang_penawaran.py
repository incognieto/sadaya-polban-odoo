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
    eval_administrasi = fields.Selection([('lulus', 'Lulus'), ('gugur', 'Gugur')], string='Evaluasi Administrasi', tracking=True)
    skor_teknis = fields.Float(string='Skor Teknis', tracking=True)
    skor_harga = fields.Float(string='Skor Harga', tracking=True)
    eval_harga_wajar = fields.Boolean(string='Harga Wajar / Sesuai HPS', tracking=True)
    eval_kualifikasi = fields.Selection([('lulus', 'Lulus'), ('gugur', 'Gugur')], string='Pembuktian Kualifikasi', tracking=True)

    @api.onchange('eval_administrasi', 'skor_teknis', 'skor_harga', 'eval_kualifikasi')
    def _onchange_evaluasi_status(self):
        for rec in self:
            # Pemenang Lelang tidak diganggu oleh otomasi (karena ditetapkan manual)
            if rec.status == 'winner':
                continue
                
            if rec.eval_administrasi == 'gugur' or rec.eval_kualifikasi == 'gugur':
                rec.status = 'failed'
            elif rec.eval_kualifikasi == 'lulus':
                rec.status = 'passed'
            elif rec.eval_administrasi == 'lulus' or rec.skor_teknis > 0 or rec.skor_harga > 0:
                rec.status = 'evaluated'
            else:
                rec.status = 'submitted'

    def action_set_pemenang(self):
        for rec in self:
            rec.status = 'winner'
            # Set other penawaran in the same paket to failed? Or just leave them
            other_bids = self.search([('paket_id', '=', rec.paket_id.id), ('id', '!=', rec.id)])
            other_bids.write({'status': 'failed'})

    def action_set_gagal(self):
        for rec in self:
            rec.status = 'failed'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('sadaya_lelang.penawaran') or 'New'
        return super(SadayaLelangPenawaran, self).create(vals_list)
