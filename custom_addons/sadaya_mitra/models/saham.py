from odoo import models, fields


class SadayaMitraSaham(models.Model):
	_name = 'sadaya_mitra.saham'
	_description = 'Kepemilikan Saham'

	penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
