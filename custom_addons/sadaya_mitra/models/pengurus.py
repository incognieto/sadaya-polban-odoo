from odoo import models, fields

class Pengurus(models.Model):
    _name = 'sadaya_mitra.pengurus'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')

    jabatan = fields.Selection([
        ('direksi', 'Direksi'),
        ('komisaris', 'Komisaris')
    ])

    nama_lengkap = fields.Char()
    nomor_hp = fields.Char()
    nik = fields.Char()
    scan_ktp = fields.Binary()
