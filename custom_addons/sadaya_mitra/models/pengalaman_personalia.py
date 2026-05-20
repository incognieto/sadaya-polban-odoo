from odoo import models, fields

class PengalamanPersonalia(models.Model):
    _name = 'sadaya_mitra.pengalaman.personalia'

    personalia_id = fields.Many2one('sadaya_mitra.personalia', required=True)
    nama_pengalaman = fields.Char()
    upload_bukti = fields.Binary()
