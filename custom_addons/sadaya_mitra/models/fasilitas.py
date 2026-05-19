from odoo import models, fields


class SadayaMitraFasilitas(models.Model):
	_name = 'sadaya_mitra.fasilitas'
	_description = 'Fasilitas'

	penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
