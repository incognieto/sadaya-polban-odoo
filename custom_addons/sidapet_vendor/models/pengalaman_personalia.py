from odoo import models, fields

class PengalamanPersonalia(models.Model):
    _name = 'sidapet.pengalaman.personalia'

    personalia_id = fields.Many2one('sidapet.personalia', required=True)
    nama_pengalaman = fields.Char()
    upload_bukti = fields.Binary()
