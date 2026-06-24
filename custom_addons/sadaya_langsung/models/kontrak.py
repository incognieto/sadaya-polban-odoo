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
        ('addendum_diajukan', 'Addendum Diajukan'),
        ('addendum_disetujui', 'Addendum Disetujui'),
        ('addendum_tte_ppk', 'Addendum TTE PPK'),
        ('pemeriksaan', 'Pemeriksaan PPHP'),
        ('selesai_kontrak', 'Selesai Kontrak'),
        ('addendum_kontrak', 'Addendum Kontrak (Aktif)'),
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

    # === Addendum & TTE Fields ===
    justifikasi_addendum = fields.Text(string='Justifikasi Addendum')
    addendum_nilai_tambah = fields.Float(string='Nilai Tambahan Addendum')
    addendum_perpanjangan_hari = fields.Integer(string='Perpanjangan Hari Addendum')
    dokumen_addendum = fields.Binary(string='Dokumen Addendum')
    filename_addendum = fields.Char(string='Filename Addendum')
    tte_ppk_kontrak = fields.Boolean(string='TTE PPK Kontrak', default=False)
    tte_vendor_kontrak = fields.Boolean(string='TTE Vendor Kontrak', default=False)
    tte_ppk_addendum = fields.Boolean(string='TTE PPK Addendum', default=False)
    tte_vendor_addendum = fields.Boolean(string='TTE Vendor Addendum', default=False)

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

    def action_tte_ppk(self):
        self.write({'tte_ppk_kontrak': True})
        if self.tte_vendor_kontrak:
            self.action_pelaksanaan()

    def action_tte_vendor(self):
        self.write({'tte_vendor_kontrak': True})
        if self.tte_ppk_kontrak:
            self.action_pelaksanaan()

    def action_pelaksanaan(self):
        self.write({'status_kontrak': 'pelaksanaan'})

    def action_ajukan_addendum(self, justifikasi, nilai_tambah, perpanjangan_hari):
        self.write({
            'status_kontrak': 'addendum_diajukan',
            'justifikasi_addendum': justifikasi,
            'addendum_nilai_tambah': nilai_tambah,
            'addendum_perpanjangan_hari': perpanjangan_hari,
            'tte_ppk_addendum': False,
            'tte_vendor_addendum': False,
        })

    def action_setujui_addendum(self):
        import base64
        self.write({
            'status_kontrak': 'addendum_disetujui',
            'dokumen_addendum': base64.b64encode(b"Dokumen Addendum Ke-1").decode('utf-8'),
            'filename_addendum': "Addendum_Ke-1.pdf"
        })

    def action_tte_ppk_addendum(self):
        self.write({
            'tte_ppk_addendum': True,
            'status_kontrak': 'addendum_tte_ppk',
        })

    def action_tte_vendor_addendum(self):
        from datetime import timedelta
        self.write({
            'tte_vendor_addendum': True,
            'status_kontrak': 'addendum_kontrak',
        })
        # Update nilai kontrak (nilai_hps)
        new_nilai = self.nilai_hps + self.addendum_nilai_tambah
        # Update timeline (tanggal_selesai)
        vals = {'nilai_hps': new_nilai}
        if self.tanggal_selesai:
            t_selesai = fields.Date.to_date(self.tanggal_selesai)
            vals['tanggal_selesai'] = t_selesai + timedelta(days=self.addendum_perpanjangan_hari)
        self.write(vals)

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
