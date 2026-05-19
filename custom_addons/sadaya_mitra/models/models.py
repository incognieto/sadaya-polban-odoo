from odoo import fields, models


class SadayaMitraPenyedia(models.Model):
    _name = 'sadaya_mitra.penyedia'
    _description = 'Penyedia / Vendor SI-DAPET'
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
    password = fields.Char()

    kualifikasi_usaha = fields.Char()
    scan_domisili = fields.Binary()
    masa_berlaku_domisili = fields.Date()

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


class IzinUsaha(models.Model):
    _name = 'sadaya_mitra.izin.usaha'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')

    tipe_izin = fields.Selection([
        ('nib', 'NIB'),
        ('sbu', 'SBU'),
        ('lainnya', 'Lainnya')
    ])

    nomor_izin = fields.Char()
    scan_dokumen = fields.Binary()
    masa_berlaku = fields.Date()


class KBLI(models.Model):
    _name = 'sadaya_mitra.kbli'

    izin_id = fields.Many2one('sadaya_mitra.izin.usaha', required=True, ondelete='cascade')
    kode_kbli = fields.Char()


class KategoriDPT(models.Model):
    _name = 'sadaya_mitra.kategori.dpt'

    nama_kategori = fields.Char()
    metode = fields.Selection([
        ('undangan', 'Undangan'),
        ('pengumuman', 'Pengumuman')
    ])
    status_buka = fields.Boolean()


class DataKeuangan(models.Model):
    _name = 'sadaya_mitra.keuangan'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)

    nama_pemilik_rekening = fields.Char()
    nomor_rekening = fields.Char()
    kode_bank = fields.Char()
    nama_bank = fields.Char()

    scan_buku_rekening = fields.Binary()
    scan_laporan_keuangan = fields.Binary()
    masa_berlaku_laporan = fields.Date()

    scan_laporan_audited = fields.Binary()
    masa_berlaku_audited = fields.Date()

    _sql_constraints = [
        ('unique_penyedia_keuangan', 'unique(penyedia_id)',
         'Satu penyedia hanya boleh punya satu data keuangan!')
    ]


class DataPajak(models.Model):
    _name = 'sadaya_mitra.pajak'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)

    npwp = fields.Char()
    bukti_kswp = fields.Binary()
    bukti_spt = fields.Binary()
    bukti_bebas_pph23 = fields.Binary()
    bukti_pp23 = fields.Binary()
    bukti_non_pkp = fields.Binary()


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


class SadayaMitraPengalamanPerusahaan(models.Model):
    _name = 'sadaya_mitra.pengalaman.perusahaan'
    _description = 'Pengalaman Perusahaan'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


class PengalamanPersonalia(models.Model):
    _name = 'sadaya_mitra.pengalaman.personalia'

    personalia_id = fields.Many2one('sadaya_mitra.personalia', required=True)
    nama_pengalaman = fields.Char()
    upload_bukti = fields.Binary()


class Pengurus(models.Model):
    _name = 'sadaya_mitra.pengurus'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')

    jabatan = fields.Selection([
        ('direksi', 'Direksi'),
        ('komisaris', 'Komisaris')
    ])

    nama_lengkap = fields.Char()
    nomor_hp = fields.Char()
    nik = fields.Char()
    scan_ktp = fields.Binary()


class SubklasifikasiSBU(models.Model):
    _name = 'sadaya_mitra.sbu'

    izin_id = fields.Many2one('sadaya_mitra.izin.usaha', required=True, ondelete='cascade')
    kode_subklasifikasi = fields.Char()


class SadayaMitraSertifikatPerusahaan(models.Model):
    _name = 'sadaya_mitra.sertifikat.perusahaan'
    _description = 'Sertifikat Perusahaan'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


class SertifikatKeahlianPersonalia(models.Model):
    _name = 'sadaya_mitra.sertifikat.personalia'

    personalia_id = fields.Many2one('sadaya_mitra.personalia', required=True)
    judul = fields.Char()
    upload = fields.Binary()


class SadayaMitraRiwayatDpt(models.Model):
    _name = 'sadaya_mitra.riwayat.dpt'
    _description = 'Riwayat DPT'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


class SadayaMitraFasilitas(models.Model):
    _name = 'sadaya_mitra.fasilitas'
    _description = 'Fasilitas'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


class LandasanHukum(models.Model):
    _name = 'sadaya_mitra.landasan.hukum'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')

    nomor_akta = fields.Char()
    tanggal_akta = fields.Date()
    nama_notaris = fields.Char()
    nomor_pengesahan = fields.Char()
    tanggal_pengesahan = fields.Date()
    perubahan_akta = fields.Text()

    _sql_constraints = [
        ('unique_penyedia_landasan', 'unique(penyedia_id)',
         'Satu penyedia hanya boleh punya satu landasan hukum!')
    ]


class SadayaMitraSaham(models.Model):
    _name = 'sadaya_mitra.saham'
    _description = 'Kepemilikan Saham'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


class SadayaMitraKantor(models.Model):
    _name = 'sadaya_mitra.kantor'
    _description = 'Kantor'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


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


class PengajuanTTE(models.Model):
    _name = 'sadaya_mitra.tte'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)

    email = fields.Char()
    pin = fields.Char()
    surat_kuasa = fields.Binary()

    status_verifikasi = fields.Selection([
        ('draft', 'Draft'),
        ('verifikasi', 'Verifikasi'),
        ('aktif', 'Aktif')
    ])
