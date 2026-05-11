from odoo import models, fields

class PendaftaranDPT(models.Model):
    _name = 'sidapet.pendaftaran.dpt'

    penyedia_id = fields.Many2one('sidapet.penyedia', required=True)
    kategori_id = fields.Many2one('sidapet.kategori.dpt', required=True)

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
