from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_sadaya_mitra_vendor = fields.Boolean(
        string="Vendor Terdaftar (Sadaya Mitra)", default=False, index=True
    )
    sadaya_mitra_penyedia_id = fields.Many2one(
        "sadaya_mitra.penyedia",
        string="Penyedia Sadaya Mitra",
        index=True,
        ondelete="set null",
    )
