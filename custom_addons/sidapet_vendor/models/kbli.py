from odoo import models, fields

class KBLI(models.Model):
    _name = 'sidapet.kbli'

    izin_id = fields.Many2one('sidapet.izin.usaha', required=True, ondelete='cascade')
    kode_kbli = fields.Char()
