from odoo import models, fields


class SadayaMitraRiwayatDpt(models.Model):
	_name = 'sadaya_mitra.riwayat.dpt'
	_description = 'Riwayat DPT'

	penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
