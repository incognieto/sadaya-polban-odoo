from odoo import models, fields

class PengajuanTTE(models.Model):
    _name = 'sadaya_mitra.tte'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)

    email = fields.Char()
    pin = fields.Char()
    surat_kuasa = fields.Binary()

    status_verifikasi = fields.Selection([
        ('draft', 'Draft'),
        ('verifikasi', 'Verifikasi'),
        ('aktif', 'Aktif')
    ])
