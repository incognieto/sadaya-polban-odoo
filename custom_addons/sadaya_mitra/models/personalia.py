from odoo import models, fields

class Personalia(models.Model):
    _name = 'sadaya_mitra.personalia'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)

    tipe_personalia = fields.Selection([
        ('ahli', 'Ahli'),
        ('pendukung', 'Pendukung')
    ])

    nama = fields.Char()
    nik = fields.Char()
    tempat_lahir = fields.Char()
    tanggal_lahir = fields.Date()
    jenjang_pendidikan = fields.Char()
    program_studi = fields.Char()
    posisi = fields.Char()

    scan_ktp = fields.Binary()
    scan_ijazah = fields.Binary()
    cv_tanggal = fields.Date()
