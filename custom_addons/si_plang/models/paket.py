# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SiPlangPaket(models.Model):
    _name = 'si_plang.paket'
    _description = 'Paket Pengadaan Langsung'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tanggal desc, id desc'

    # === Informasi Paket ===
    name = fields.Char(
        string='Nama Paket',
        required=True,
        tracking=True,
    )
    unit_pengusul = fields.Char(
        string='Unit Pengusul',
        tracking=True,
    )
    jenis_pengadaan = fields.Selection([
        ('barang', 'Barang'),
        ('jasa_lainnya', 'Jasa Lainnya'),
        ('konstruksi', 'Konstruksi'),
        ('jasa_konsultansi', 'Jasa Konsultansi'),
    ], string='Jenis Pengadaan', tracking=True)

    # === Status Workflow (sesuai BPMN 1.5.3) ===
    # 1. draft         = Pemicu paket (Admin buat paket baru)
    # 2. input_paket   = Input paket pengadaan (Admin sudah lengkapi detail)
    # 3. penawaran     = Submit penawaran langsung (Vendor kirim penawaran)
    # 4. seleksi       = Seleksi dan validasi (PP periksa dokumen)
    # 5. terbit_spk    = Terbitkan SPK (SPK diterbitkan)
    # 6. selesai       = Selesai pengadaan
    status_paket = fields.Selection([
        ('draft', 'Draft'),
        ('input_paket', 'Input Paket Pengadaan'),
        ('penawaran', 'Penawaran Vendor'),
        ('seleksi', 'Seleksi & Validasi'),
        ('terbit_spk', 'Terbit SPK'),
        ('selesai', 'Selesai'),
        ('batal', 'Batal'),
    ], string='Status Paket', default='draft', tracking=True)

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
    item_ids = fields.One2many(
        'si_plang.paket.line',
        'paket_id',
        string='Daftar Barang/Jasa',
    )

    penawaran_ids = fields.One2many(
        'si_plang.penawaran',
        'paket_id',
        string='Daftar Penawaran Vendor',
    )

    vendor_pemenang_id = fields.Many2one(
        'res.partner',
        string='Vendor Pemenang',
        tracking=True,
        help='Vendor yang terpilih sebagai pemenang pengadaan',
    )

    kontrak_ids = fields.One2many(
        'si_plang.kontrak',
        'paket_id',
        string='Kontrak / SPK',
    )

    # === Catatan ===
    keterangan = fields.Text(string='Keterangan')

    # ------------------------------------------------------------------
    # Constraint: Nilai HPS harus < 200 Juta (pengadaan langsung)
    # ------------------------------------------------------------------
    @api.constrains('nilai_hps')
    def _check_nilai_hps(self):
        for rec in self:
            if rec.nilai_hps and rec.nilai_hps >= 200000000:
                raise ValidationError(
                    "Nilai HPS untuk pengadaan langsung harus di bawah Rp200.000.000. "
                    "Jika nilainya di atas itu, gunakan modul Tender."
                )

    # ------------------------------------------------------------------
    # Workflow buttons (sesuai BPMN 1.5.3 Pengadaan Langsung)
    # ------------------------------------------------------------------
    def action_input_paket(self):
        """BPMN Step 1→2: Pemicu → Input paket pengadaan
        Admin melengkapi detail kebutuhan barang/jasa ke dalam sistem.
        """
        self.write({'status_paket': 'input_paket'})

    def action_submit_penawaran(self):
        """BPMN Step 2→3: Input paket → Submit penawaran langsung
        Vendor yang terpilih/melihat pengumuman mengirim penawaran.
        """
        self.write({'status_paket': 'penawaran'})

    def action_seleksi_validasi(self):
        """BPMN Step 3→4: Submit penawaran → Seleksi dan validasi
        Pejabat Pengadaan memeriksa dokumen penawaran & administrasi.
        """
        self.write({'status_paket': 'seleksi'})

    def action_terbitkan_spk(self):
        """BPMN Step 4→5: Seleksi dan validasi → Terbitkan SPK
        Penawaran valid, sistem terbitkan Surat Perintah Kerja.
        Auto-create Kontrak/SPK record.
        """
        for rec in self:
            # Pastikan sudah ada vendor pemenang
            if not rec.vendor_pemenang_id:
                raise ValidationError(
                    "Pilih Vendor Pemenang terlebih dahulu di tab 'Penawaran Vendor' "
                    "sebelum menerbitkan SPK."
                )
        self.write({'status_paket': 'terbit_spk'})
        # Auto-create kontrak/SPK jika belum ada
        for rec in self:
            if not rec.kontrak_ids:
                self.env['si_plang.kontrak'].create({
                    'name': rec.name,
                    'paket_id': rec.id,
                    'pejabat_pembuat': '',
                    'penyedia': rec.vendor_pemenang_id.name or '',
                    'jenis_pengadaan': rec.jenis_pengadaan,
                    'nilai_hps': rec.nilai_hps,
                    'status_kontrak': 'persiapan_kontrak',
                })

    def action_selesai(self):
        """BPMN Step 5→6: Terbitkan SPK → Selesai pengadaan
        SPK telah resmi diterbitkan, pengadaan selesai.
        """
        self.write({'status_paket': 'selesai'})

    def action_batal(self):
        """Exception: Batalkan paket"""
        self.write({'status_paket': 'batal'})

    def action_reset_draft(self):
        """Reset ke draft"""
        self.write({'status_paket': 'draft'})


class SiPlangPaketLine(models.Model):
    _name = 'si_plang.paket.line'
    _description = 'Detail Item Paket'

    paket_id = fields.Many2one('si_plang.paket', string='Paket', ondelete='cascade')
    name = fields.Char(string='Nama Barang/Jasa', required=True)
    deskripsi = fields.Text(string='Spesifikasi Teknis')
    qty = fields.Float(string='Jumlah', default=1.0)
    satuan = fields.Selection([
        ('unit', 'Unit'),
        ('set', 'Set'),
        ('pcs', 'Pcs'),
        ('lot', 'Lot'),
        ('m', 'Meter'),
        ('jam', 'Jam/Hari'),
    ], string='Satuan', default='unit')
    harga_satuan = fields.Float(string='Harga Satuan (Est.)')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('qty', 'harga_satuan')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.harga_satuan


class SiPlangPenawaran(models.Model):
    _name = 'si_plang.penawaran'
    _description = 'Penawaran Vendor'
    _order = 'harga_penawaran asc'

    paket_id = fields.Many2one(
        'si_plang.paket',
        string='Paket',
        required=True,
        ondelete='cascade',
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor / Penyedia',
        required=True,
        help='Pilih dari daftar vendor yang sudah terdaftar',
    )
    harga_penawaran = fields.Float(
        string='Harga Penawaran',
        required=True,
    )
    dokumen_penawaran = fields.Binary(
        string='Dokumen Penawaran',
        help='Upload file PDF penawaran dari vendor',
    )
    dokumen_filename = fields.Char(string='Nama File')
    catatan = fields.Text(string='Catatan')
    tanggal = fields.Date(
        string='Tanggal Penawaran',
        default=fields.Date.today,
    )
    status_penawaran = fields.Selection([
        ('masuk', 'Masuk'),
        ('evaluasi', 'Dalam Evaluasi'),
        ('terpilih', 'Terpilih (Pemenang)'),
        ('ditolak', 'Ditolak'),
    ], string='Status', default='masuk')

    def action_pilih_pemenang(self):
        """Tandai vendor ini sebagai pemenang dan set di Paket."""
        for rec in self:
            # Reset semua penawaran lain di paket ini
            siblings = self.search([
                ('paket_id', '=', rec.paket_id.id),
                ('id', '!=', rec.id),
            ])
            siblings.write({'status_penawaran': 'ditolak'})
            # Tandai ini sebagai pemenang
            rec.write({'status_penawaran': 'terpilih'})
            # Set vendor pemenang di paket
            rec.paket_id.write({'vendor_pemenang_id': rec.vendor_id.id})

    def action_tolak(self):
        """Tolak penawaran ini."""
        self.write({'status_penawaran': 'ditolak'})

    def action_reset_masuk(self):
        """Reset status ke masuk."""
        self.write({'status_penawaran': 'masuk'})
