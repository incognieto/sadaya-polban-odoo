import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SadayaMitraPenyedia(models.Model):
    _name = "sadaya_mitra.penyedia"
    _description = "Penyedia / Vendor Sadaya Mitra"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner (Odoo)",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="Partner Odoo yang dibuat otomatis untuk penyedia ini.",
    )

    jenis_penyedia = fields.Selection(
        [("badan_usaha", "Badan Usaha"), ("perorangan", "Perorangan")], required=True
    )

    nama_badan_usaha = fields.Char(required=True)
    email = fields.Char()
    nomor_telepon = fields.Char()
    nomor_whatsapp = fields.Char()
    narahubung = fields.Char()
    alamat = fields.Text()

    kualifikasi_usaha = fields.Char()
    scan_domisili = fields.Binary()
    masa_berlaku_domisili = fields.Date()

    # === field lama ===

    # 1:1
    landasan_hukum_id = fields.One2many("sadaya_mitra.landasan.hukum", "penyedia_id")
    keuangan_id = fields.One2many("sadaya_mitra.keuangan", "penyedia_id")
    pajak_id = fields.One2many("sadaya_mitra.pajak", "penyedia_id")

    # 1:N
    pengurus_ids = fields.One2many("sadaya_mitra.pengurus", "penyedia_id")
    izin_usaha_ids = fields.One2many("sadaya_mitra.izin.usaha", "penyedia_id")
    sertifikat_perusahaan_ids = fields.One2many(
        "sadaya_mitra.sertifikat.perusahaan", "penyedia_id"
    )
    saham_ids = fields.One2many("sadaya_mitra.saham", "penyedia_id")
    personalia_ids = fields.One2many("sadaya_mitra.personalia", "penyedia_id")
    kantor_ids = fields.One2many("sadaya_mitra.kantor", "penyedia_id")
    fasilitas_ids = fields.One2many("sadaya_mitra.fasilitas", "penyedia_id")
    pengalaman_perusahaan_ids = fields.One2many(
        "sadaya_mitra.pengalaman.perusahaan", "penyedia_id"
    )
    pendaftaran_dpt_ids = fields.One2many("sadaya_mitra.pendaftaran.dpt", "penyedia_id")
    tte_ids = fields.One2many("sadaya_mitra.tte", "penyedia_id")

    def _prepare_partner_vals(self, vals=None):
        vals = vals or {}
        name = vals.get("nama_badan_usaha") or self.nama_badan_usaha
        email = vals.get("email") if "email" in vals else self.email
        phone = (
            vals.get("nomor_telepon") if "nomor_telepon" in vals else self.nomor_telepon
        )
        street = vals.get("alamat") if "alamat" in vals else self.alamat
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "street": street,
            "is_sadaya_mitra_vendor": True,
        }

    def _ensure_partner_exists(self, vals=None):
        for rec in self:
            if rec.partner_id:
                continue
            partner_vals = rec._prepare_partner_vals(vals)
            partner_vals["sadaya_mitra_penyedia_id"] = rec.id
            partner = rec.env["res.partner"].sudo().create(partner_vals)
            rec.sudo().write({"partner_id": partner.id})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list):
            rec._ensure_partner_exists(vals)
        return records

    def write(self, vals):
        res = super().write(vals)
        self.filtered(lambda r: not r.partner_id)._ensure_partner_exists(vals)
        sync_fields = {
            "nama_badan_usaha",
            "email",
            "nomor_telepon",
            "nomor_whatsapp",
            "alamat",
        }
        if sync_fields.intersection(vals.keys()):
            for rec in self.filtered("partner_id"):
                rec.partner_id.sudo().write(rec._prepare_partner_vals(vals))
        return res

    def _register_hook(self):
        res = super()._register_hook()
        try:
            missing = (
                self.env["sadaya_mitra.penyedia"]
                .sudo()
                .search([("partner_id", "=", False)])
            )
            if missing:
                missing._ensure_partner_exists()
        except Exception:
            _logger.exception("Failed to backfill partner_id for sadaya_mitra.penyedia")
        return res
