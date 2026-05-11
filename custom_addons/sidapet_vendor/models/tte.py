from odoo import models, fields

class PengajuanTTE(models.Model):
    _name = 'sidapet.tte'

    penyedia_id = fields.Many2one('sidapet.penyedia', required=True)

    email = fields.Char()
    pin = fields.Char()
    surat_kuasa = fields.Binary()

    status_verifikasi = fields.Selection([
        ('draft', 'Draft'),
        ('verifikasi', 'Verifikasi'),
        ('aktif', 'Aktif')
    ])
