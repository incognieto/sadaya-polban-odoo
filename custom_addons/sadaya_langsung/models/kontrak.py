# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SadayaLangsungKontrak(models.Model):
    _name = 'sadaya_langsung.kontrak'
    _description = 'Kontrak'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tanggal desc, id desc'

    # === Informasi Kontrak ===
    name = fields.Char(
        string='Nama Paket',
        required=True,
        tracking=True,
    )
    pejabat_pembuat = fields.Char(
        string='Pejabat Pembuat',
        tracking=True,
    )
    penyedia = fields.Char(
        string='Penyedia',
        tracking=True,
        help='Nama vendor/penyedia jasa',
    )
    jenis_pengadaan = fields.Selection([
        ('barang', 'Barang'),
        ('jasa_lainnya', 'Jasa Lainnya'),
        ('konstruksi', 'Konstruksi'),
        ('jasa_konsultansi', 'Jasa Konsultansi'),
    ], string='Jenis Pengadaan', tracking=True)

    # === Status Kontrak ===
    status_kontrak = fields.Selection([
        ('pam', 'Pre-Award Meeting (PAM)'),
        ('persiapan_kontrak', 'Persiapan Kontrak'),
        ('proses_tte', 'Proses Kontrak (TTE)'),
        ('pelaksanaan', 'Pelaksanaan Pekerjaan'),
        ('pemeriksaan', 'Pemeriksaan PPHP'),
        ('selesai_kontrak', 'Selesai Kontrak'),
        ('addendum_kontrak', 'Addendum Kontrak'),
        ('revisi', 'Revisi'),
        ('batal', 'Batal'),
    ], string='Status Kontrak', default='pam', tracking=True)

    # === Keuangan ===
    nilai_hps = fields.Float(
        string='Nilai HPS',
        tracking=True,
        help='Harga Perkiraan Sendiri (dalam Rupiah)',
    )

    # === Jadwal ===
    tanggal = fields.Date(string='Tanggal', default=fields.Date.today)
    tanggal_mulai = fields.Date(string='Tanggal Mulai')
    tanggal_selesai = fields.Date(string='Tanggal Selesai')

    # === Relasi ===
    paket_id = fields.Many2one(
        'sadaya_langsung.paket',
        string='Paket',
        ondelete='cascade',
    )

    # === Catatan ===
    keterangan = fields.Text(string='Keterangan')

    # ------------------------------------------------------------------
    # Auto-fill jenis_pengadaan dari Paket terkait
    # ------------------------------------------------------------------
    @api.onchange('paket_id')
    def _onchange_paket_id(self):
        if self.paket_id:
            self.name = self.paket_id.name
            self.jenis_pengadaan = self.paket_id.jenis_pengadaan
            self.nilai_hps = self.paket_id.nilai_hps

    # ------------------------------------------------------------------
    # Workflow buttons
    # ------------------------------------------------------------------
    def action_persiapan_kontrak(self):
        self.write({'status_kontrak': 'persiapan_kontrak'})

    def action_proses_tte(self):
        self.write({'status_kontrak': 'proses_tte'})

    def action_pelaksanaan(self):
        self.write({'status_kontrak': 'pelaksanaan'})

    def action_pemeriksaan(self):
        self.write({'status_kontrak': 'pemeriksaan'})

    def action_selesai_kontrak(self):
        self.write({'status_kontrak': 'selesai_kontrak'})

    def action_revisi(self):
        self.write({'status_kontrak': 'revisi'})

    def action_addendum(self):
        self.write({'status_kontrak': 'addendum_kontrak'})

    def action_batal(self):
        self.write({'status_kontrak': 'batal'})
