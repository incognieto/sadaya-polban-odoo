# -*- coding: utf-8 -*-

from odoo import fields, models


class Contract(models.Model):
    _name = "sadaya_rutin.contract"
    _description = "Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Nama Kontrak", required=True, tracking=True)

    package_id = fields.Many2one(
        "sadaya_rutin.procurement_package",
        string="Paket",
        ondelete="cascade",
        index=True,
        tracking=True,
    )

    procurement_type = fields.Selection(
        related="package_id.procurement_type",
        store=True,
        readonly=True,
    )

    officer_name = fields.Char(string="Pejabat Pembuat", tracking=True)
    vendor_name = fields.Char(string="Penyedia", tracking=True)

    hps_value = fields.Monetary(string="Nilai HPS", tracking=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
    )

    start_date = fields.Date(string="Tanggal Mulai", tracking=True)
    end_date = fields.Date(string="Tanggal Selesai", tracking=True)

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("preparation", "Persiapan Kontrak"),
            ("in_progress", "Proses Kontrak"),
            ("done", "Selesai Kontrak"),
            ("addendum", "Addendum Kontrak"),
        ],
        string="Status Kontrak",
        default="draft",
        tracking=True,
    )
