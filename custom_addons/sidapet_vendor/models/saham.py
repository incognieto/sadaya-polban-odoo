from odoo import models, fields


class SidapetSaham(models.Model):
	_name = 'sidapet.saham'
	_description = 'Kepemilikan Saham'

	penyedia_id = fields.Many2one('sidapet.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
