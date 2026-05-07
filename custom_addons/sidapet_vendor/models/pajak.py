from odoo import models, fields

class DataPajak(models.Model):
    _name = 'sidapet.pajak'

    penyedia_id = fields.Many2one('sidapet.penyedia', required=True)

    npwp = fields.Char()
    bukti_kswp = fields.Binary()
    bukti_spt = fields.Binary()
    bukti_bebas_pph23 = fields.Binary()
    bukti_pp23 = fields.Binary()
    bukti_non_pkp = fields.Binary()
