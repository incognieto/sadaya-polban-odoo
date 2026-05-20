from odoo import models, fields

class SadayaMitraPenyedia(models.Model):
    _name = 'sadaya_mitra.penyedia'
    _description = 'Penyedia / Vendor Sadaya Mitra'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    jenis_penyedia = fields.Selection([
        ('badan_usaha', 'Badan Usaha'),
        ('perorangan', 'Perorangan')
    ], required=True)

    nama_badan_usaha = fields.Char(required=True)
    email = fields.Char()
    nomor_telepon = fields.Char()
    nomor_whatsapp = fields.Char()
    narahubung = fields.Char()
    alamat = fields.Text()

    kualifikasi_usaha = fields.Char()
    scan_domisili = fields.Binary()
    masa_berlaku_domisili = fields.Date()

    # === field lama ===

    # 1:1
    landasan_hukum_id = fields.One2many('sadaya_mitra.landasan.hukum', 'penyedia_id')
    keuangan_id = fields.One2many('sadaya_mitra.keuangan', 'penyedia_id')
    pajak_id = fields.One2many('sadaya_mitra.pajak', 'penyedia_id')

    # 1:N
    pengurus_ids = fields.One2many('sadaya_mitra.pengurus', 'penyedia_id')
    izin_usaha_ids = fields.One2many('sadaya_mitra.izin.usaha', 'penyedia_id')
    sertifikat_perusahaan_ids = fields.One2many('sadaya_mitra.sertifikat.perusahaan', 'penyedia_id')
    saham_ids = fields.One2many('sadaya_mitra.saham', 'penyedia_id')
    personalia_ids = fields.One2many('sadaya_mitra.personalia', 'penyedia_id')
    kantor_ids = fields.One2many('sadaya_mitra.kantor', 'penyedia_id')
    fasilitas_ids = fields.One2many('sadaya_mitra.fasilitas', 'penyedia_id')
    pengalaman_perusahaan_ids = fields.One2many('sadaya_mitra.pengalaman.perusahaan', 'penyedia_id')
    pendaftaran_dpt_ids = fields.One2many('sadaya_mitra.pendaftaran.dpt', 'penyedia_id')
    tte_ids = fields.One2many('sadaya_mitra.tte', 'penyedia_id')