# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProcurementPackage(models.Model):
    _name = "sadaya_rutin.procurement_package"
    _description = "Sadaya Rutin Package"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    code = fields.Char(string="Kode Paket", tracking=True)
    name = fields.Char(string="Nama Paket", required=True, tracking=True)

    amount_total = fields.Monetary(
        string="Nilai",
        currency_field="currency_id",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
    )

    procurement_type = fields.Selection(
        [
            ("goods", "Barang"),
            ("services", "Jasa Lainnya"),
            ("construction", "Konstruksi"),
            ("consulting", "Jasa Konsultansi"),
        ],
        string="Jenis Pengadaan",
        required=True,
        tracking=True,
    )

    proposing_unit = fields.Char(string="Unit Pengusul", tracking=True)

    start_date = fields.Date(string="Tanggal Mulai", tracking=True)
    end_date = fields.Date(string="Tanggal Selesai", tracking=True)

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("ecatalog_check", "Cek E-Katalog"),
            ("negotiation_vendor", "Negosiasi (Penyedia)"),
            ("negotiation_pp", "Negosiasi (PP)"),
            ("negotiation_done", "Negosiasi Selesai"),
            ("negotiation_minutes", "Proses Berita Acara Negosiasi"),
            ("spk_preparation", "Persiapan SPK"),
            ("spk_process", "Proses SPK"),
            ("delivery", "Pengiriman"),
            ("inspection", "Pemeriksaan"),
            ("done", "Selesai"),
            ("revision", "Revisi"),
            ("addendum", "Addendum SPK"),
            ("cancelled", "Batal"),
        ],
        string="Status Paket",
        default="draft",
        tracking=True,
    )

    # Tab 1 - Data Permintaan
    item_name = fields.Char(string="Nama Barang/Jasa")
    item_spec = fields.Text(string="Spesifikasi")
    item_qty = fields.Float(string="Jumlah")
    estimated_budget = fields.Monetary(
        string="Estimasi Anggaran",
        currency_field="currency_id",
    )
    request_notes = fields.Text(string="Catatan Permintaan")

    # Tab 2 - Cek E-Katalog
    ecatalog_status = fields.Selection(
        [
            ("available", "Tersedia"),
            ("not_available", "Tidak Tersedia"),
        ],
        string="Status E-Katalog",
        default="available",
    )
    ecatalog_notes = fields.Text(string="Catatan E-Katalog")

    # Tab 3 - Negosiasi
    vendor_name = fields.Char(string="Vendor")
    negotiation_price = fields.Monetary(
        string="Harga Negosiasi",
        currency_field="currency_id",
    )
    negotiation_notes = fields.Text(string="Catatan Negosiasi")
    negotiation_history = fields.Text(string="Riwayat Tawar-Menawar")

    # Tab 4 - Surat Pesanan (SP)
    sp_number = fields.Char(string="Nomor Surat Pesanan")
    sp_date = fields.Date(string="Tanggal Surat Pesanan")
    sp_signed_ppk = fields.Boolean(string="TTE PPK")
    sp_signed_vendor = fields.Boolean(string="TTE Vendor (SP)")

    # Tab 5 - Pengiriman
    delivery_date = fields.Date(string="Tanggal Pengiriman")
    delivery_notes = fields.Text(string="Catatan Pengiriman")

    # Tab 6 - Pemeriksaan & Serah Terima
    inspection_status = fields.Selection(
        [
            ("ok", "Sesuai Spek"),
            ("not_ok", "Tidak Sesuai"),
        ],
        string="Hasil Pemeriksaan",
    )
    inspection_notes = fields.Text(string="Catatan Pemeriksaan")
    bast_number = fields.Char(string="Nomor BAST")
    bast_date = fields.Date(string="Tanggal BAST")
    bast_signed_pphp = fields.Boolean(string="TTE Tim Teknis/PPHP")
    bast_signed_user = fields.Boolean(string="TTE User")
    bast_signed_vendor = fields.Boolean(string="TTE Vendor (BAST)")

    # Tab 7 - Selesai
    completion_notes = fields.Text(string="Catatan Penyelesaian")

    needs_reroute = fields.Boolean(
        string="Alihkan ke Sadaya Langsung",
        compute="_compute_needs_reroute",
    )
    requires_ppk = fields.Boolean(
        string="Butuh PPK (> 200 Juta)",
        compute="_compute_requires_ppk",
    )

    contract_ids = fields.One2many(
        "sadaya_rutin.contract",
        "package_id",
        string="Kontrak",
    )

    contract_count = fields.Integer(compute="_compute_contract_count")

    @api.depends("ecatalog_status")
    def _compute_needs_reroute(self):
        for rec in self:
            rec.needs_reroute = rec.ecatalog_status == "not_available"

    @api.depends("amount_total")
    def _compute_requires_ppk(self):
        for rec in self:
            rec.requires_ppk = (rec.amount_total or 0.0) > 200000000.0

    @api.constrains("delivery_date")
    def _check_delivery_weekday(self):
        for rec in self:
            if rec.delivery_date and rec.delivery_date.weekday() >= 5:
                raise ValidationError(
                    "Pengiriman hanya dapat dijadwalkan pada hari kerja (Senin-Jumat)."
                )

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.contract_ids)

    def _ensure_status(self, allowed):
        for rec in self:
            if rec.status not in allowed:
                raise ValidationError("Status paket tidak sesuai untuk tindakan ini.")

    def _ensure_required(self, fields_map):
        for rec in self:
            missing = [label for label, value in fields_map.items() if not value]
            if missing:
                raise ValidationError(
                    "Field wajib belum lengkap: %s" % ", ".join(missing)
                )

    def action_to_ecatalog(self):
        self._ensure_status(["draft", "revision"])
        for rec in self:
            rec._ensure_required(
                {
                    "Nama Barang/Jasa": rec.item_name,
                    "Jumlah": rec.item_qty,
                    "Estimasi Anggaran": rec.estimated_budget,
                }
            )
            rec.status = "ecatalog_check"

    def action_to_negotiation_vendor(self):
        self._ensure_status(["ecatalog_check"])
        for rec in self:
            if rec.ecatalog_status == "not_available":
                raise ValidationError(
                    "Barang tidak tersedia di e-katalog. Alihkan ke Sadaya Langsung."
                )
            rec.status = "negotiation_vendor"

    def action_to_negotiation_pp(self):
        self._ensure_status(["negotiation_vendor"])
        for rec in self:
            rec._ensure_required({"Vendor": rec.vendor_name})
            rec.status = "negotiation_pp"

    def action_to_negotiation_done(self):
        self._ensure_status(["negotiation_pp"])
        for rec in self:
            rec._ensure_required({"Harga Negosiasi": rec.negotiation_price})
            rec.status = "negotiation_done"

    def action_to_negotiation_minutes(self):
        self._ensure_status(["negotiation_done"])
        for rec in self:
            rec.status = "negotiation_minutes"

    def action_to_spk_preparation(self):
        self._ensure_status(["negotiation_minutes"])
        for rec in self:
            rec.status = "spk_preparation"

    def action_to_spk_process(self):
        self._ensure_status(["spk_preparation"])
        for rec in self:
            rec._ensure_required({"Nomor SP": rec.sp_number, "Tanggal SP": rec.sp_date})
            rec.status = "spk_process"

    def action_to_delivery(self):
        self._ensure_status(["spk_process"])
        for rec in self:
            if not (rec.sp_signed_ppk and rec.sp_signed_vendor):
                raise ValidationError("TTE PPK dan Vendor harus lengkap sebelum Pengiriman.")
            rec.status = "delivery"

    def action_to_inspection(self):
        self._ensure_status(["delivery"])
        for rec in self:
            rec._ensure_required({"Tanggal Pengiriman": rec.delivery_date})
            rec.status = "inspection"

    def action_to_done(self):
        self._ensure_status(["inspection"])
        for rec in self:
            if rec.inspection_status != "ok":
                raise ValidationError("Hasil pemeriksaan belum sesuai spek.")
            rec.status = "done"

    def action_set_revision(self):
        self._ensure_status([
            "ecatalog_check",
            "negotiation_vendor",
            "negotiation_pp",
            "negotiation_done",
            "negotiation_minutes",
            "spk_preparation",
            "spk_process",
            "delivery",
            "inspection",
        ])
        for rec in self:
            rec.status = "revision"

    def action_set_addendum(self):
        self._ensure_status(["spk_process", "done"])
        for rec in self:
            rec.status = "addendum"

    def action_cancel(self):
        self._ensure_status([
            "draft",
            "ecatalog_check",
            "negotiation_vendor",
            "negotiation_pp",
            "negotiation_done",
            "negotiation_minutes",
            "spk_preparation",
            "spk_process",
            "delivery",
            "inspection",
            "revision",
            "addendum",
        ])
        for rec in self:
            rec.status = "cancelled"

    def action_reset_draft(self):
        self._ensure_status(["revision", "cancelled"])
        for rec in self:
            rec.status = "draft"
