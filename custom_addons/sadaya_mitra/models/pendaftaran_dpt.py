from odoo import models, fields

class PendaftaranDPT(models.Model):
    _name = 'sadaya_mitra.pendaftaran.dpt'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)
    kategori_id = fields.Many2one('sadaya_mitra.kategori.dpt', required=True)

    tanggal_daftar = fields.Datetime()

    status_proses = fields.Selection([
        ('pendaftaran', 'Pendaftaran'),
        ('verifikasi', 'Verifikasi'),
        ('perbaikan', 'Perbaikan'),
        ('evaluasi', 'Evaluasi'),
        ('pengumuman', 'Pengumuman')
    ])

    waktu_verifikasi = fields.Datetime()
    hasil_akhir = fields.Selection([
        ('terpilih', 'Terpilih'),
        ('tidak', 'Tidak')
    ])

    catatan_perbaikan = fields.Text()
