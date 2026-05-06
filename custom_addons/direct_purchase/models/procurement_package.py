# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProcurementPackage(models.Model):
    _name = "direct_purchase.procurement_package"
    _description = "Procurement Package"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Nama Paket", required=True, tracking=True)

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
            ("vendor_offer", "Proses Penawaran Penyedia"),
            ("negotiation_vendor", "Proses Negosiasi (Penyedia)"),
            ("negotiation_officer", "Proses Negosiasi (PP)"),
            ("negotiation_done", "Negosiasi Selesai"),
            ("minutes_of_meeting", "Proses Berita Acara Negosiasi"),
            ("contract_addendum", "Addendum Kontrak"),
            ("contract_preparation", "Persiapan Kontrak"),
            ("contract_process", "Proses Kontrak"),
            ("contract_done", "Selesai Kontrak"),
            ("cancelled", "Batal"),
        ],
        string="Status Paket",
        default="draft",
        tracking=True,
    )

    contract_ids = fields.One2many(
        "direct_purchase.contract",
        "package_id",
        string="Kontrak",
    )

    contract_count = fields.Integer(compute="_compute_contract_count")

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.contract_ids)
