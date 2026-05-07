from odoo import models, fields


class SidapetRiwayatDpt(models.Model):
	_name = 'sidapet.riwayat.dpt'
	_description = 'Riwayat DPT'

	penyedia_id = fields.Many2one('sidapet.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
