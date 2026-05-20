from odoo import models, fields

class KategoriDPT(models.Model):
    _name = 'sadaya_mitra.kategori.dpt'

    nama_kategori = fields.Char()
    metode = fields.Selection([
        ('undangan', 'Undangan'),
        ('pengumuman', 'Pengumuman')
    ])
    status_buka = fields.Boolean()
