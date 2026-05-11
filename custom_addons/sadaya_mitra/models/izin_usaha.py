from odoo import models, fields

class IzinUsaha(models.Model):
    _name = 'sadaya_mitra.izin.usaha'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')

    tipe_izin = fields.Selection([
        ('nib', 'NIB'),
        ('sbu', 'SBU'),
        ('lainnya', 'Lainnya')
    ])

    nomor_izin = fields.Char()
    scan_dokumen = fields.Binary()
    masa_berlaku = fields.Date()
