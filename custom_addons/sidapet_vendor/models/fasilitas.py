from odoo import models, fields


class SidapetFasilitas(models.Model):
	_name = 'sidapet.fasilitas'
	_description = 'Fasilitas'

	penyedia_id = fields.Many2one('sidapet.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
