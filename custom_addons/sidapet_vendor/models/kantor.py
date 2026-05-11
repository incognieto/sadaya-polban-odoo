from odoo import models, fields


class SidapetKantor(models.Model):
	_name = 'sidapet.kantor'
	_description = 'Kantor'

	penyedia_id = fields.Many2one('sidapet.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
