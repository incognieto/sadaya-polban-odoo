from odoo import models, fields

class SIPlang(models.Model):
    _name = 'si_plang.si_plang'
    _description = 'SI-Plang'

    name = fields.Char(string='Nama')
    description = fields.Text(string='Deskripsi')