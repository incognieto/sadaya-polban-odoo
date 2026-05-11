from odoo import models, fields


class SidapetSertifikatPerusahaan(models.Model):
	_name = 'sidapet.sertifikat.perusahaan'
	_description = 'Sertifikat Perusahaan'

	penyedia_id = fields.Many2one('sidapet.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
