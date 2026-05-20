from odoo import models, fields


class SadayaMitraSertifikatPerusahaan(models.Model):
	_name = 'sadaya_mitra.sertifikat.perusahaan'
	_description = 'Sertifikat Perusahaan'

	penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
	name = fields.Char()
