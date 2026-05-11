from odoo import models, fields


class SadayaMitraPengalamanPerusahaan(models.Model):
	_name = 'sadaya_mitra.pengalaman.perusahaan'
	_description = 'Pengalaman Perusahaan'

	penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
