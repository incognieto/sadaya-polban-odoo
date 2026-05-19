from odoo import models, fields

class KBLI(models.Model):
    _name = 'sadaya_mitra.kbli'

    izin_id = fields.Many2one('sadaya_mitra.izin.usaha', required=True, ondelete='cascade')
    kode_kbli = fields.Char()
