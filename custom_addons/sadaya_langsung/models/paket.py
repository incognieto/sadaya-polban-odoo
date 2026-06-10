# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SadayaLangsungPaket(models.Model):
    _name = "sadaya_langsung.paket"
    _description = "Paket Sadaya Langsung"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "tanggal desc, id desc"

    # === Informasi Paket ===
    name = fields.Char(
        string="Nama Paket",
        required=True,
        tracking=True,
    )
    unit_pengusul = fields.Char(
        string="Unit Pengusul",
        tracking=True,
    )
    jenis_pengadaan = fields.Selection(
        [
            ("barang", "Barang"),
            ("jasa_lainnya", "Jasa Lainnya"),
            ("konstruksi", "Konstruksi"),
            ("jasa_konsultansi", "Jasa Konsultansi"),
        ],
        string="Jenis Pengadaan",
        tracking=True,
    )

    status_paket = fields.Selection(
        [
            ("draft", "Draft / Persiapan"),
            ("menunggu_persetujuan", "Menunggu Persetujuan"),
            ("pengumuman", "Pengumuman"),
            ("pendaftaran_peserta", "Pendaftaran Peserta"),
            ("pemasukan_penawaran", "Pemasukan Penawaran"),
            ("pembukaan_penawaran", "Pembukaan Penawaran"),
            ("evaluasi", "Evaluasi (A, K, T, H)"),
            ("pembuktian_kualifikasi", "Pembuktian Kualifikasi"),
            ("negosiasi", "Klarifikasi & Negosiasi"),
            ("penetapan", "Penetapan Pemenang"),
            ("spk_dibuat", "SPK Diterbitkan (Selesai)"),
            ("batal", "Batal"),
        ],
        string="Status Paket",
        default="draft",
        tracking=True,
    )

    # === Keuangan ===
    nilai_hps = fields.Float(
        string="Nilai HPS",
        tracking=True,
        help="Harga Perkiraan Sendiri (dalam Rupiah)",
    )

    # === Jadwal ===
    tanggal = fields.Date(string="Tanggal", default=fields.Date.today)
    tanggal_mulai = fields.Date(string="Tanggal Mulai")
    tanggal_selesai = fields.Date(string="Tanggal Selesai")

    # === Dokumen Persiapan ===
    dokumen_kak = fields.Binary(string="Dokumen KAK", tracking=True)
    filename_kak = fields.Char(string="Nama File KAK")
    dokumen_rab = fields.Binary(string="Dokumen RAB/HPS", tracking=True)
    filename_rab = fields.Char(string="Nama File RAB")

    # === Klarifikasi & Negosiasi ===
    catatan_negosiasi = fields.Text(
        string="Catatan Klarifikasi & Negosiasi", tracking=True
    )
    harga_sepakat = fields.Float(string="Harga Hasil Kesepakatan", tracking=True)

    # === Relasi ===
    item_ids = fields.One2many(
        "sadaya_langsung.paket.line",
        "paket_id",
        string="Daftar Barang/Jasa",
    )

    penawaran_ids = fields.One2many(
        "sadaya_langsung.penawaran",
        "paket_id",
        string="Daftar Penawaran Vendor",
    )

    vendor_pemenang_id = fields.Many2one(
        "res.partner",
        string="Vendor Pemenang",
        tracking=True,
        help="Vendor yang terpilih sebagai pemenang pengadaan",
        domain=[("is_sadaya_mitra_vendor", "=", True)],
    )

    kontrak_ids = fields.One2many(
        "sadaya_langsung.kontrak",
        "paket_id",
        string="Kontrak / SPK",
    )

    contract_count = fields.Integer(
        string="Contract Count",
        compute="_compute_contract_count",
        store=True,
    )

    # === Catatan ===
    keterangan = fields.Text(string="Keterangan")

    # ------------------------------------------------------------------
    # Helper: infer Unit Pengusul from Sadaya Rancang (rancang.usulan)
    # ------------------------------------------------------------------
    def _infer_unit_pengusul(self, name, nilai_hps):
        """Best-effort inference for Unit Pengusul.

        Constraint: we only change module sadaya_langsung.
        Data that already flows to sadaya_langsung from upstream modules:
        - rancang.usulan.name -> sadaya_tawar.paket.name -> sadaya_langsung.paket.name
        - rancang.usulan.rab  -> sadaya_tawar.paket.nilai_hps -> sadaya_langsung.paket.nilai_hps
        """
        if not name or not nilai_hps:
            return False

        # Avoid hard dependency if sadaya_rancang is not installed.
        if "rancang.usulan" not in self.env.registry:
            return False

        # Float tolerance (rab/nilai_hps represent Rupiah but stored as float).
        eps = 0.01
        domain = [
            ("name", "=", name),
            ("rab", ">=", float(nilai_hps) - eps),
            ("rab", "<=", float(nilai_hps) + eps),
            ("state", "=", "published"),
            ("pemohon", "!=", False),
        ]
        usulan = (
            self.env["rancang.usulan"].sudo().search(domain, order="id desc", limit=1)
        )
        return usulan.pemohon or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("unit_pengusul"):
                inferred = self._infer_unit_pengusul(
                    vals.get("name"), vals.get("nilai_hps")
                )
                if inferred:
                    vals["unit_pengusul"] = inferred
        return super().create(vals_list)

    @api.depends("kontrak_ids")
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.kontrak_ids)

    # ------------------------------------------------------------------
    # Constraint: Nilai HPS harus < 200 Juta (pengadaan langsung)
    # ------------------------------------------------------------------
    @api.constrains("nilai_hps")
    def _check_nilai_hps(self):
        for rec in self:
            if rec.nilai_hps and rec.nilai_hps >= 200000000:
                raise ValidationError(
                    "Nilai HPS untuk pengadaan langsung harus di bawah Rp200.000.000. "
                    "Jika nilainya di atas itu, gunakan modul SadayaLelang."
                )

    def _get_allowed_status_transitions(self):
        return {
            "draft": ["menunggu_persetujuan", "batal"],
            "menunggu_persetujuan": ["pengumuman", "batal"],
            "pengumuman": ["pendaftaran_peserta", "batal"],
            "pendaftaran_peserta": ["pemasukan_penawaran", "batal"],
            "pemasukan_penawaran": ["pembukaan_penawaran", "batal"],
            "pembukaan_penawaran": ["evaluasi", "batal"],
            "evaluasi": ["pembuktian_kualifikasi", "negosiasi", "batal"],
            "pembuktian_kualifikasi": ["negosiasi", "batal"],
            "negosiasi": ["penetapan", "batal"],
            "penetapan": ["spk_dibuat", "batal"],
            "spk_dibuat": [],
            "batal": ["draft"],
        }

    def _ensure_status_transition_allowed(self, status):
        for rec in self:
            if rec.status_paket == status:
                continue
            allowed = self._get_allowed_status_transitions().get(rec.status_paket, [])
            if status not in allowed:
                raise ValidationError(
                    "Transisi status dari %s ke %s tidak diizinkan."
                    % (rec.status_paket, status)
                )

    def _ensure_vendor_pemenang(self):
        for rec in self:
            if not rec.vendor_pemenang_id:
                raise ValidationError(
                    "Harap pilih Vendor terlebih dahulu sebelum melanjutkan ke tahap ini."
                )

    def _ensure_ready_for_undangan(self, vals=None):
        vals = vals or {}
        for rec in self:
            tanggal_mulai = vals.get("tanggal_mulai", rec.tanggal_mulai)
            tanggal_selesai = vals.get("tanggal_selesai", rec.tanggal_selesai)

            if not tanggal_mulai or not tanggal_selesai:
                raise ValidationError(
                    "Tanggal Mulai dan Tanggal Selesai wajib diisi sebelum melanjutkan."
                )
            if tanggal_selesai < tanggal_mulai:
                raise ValidationError(
                    "Tanggal Selesai tidak boleh lebih awal dari Tanggal Mulai."
                )
            if not rec.penawaran_ids or not any(p.vendor_id for p in rec.penawaran_ids):
                raise ValidationError(
                    "Minimal 1 Vendor wajib diisi di subtab 'Pengolahan Penawaran' sebelum mengirim undangan."
                )

    def _ensure_contract_not_exists(self):
        for rec in self:
            if rec.kontrak_ids:
                raise ValidationError("Kontrak sudah dibuat untuk paket ini.")

    def action_ajukan(self):
        """Step 1→2: Draft → Menunggu Persetujuan"""
        self._ensure_status_transition_allowed("menunggu_persetujuan")
        self.write({"status_paket": "menunggu_persetujuan"})

    def action_pengumuman(self):
        """Step 2→3: Menunggu Persetujuan → Pengumuman"""
        self._ensure_status_transition_allowed("pengumuman")
        self._ensure_ready_for_undangan()
        self.write({"status_paket": "pengumuman"})

    def action_pendaftaran(self):
        """Step 3→4: Pengumuman → Pendaftaran Peserta"""
        self._ensure_status_transition_allowed("pendaftaran_peserta")
        self.write({"status_paket": "pendaftaran_peserta"})

    def action_pemasukan_penawaran(self):
        """Step 4→6: Pendaftaran Peserta → Pemasukan Penawaran"""
        self._ensure_status_transition_allowed("pemasukan_penawaran")
        self.write({"status_paket": "pemasukan_penawaran"})

    def action_pembukaan_penawaran(self):
        """Step 4→5: Pemasukan Penawaran → Pembukaan Penawaran"""
        self._ensure_status_transition_allowed("pembukaan_penawaran")
        self.write({"status_paket": "pembukaan_penawaran"})

    def action_evaluasi(self):
        """Step 5→6: Pembukaan Penawaran → Evaluasi"""
        self._ensure_status_transition_allowed("evaluasi")
        self.write({"status_paket": "evaluasi"})

    def action_pembuktian_kualifikasi(self):
        """Step 6→7: Evaluasi → Pembuktian Kualifikasi"""
        self._ensure_status_transition_allowed("pembuktian_kualifikasi")
        self.write({"status_paket": "pembuktian_kualifikasi"})

    def action_negosiasi(self):
        """Step 7→8: Pembuktian Kualifikasi / Evaluasi → Klarifikasi & Negosiasi"""
        self._ensure_status_transition_allowed("negosiasi")
        self.write({"status_paket": "negosiasi"})

    def action_tetapkan_pemenang(self):
        """Step 8→9: Negosiasi → Penetapan Pemenang"""
        self._ensure_status_transition_allowed("penetapan")
        self._ensure_vendor_pemenang()
        self.write({"status_paket": "penetapan"})

    def action_buat_spk(self):
        """Step 9: Penetapan Pemenang → Buat SPK"""
        self._ensure_status_transition_allowed("spk_dibuat")
        self._ensure_vendor_pemenang()
        self._ensure_contract_not_exists()
        self.write({"status_paket": "spk_dibuat"})

    def _create_contract_if_needed(self):
        for rec in self:
            if rec.status_paket == "spk_dibuat" and not rec.kontrak_ids:
                if not rec.vendor_pemenang_id:
                    raise ValidationError(
                        "Vendor pemenang harus diisi sebelum membuat kontrak."
                    )
                self.env["sadaya_langsung.kontrak"].create(
                    {
                        "name": rec.name,
                        "paket_id": rec.id,
                        "pejabat_pembuat": self.env.user.name,
                        "penyedia": rec.vendor_pemenang_id.name,
                        "jenis_pengadaan": rec.jenis_pengadaan,
                        "nilai_hps": rec.nilai_hps,
                        "tanggal_mulai": rec.tanggal_mulai,
                        "tanggal_selesai": rec.tanggal_selesai,
                        "status_kontrak": "pam",
                    }
                )

    def write(self, vals):
        if vals.get("status_paket"):
            self._ensure_status_transition_allowed(vals.get("status_paket"))
            if vals.get("status_paket") == "pengumuman":
                self._ensure_ready_for_undangan(vals)
            if vals.get("status_paket") == "spk_dibuat":
                self._ensure_vendor_pemenang()
                if any(rec.kontrak_ids for rec in self):
                    raise ValidationError("Kontrak sudah dibuat untuk paket ini.")
        res = super(SadayaLangsungPaket, self).write(vals)
        if vals.get("status_paket") == "spk_dibuat":
            self._create_contract_if_needed()

        # Backfill unit_pengusul on any write, but never override explicit edits.
        if "unit_pengusul" not in vals:
            for rec in self.filtered(
                lambda r: not r.unit_pengusul and r.name and r.nilai_hps
            ):
                inferred = rec._infer_unit_pengusul(rec.name, rec.nilai_hps)
                if inferred:
                    super(SadayaLangsungPaket, rec).write({"unit_pengusul": inferred})
        return res

    def action_selesai(self):
        """Step 7→8: Kontrak → Selesai"""
        self._ensure_status_transition_allowed("selesai")
        self.write({"status_paket": "selesai"})

    def action_batal(self):
        """Exception: Batalkan paket"""
        self.write({"status_paket": "batal"})

    def action_reset_draft(self):
        """Reset ke draft"""
        self.write({"status_paket": "draft"})


class SadayaLangsungPaketLine(models.Model):
    _name = "sadaya_langsung.paket.line"
    _description = "Detail Item Paket"

    paket_id = fields.Many2one(
        "sadaya_langsung.paket", string="Paket", ondelete="cascade"
    )
    name = fields.Char(string="Nama Barang/Jasa", required=True)
    deskripsi = fields.Text(string="Spesifikasi Teknis")
    qty = fields.Float(string="Jumlah", default=1.0)
    satuan = fields.Selection(
        [
            ("unit", "Unit"),
            ("set", "Set"),
            ("pcs", "Pcs"),
            ("lot", "Lot"),
            ("m", "Meter"),
            ("jam", "Jam/Hari"),
        ],
        string="Satuan",
        default="unit",
    )
    harga_satuan = fields.Float(string="Harga Satuan (Est.)")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends("qty", "harga_satuan")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.harga_satuan


class SadayaLangsungPenawaran(models.Model):
    _name = "sadaya_langsung.penawaran"
    _description = "Penawaran Vendor"
    _order = "harga_penawaran asc"

    paket_id = fields.Many2one(
        "sadaya_langsung.paket",
        string="Paket",
        required=True,
        ondelete="cascade",
    )
    vendor_id = fields.Many2one(
        "res.partner",
        string="Vendor / Penyedia",
        required=True,
        domain=[("is_sadaya_mitra_vendor", "=", True)],
    )
    harga_penawaran = fields.Float(string="Harga Penawaran")
    tanggal = fields.Date(string="Tanggal Penawaran", default=fields.Date.today)

    dokumen_penawaran = fields.Binary(string="Dokumen Penawaran")
    dokumen_filename = fields.Char(string="Nama Dokumen")
    catatan = fields.Text(string="Catatan / Keterangan")

    # === Evaluasi ===
    evaluasi_administrasi = fields.Selection(
        [("lulus", "Lulus"), ("gugur", "Gugur")], string="Admin"
    )
    evaluasi_teknis = fields.Selection(
        [("lulus", "Lulus"), ("gugur", "Gugur")], string="Teknis"
    )
    evaluasi_harga = fields.Selection(
        [("lulus", "Lulus"), ("gugur", "Gugur")], string="Harga"
    )
    lulus_evaluasi = fields.Boolean(
        string="Lulus Total", compute="_compute_lulus", store=True
    )

    status_penawaran = fields.Selection(
        [
            ("diajukan", "Diajukan"),
            ("dipilih", "Dipilih sbg Pemenang"),
            ("ditolak", "Ditolak"),
        ],
        string="Status",
        default="diajukan",
    )

    @api.depends("evaluasi_administrasi", "evaluasi_teknis", "evaluasi_harga")
    def _compute_lulus(self):
        for rec in self:
            rec.lulus_evaluasi = (
                rec.evaluasi_administrasi == "lulus"
                and rec.evaluasi_teknis == "lulus"
                and rec.evaluasi_harga == "lulus"
            )

    def action_pilih_pemenang(self):
        for rec in self:
            if not rec.lulus_evaluasi:
                raise ValidationError("Vendor tidak memenuhi syarat lulus evaluasi!")
            if not rec.harga_penawaran:
                raise ValidationError(
                    "Harga penawaran wajib diisi sebelum menetapkan pemenang."
                )
            # Reset semua penawaran lain di paket ini
            siblings = self.search(
                [
                    ("paket_id", "=", rec.paket_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            siblings.write({"status_penawaran": "ditolak"})

            rec.status_penawaran = "dipilih"
            rec.paket_id.vendor_pemenang_id = rec.vendor_id
            rec.paket_id.harga_sepakat = rec.harga_penawaran

    def action_tolak(self):
        """Tolak penawaran ini."""
        self.write({"status_penawaran": "ditolak"})

    def action_reset_masuk(self):
        """Reset status ke masuk."""
        self.write({"status_penawaran": "diajukan"})
