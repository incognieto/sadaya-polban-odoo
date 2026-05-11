from odoo import models, fields

class LandasanHukum(models.Model):
    _name = 'sidapet.landasan.hukum'

    penyedia_id = fields.Many2one('sidapet.penyedia', required=True, ondelete='cascade')

    nomor_akta = fields.Char()
    tanggal_akta = fields.Date()
    nama_notaris = fields.Char()
    nomor_pengesahan = fields.Char()
    tanggal_pengesahan = fields.Date()
    perubahan_akta = fields.Text()

    _sql_constraints = [
        ('unique_penyedia_landasan', 'unique(penyedia_id)',
         'Satu penyedia hanya boleh punya satu landasan hukum!')
    ]