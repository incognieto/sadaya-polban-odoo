# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SadayaLelangPaket(models.Model):
    _name = 'sadaya_lelang.paket'
    _description = 'Paket Lelang / Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama Paket', required=True, tracking=True)
    kode_tender = fields.Char(string='Kode Tender', readonly=True, copy=False, default='New')
    description = fields.Text(string='Deskripsi Singkat')
    
    hps = fields.Monetary(string='Nilai HPS', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    
    status = fields.Selection([
        ('persiapan_lelang', 'Persiapan Lelang (POKJA)'),
        ('pengumuman_lelang', 'Pengumuman Lelang'),
        ('pendaftaran_penawaran', 'Pendaftaran & Penawaran'),
        ('evaluasi_pembuktian', 'Evaluasi & Pembuktian'),
        ('laporan_hasil', 'Laporan Hasil Lelang'),
        ('sppbj', 'SPPBJ'),
        ('jaminan_pelaksanaan', 'Jaminan Pelaksanaan'),
        ('kontrak', 'Tanda Tangan Kontrak'),
        ('pelaksanaan', 'Pelaksanaan Pekerjaan'),
        ('bast', 'Serah Terima (BAST)'),
        ('selesai', 'Selesai'),
        ('cancelled', 'Dibatalkan')
    ], string='Status', default='persiapan_lelang', tracking=True)

    metode_pemilihan = fields.Selection([
        ('tender', 'Tender'),
        ('seleksi', 'Seleksi')
    ], string='Metode Pemilihan', default='tender', tracking=True)

    # SOP Roles Assignment
    user_id = fields.Many2one('res.users', string='USER / Pemohon')
    manajemen_id = fields.Many2one('res.users', string='MANAJEMEN / Approver')
    ppk_id = fields.Many2one('res.users', string='PPK')
    pokja_id = fields.Many2one('res.users', string='POKJA')
    pphp_id = fields.Many2one('res.users', string='PPHP')

    # SOP Documents Uploads
    file_kebutuhan = fields.Binary(string='Dokumen Kebutuhan')
    file_disposisi = fields.Binary(string='Disposisi Manajemen')
    file_sppbj = fields.Binary(string='Dokumen SPPBJ')
    file_kontrak = fields.Binary(string='Dokumen Kontrak')
    file_jaminan_pelaksanaan = fields.Binary(string='Jaminan Pelaksanaan (Vendor)')
    file_bast = fields.Binary(string='Dokumen BAST')

    jadwal_ids = fields.One2many('sadaya_lelang.jadwal', 'paket_id', string='Jadwal Tender')
    dokumen_ids = fields.One2many('sadaya_lelang.dokumen', 'paket_id', string='Dokumen Pemilihan')
    penawaran_ids = fields.One2many('sadaya_lelang.penawaran', 'paket_id', string='Dokumen Penawaran')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('kode_tender', 'New') == 'New':
                vals['kode_tender'] = self.env['ir.sequence'].next_by_code('sadaya_lelang.paket') or 'New'
        return super(SadayaLelangPaket, self).create(vals_list)
