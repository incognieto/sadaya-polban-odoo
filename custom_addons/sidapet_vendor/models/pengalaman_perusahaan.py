from odoo import models, fields


class SidapetPengalamanPerusahaan(models.Model):
	_name = 'sidapet.pengalaman.perusahaan'
	_description = 'Pengalaman Perusahaan'

	penyedia_id = fields.Many2one('sidapet.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
