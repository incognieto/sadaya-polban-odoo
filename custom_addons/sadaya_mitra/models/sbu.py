from odoo import models, fields

class SubklasifikasiSBU(models.Model):
    _name = 'sadaya_mitra.sbu'

    izin_id = fields.Many2one('sadaya_mitra.izin.usaha', required=True, ondelete='cascade')
    kode_subklasifikasi = fields.Char()
