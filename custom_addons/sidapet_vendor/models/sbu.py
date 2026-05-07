from odoo import models, fields

class SubklasifikasiSBU(models.Model):
    _name = 'sidapet.sbu'

    izin_id = fields.Many2one('sidapet.izin.usaha', required=True, ondelete='cascade')
    kode_subklasifikasi = fields.Char()
