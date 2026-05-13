# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SadayaLangsungPaket(models.Model):
    _name = 'sadaya_langsung.paket'
    _description = 'Paket Sadaya Langsung'
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

    # === Status Workflow (sesuai SOP Pengadaan Polban & SPSE) ===
    # 1. draft         = Persiapan Pengadaan (Draft HPS & Syarat)
    # 2. undangan      = Undangan/Permintaan Penawaran ke Penyedia
    # 3. penawaran     = Menunggu Penawaran Vendor
    # 4. evaluasi      = Evaluasi Administrasi, Kualifikasi, Teknis, dan Harga
    # 5. negosiasi     = Klarifikasi dan Negosiasi Teknis & Harga
    # 6. sppbj         = Penetapan / Surat Penunjukan Penyedia Barang/Jasa
    # 7. kontrak       = Penandatanganan SPK/Kontrak
    # 8. selesai       = Selesai
    status_paket = fields.Selection([
        ('draft', 'Draft / Persiapan'),
        ('undangan', 'Kirim Undangan'),
        ('penawaran', 'Menunggu Penawaran'),
        ('evaluasi', 'Evaluasi'),
        ('negosiasi', 'Klarifikasi & Negosiasi'),
        ('sppbj', 'Penetapan Penyedia (SPPBJ)'),
        ('kontrak', 'Kontrak / SPK'),
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

    # === Dokumen Persiapan ===
    dokumen_kak = fields.Binary(string='Dokumen KAK', tracking=True)
    filename_kak = fields.Char(string='Nama File KAK')
    dokumen_rab = fields.Binary(string='Dokumen RAB/HPS', tracking=True)
    filename_rab = fields.Char(string='Nama File RAB')

    # === Klarifikasi & Negosiasi ===
    catatan_negosiasi = fields.Text(string='Catatan Klarifikasi & Negosiasi', tracking=True)
    harga_sepakat = fields.Float(string='Harga Hasil Kesepakatan', tracking=True)

    # === Relasi ===
    item_ids = fields.One2many(
        'sadaya_langsung.paket.line',
        'paket_id',
        string='Daftar Barang/Jasa',
    )

    penawaran_ids = fields.One2many(
        'sadaya_langsung.penawaran',
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
        'sadaya_langsung.kontrak',
        'paket_id',
        string='Kontrak / SPK',
    )

    contract_count = fields.Integer(
        string='Contract Count',
        compute='_compute_contract_count',
        store=True,
    )

    # === Catatan ===
    keterangan = fields.Text(string='Keterangan')

    @api.depends('kontrak_ids')
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.kontrak_ids)

    # ------------------------------------------------------------------
    # Constraint: Nilai HPS harus < 200 Juta (pengadaan langsung)
    # ------------------------------------------------------------------
    @api.constrains('nilai_hps')
    def _check_nilai_hps(self):
        for rec in self:
            if rec.nilai_hps and rec.nilai_hps >= 200000000:
                raise ValidationError(
                    "Nilai HPS untuk pengadaan langsung harus di bawah Rp200.000.000. "
                    "Jika nilainya di atas itu, gunakan modul SadayaLelang."
                )

    def _get_allowed_status_transitions(self):
        return {
            'draft': ['undangan', 'batal'],
            'undangan': ['penawaran', 'batal'],
            'penawaran': ['evaluasi', 'batal'],
            'evaluasi': ['negosiasi', 'batal'],
            'negosiasi': ['sppbj', 'batal'],
            'sppbj': ['kontrak', 'batal'],
            'kontrak': ['selesai', 'batal'],
            'selesai': [],
            'batal': ['draft'],
        }

    def _ensure_status_transition_allowed(self, status):
        for rec in self:
            if rec.status_paket == status:
                continue
            allowed = self._get_allowed_status_transitions().get(rec.status_paket, [])
            if status not in allowed:
                raise ValidationError(
                    "Transisi status dari %s ke %s tidak diizinkan." % (
                        rec.status_paket, status
                    )
                )

    def _ensure_vendor_pemenang(self):
        for rec in self:
            if not rec.vendor_pemenang_id:
                raise ValidationError(
                    "Harap pilih Vendor Pemenang terlebih dahulu sebelum melanjutkan ke tahap ini."
                )

    def _ensure_contract_not_exists(self):
        for rec in self:
            if rec.kontrak_ids:
                raise ValidationError(
                    "Kontrak sudah dibuat untuk paket ini."
                )

    def action_kirim_undangan(self):
        """Step 1→2: Draft → Kirim Undangan"""
        self._ensure_status_transition_allowed('undangan')
        self.write({'status_paket': 'undangan'})

    def action_tunggu_penawaran(self):
        """Step 2→3: Kirim Undangan → Menunggu Penawaran"""
        self._ensure_status_transition_allowed('penawaran')
        self.write({'status_paket': 'penawaran'})

    def action_evaluasi(self):
        """Step 3→4: Penawaran → Evaluasi"""
        self._ensure_status_transition_allowed('evaluasi')
        self.write({'status_paket': 'evaluasi'})

    def action_negosiasi(self):
        """Step 4→5: Evaluasi → Klarifikasi & Negosiasi"""
        self._ensure_status_transition_allowed('negosiasi')
        self.write({'status_paket': 'negosiasi'})
        
    def action_tetapkan_pemenang(self):
        """Step 5→6: Negosiasi → SPPBJ (Penetapan)"""
        self._ensure_status_transition_allowed('sppbj')
        self._ensure_vendor_pemenang()
        self.write({'status_paket': 'sppbj'})

    def action_buat_kontrak(self):
        """Step 6→7: SPPBJ → Kontrak/SPK"""
        self._ensure_status_transition_allowed('kontrak')
        self._ensure_vendor_pemenang()
        self._ensure_contract_not_exists()
        self.write({'status_paket': 'kontrak'})

    def _create_contract_if_needed(self):
        for rec in self:
            if rec.status_paket == 'kontrak' and not rec.kontrak_ids:
                if not rec.vendor_pemenang_id:
                    raise ValidationError(
                        "Vendor pemenang harus diisi sebelum membuat kontrak."
                    )
                self.env['sadaya_langsung.kontrak'].create({
                    'name': rec.name,
                    'paket_id': rec.id,
                    'pejabat_pembuat': self.env.user.name,
                    'penyedia': rec.vendor_pemenang_id.name,
                    'jenis_pengadaan': rec.jenis_pengadaan,
                    'nilai_hps': rec.nilai_hps,
                    'tanggal_mulai': rec.tanggal_mulai,
                    'tanggal_selesai': rec.tanggal_selesai,
                    'status_kontrak': 'persiapan_kontrak',
                })

    def write(self, vals):
        if vals.get('status_paket'):
            self._ensure_status_transition_allowed(vals.get('status_paket'))
            if vals.get('status_paket') == 'kontrak':
                self._ensure_vendor_pemenang()
                if any(rec.kontrak_ids for rec in self):
                    raise ValidationError(
                        "Kontrak sudah dibuat untuk paket ini."
                    )
        res = super(SadayaLangsungPaket, self).write(vals)
        if vals.get('status_paket') == 'kontrak':
            self._create_contract_if_needed()
        return res

    def action_selesai(self):
        """Step 7→8: Kontrak → Selesai"""
        self._ensure_status_transition_allowed('selesai')
        self.write({'status_paket': 'selesai'})

    def action_batal(self):
        """Exception: Batalkan paket"""
        self.write({'status_paket': 'batal'})

    def action_reset_draft(self):
        """Reset ke draft"""
        self.write({'status_paket': 'draft'})


class SadayaLangsungPaketLine(models.Model):
    _name = 'sadaya_langsung.paket.line'
    _description = 'Detail Item Paket'

    paket_id = fields.Many2one('sadaya_langsung.paket', string='Paket', ondelete='cascade')
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


class SadayaLangsungPenawaran(models.Model):
    _name = 'sadaya_langsung.penawaran'
    _description = 'Penawaran Vendor'
    _order = 'harga_penawaran asc'

    paket_id = fields.Many2one(
        'sadaya_langsung.paket',
        string='Paket',
        required=True,
        ondelete='cascade',
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor / Penyedia',
        required=True,
    )
    harga_penawaran = fields.Float(string='Harga Penawaran', required=True)
    tanggal = fields.Date(string='Tanggal Penawaran', default=fields.Date.today)
    
    dokumen_penawaran = fields.Binary(string='Dokumen Penawaran')
    dokumen_filename = fields.Char(string='Nama Dokumen')
    catatan = fields.Text(string='Catatan / Keterangan')
    
    # === Evaluasi ===
    evaluasi_administrasi = fields.Selection([('lulus', 'Lulus'), ('gugur', 'Gugur')], string='Admin')
    evaluasi_teknis = fields.Selection([('lulus', 'Lulus'), ('gugur', 'Gugur')], string='Teknis')
    evaluasi_harga = fields.Selection([('lulus', 'Lulus'), ('gugur', 'Gugur')], string='Harga')
    lulus_evaluasi = fields.Boolean(string='Lulus Total', compute='_compute_lulus', store=True)

    status_penawaran = fields.Selection([
        ('diajukan', 'Diajukan'),
        ('dipilih', 'Dipilih sbg Pemenang'),
        ('ditolak', 'Ditolak')
    ], string='Status', default='diajukan')

    @api.depends('evaluasi_administrasi', 'evaluasi_teknis', 'evaluasi_harga')
    def _compute_lulus(self):
        for rec in self:
            rec.lulus_evaluasi = (
                rec.evaluasi_administrasi == 'lulus' and 
                rec.evaluasi_teknis == 'lulus' and 
                rec.evaluasi_harga == 'lulus'
            )

    def action_pilih_pemenang(self):
        for rec in self:
            if not rec.lulus_evaluasi:
                raise ValidationError("Vendor tidak memenuhi syarat lulus evaluasi!")
            # Reset semua penawaran lain di paket ini
            siblings = self.search([
                ('paket_id', '=', rec.paket_id.id),
                ('id', '!=', rec.id),
            ])
            siblings.write({'status_penawaran': 'ditolak'})
            
            rec.status_penawaran = 'dipilih'
            rec.paket_id.vendor_pemenang_id = rec.vendor_id
            rec.paket_id.harga_sepakat = rec.harga_penawaran

    def action_tolak(self):
        """Tolak penawaran ini."""
        self.write({'status_penawaran': 'ditolak'})

    def action_reset_masuk(self):
        """Reset status ke masuk."""
        self.write({'status_penawaran': 'diajukan'})
