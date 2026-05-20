from odoo import models, fields


class SadayaMitraKantor(models.Model):
	_name = 'sadaya_mitra.kantor'
	_description = 'Kantor'

	penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
