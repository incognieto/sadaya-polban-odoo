from odoo import models, fields

class SertifikatKeahlianPersonalia(models.Model):
    _name = 'sidapet.sertifikat.personalia'

    personalia_id = fields.Many2one('sidapet.personalia', required=True)
    judul = fields.Char()
    upload = fields.Binary()
