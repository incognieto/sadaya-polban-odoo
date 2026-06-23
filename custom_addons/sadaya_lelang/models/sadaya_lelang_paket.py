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
        ('draft', 'Draft'),
        ('menunggu_persetujuan', 'Menunggu Persetujuan'),
        ('pengumuman', 'Pengumuman'),
        ('pendaftaran', 'Pendaftaran Peserta'),
        ('penjelasan', 'Pemberian Penjelasan (Tanya Jawab)'),
        ('lelang', 'Lelang'),
        ('pemasukan_penawaran', 'Pemasukan Penawaran'),
        ('pembukaan', 'Pembukaan Penawaran'),
        ('eval_administrasi', 'Evaluasi Administrasi'),
        ('eval_teknis', 'Evaluasi Teknis'),
        ('eval_harga', 'Evaluasi Harga'),
        ('pembuktian_kualifikasi', 'Pembuktian Kualifikasi'),
        ('penetapan_pemenang', 'Penetapan Pemenang'),
        ('masa_sanggah', 'Masa Sanggah'),
        ('sppbj', 'SPPBJ / SPK'),
        ('pam', 'Pre-Award Meeting (PAM)'),
        ('kontrak', 'Tanda Tangan Kontrak'),
        ('pelaksanaan', 'Pelaksanaan Pekerjaan & BAST'),
        ('batal', 'Batal')
    ], string='Status', default='draft', tracking=True)

    # metode_pemilihan = fields.Selection([
    #     ('sadaya_lelang', 'Sadaya Lelang'),
    #     ('seleksi', 'Seleksi')
    # ], string='Metode Pemilihan', default='sadaya_lelang', tracking=True)

    metode_pemilihan = fields.Selection([
        ('sadaya_lelang', 'Sadaya Lelang'),
        ('seleksi', 'Seleksi'),
        ('tender', 'Tender')
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
    
    # Dokumen POKJA
    file_dokumen_pemilihan = fields.Binary(string='Dokumen Pemilihan')
    file_ba_penjelasan = fields.Binary(string='BA Pemberian Penjelasan')
    file_bahp = fields.Binary(string='Berita Acara Hasil Pelelangan (BAHP)')
    
    file_sppbj = fields.Binary(string='Dokumen SPPBJ')
    file_kontrak = fields.Binary(string='Dokumen Kontrak')
    file_jaminan_pelaksanaan = fields.Binary(string='Jaminan Pelaksanaan (Vendor)')
    file_bast = fields.Binary(string='Dokumen BAST')

    jadwal_ids = fields.One2many('sadaya_lelang.jadwal', 'paket_id', string='Jadwal Tender')
    dokumen_ids = fields.One2many('sadaya_lelang.dokumen', 'paket_id', string='Dokumen Pemilihan (Legacy)')
    penawaran_ids = fields.One2many('sadaya_lelang.penawaran', 'paket_id', string='Dokumen Penawaran')
    sanggah_ids = fields.One2many('sadaya_lelang.sanggah', 'paket_id', string='Daftar Sanggahan')
    penjelasan_ids = fields.One2many('sadaya_lelang.penjelasan', 'paket_id', string='Forum Tanya Jawab')

    def action_to_pengumuman(self):
        for rec in self: rec.status = 'pengumuman'

    def action_to_pendaftaran(self):
        for rec in self: rec.status = 'pendaftaran'

    def action_to_penjelasan(self):
        for rec in self: rec.status = 'penjelasan'

    def action_to_pemasukan(self):
        for rec in self: rec.status = 'pemasukan_penawaran'

    def action_to_pembukaan(self):
        for rec in self: rec.status = 'pembukaan'

    def action_mulai_evaluasi(self):
        for rec in self: rec.status = 'eval_administrasi'

    def action_tetapkan_pemenang(self):
        for rec in self: rec.status = 'penetapan_pemenang'

    def action_to_sppbj(self):
        for rec in self: rec.status = 'sppbj'

    def action_to_pam(self):
        for rec in self: rec.status = 'pam'

    def action_to_kontrak(self):
        for rec in self: rec.status = 'kontrak'

    def action_to_pelaksanaan(self):
        for rec in self: rec.status = 'pelaksanaan'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('kode_tender', 'New') == 'New':
                vals['kode_tender'] = self.env['ir.sequence'].next_by_code('sadaya_lelang.paket') or 'New'
        return super(SadayaLelangPaket, self).create(vals_list)
