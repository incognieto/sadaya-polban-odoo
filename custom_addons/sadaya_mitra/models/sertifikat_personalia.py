from odoo import models, fields

class SertifikatKeahlianPersonalia(models.Model):
    _name = 'sadaya_mitra.sertifikat.personalia'

    personalia_id = fields.Many2one('sadaya_mitra.personalia', required=True)
    judul = fields.Char()
    upload = fields.Binary()
