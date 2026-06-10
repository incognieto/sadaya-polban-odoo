import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SadayaMitraPenyedia(models.Model):
    _name = 'sadaya_mitra.penyedia'
    _description = 'Penyedia / Vendor SI-DAPET'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='set null', index=True
    )
    jenis_penyedia = fields.Selection([
        ('badan_usaha', 'Badan Usaha'),
        ('perorangan', 'Perorangan')
    ], required=True)

    nama_badan_usaha = fields.Char(required=True)
    email = fields.Char()
    nomor_telepon = fields.Char()
    nomor_whatsapp = fields.Char()
    narahubung = fields.Char()
    nomor_nik_narahubung = fields.Char()
    alamat = fields.Text()
    kata_sandi = fields.Char()
    swafoto_narahubung = fields.Binary()
    nomor_npwp_perusahaan = fields.Char()
    bukti_npwp = fields.Binary()
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


    status_verifikasi = fields.Selection([
        ('draft', 'Menunggu Verifikasi'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ], string='Status Verifikasi', default='draft', tracking=True)

    catatan_verifikasi = fields.Text(string='Catatan Verifikasi')
    tanggal_verifikasi = fields.Datetime(string='Tanggal Verifikasi')

    data_lengkap_count = fields.Char(
        string='Kelengkapan Data', compute='_compute_data_lengkap'
    )

    def _compute_data_lengkap(self):
        for record in self:
            checklist = {
                'landasan_hukum': bool(record.landasan_hukum_id),
                'pengurus': bool(record.pengurus_ids),
                'izin_usaha': bool(record.izin_usaha_ids),
                'sertifikat_perusahaan': bool(record.sertifikat_perusahaan_ids),
                'saham': bool(record.saham_ids),
                'personalia': bool(record.personalia_ids),
                'kantor': bool(record.kantor_ids),
                'fasilitas': bool(record.fasilitas_ids),
                'pengalaman_perusahaan': bool(record.pengalaman_perusahaan_ids),
                'keuangan': bool(record.keuangan_id),
                'pajak': bool(record.pajak_id),
                'pendaftaran_dpt': bool(record.pendaftaran_dpt_ids),
                'tte': bool(record.tte_ids),
            }
            total = len(checklist)
            completed = sum(1 for v in checklist.values() if v)
            record.data_lengkap_count = f"{completed}/{total}"

    def action_approve(self):
        self.write({
            'status_verifikasi': 'approved',
            'tanggal_verifikasi': fields.Datetime.now(),
        })

    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sadaya_mitra.verifikasi.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_penyedia_id': self.id,
                'action_type': 'reject',
            }
        }

    def _ensure_partner_exists(self, vals=None):
        for rec in self:
            if rec.partner_id:
                continue

            partner_vals = rec._prepare_partner_vals(vals)
            partner_vals["sadaya_mitra_penyedia_id"] = rec.id
            partner = rec.env["res.partner"].sudo().create(partner_vals)
            rec.sudo().write({"partner_id": partner.id})

    def _prepare_partner_vals(self, vals=None):
        self.ensure_one()
        vals = vals or {}

        jenis_penyedia = vals.get("jenis_penyedia") or self.jenis_penyedia
        return {
            "name": vals.get("nama_badan_usaha")
            or self.nama_badan_usaha
            or self.narahubung
            or "Penyedia",
            "email": vals.get("email") or self.email,
            "phone": vals.get("nomor_telepon") or self.nomor_telepon,
            # "mobile": vals.get("nomor_whatsapp") or self.nomor_whatsapp,
            "street": vals.get("alamat") or self.alamat,
            "is_company": jenis_penyedia == "badan_usaha",
            "is_sadaya_mitra_vendor": True,
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list):
            rec._ensure_partner_exists(vals)
        return records

    def write(self, vals):
        res = super().write(vals)

        # kalau ada record penyedia yang belum punya partner, buatkan
        self.filtered(lambda r: not r.partner_id)._ensure_partner_exists(vals)

        # sync bila ada perubahan field yang relevan
        sync_fields = {"nama_badan_usaha", "email", "nomor_telepon", "alamat"}
        if sync_fields.intersection(vals.keys()):
            for rec in self.filtered("partner_id"):
                rec.partner_id.sudo().write(rec._prepare_partner_vals(vals))

        return res

    def _register_hook(self):
        res = super()._register_hook()
        try:
            with self.env.cr.savepoint():
                missing = (
                    self.env["sadaya_mitra.penyedia"]
                    .sudo()
                    .search([("partner_id", "=", False)])
                )
                if missing:
                    missing._ensure_partner_exists()
        except Exception:
            _logger.exception("Failed to backfill partner_id for sadaya_mitra.penyedia")
        return res

    def action_reset(self):
        self.write({
            'status_verifikasi': 'draft',
            'catatan_verifikasi': '',
            'tanggal_verifikasi': False,
        })


class IzinUsaha(models.Model):
    _name = 'sadaya_mitra.izin.usaha'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')

    tipe_izin = fields.Selection([
        ('nib', 'NIB'),
        ('sbu', 'SBU'),
        ('lainnya', 'Lainnya')
    ])

    nama_izin = fields.Char()
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

    tenaga_ahli = fields.Char()
    nik = fields.Char()
    tempat_lahir = fields.Char()
    tanggal_lahir = fields.Date()
    jenjang_pendidikan = fields.Char()
    program_studi = fields.Char()
    posisi = fields.Char()

    scan_ktp = fields.Binary()
    scan_ijazah = fields.Binary()
    cv_pdf = fields.Binary()
    cv_tanggal = fields.Date()
    pengalaman_ids = fields.One2many('sadaya_mitra.pengalaman.personalia', 'personalia_id')
    sertifikat_ids = fields.One2many('sadaya_mitra.sertifikat.personalia', 'personalia_id')
    
    # Fields moved from Pengalaman Personalia
    pengalaman = fields.Char()
    bukti_pengalaman = fields.Binary()

    # Fields moved from Sertifikat Personalia
    nama_sertifikat = fields.Char()
    bukti_sertifikat = fields.Binary()


class SadayaMitraPengalamanPerusahaan(models.Model):
    _name = 'sadaya_mitra.pengalaman.perusahaan'
    _description = 'Pengalaman Perusahaan'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


class PengalamanPersonalia(models.Model):
    _name = 'sadaya_mitra.pengalaman.personalia'

    personalia_id = fields.Many2one('sadaya_mitra.personalia', required=True)
    pengalaman = fields.Char()
    bukti_pengalaman = fields.Binary()


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
    nama_sertifikat = fields.Char()
    bukti_sertifikat = fields.Binary()


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
    _name = "sadaya_mitra.landasan.hukum"
    _description = "Landasan Hukum"

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')

    nomor_akta = fields.Char()
    tanggal_akta = fields.Date()
    nama_notaris = fields.Char()
    nomor_pengesahan = fields.Char()
    tanggal_pengesahan = fields.Date()
    perubahan_akta = fields.Text()
    scan_bukti = fields.Binary()

    _sql_constraints = [
        ('unique_penyedia_landasan', 'unique(penyedia_id)',
         'Satu penyedia hanya boleh punya satu landasan hukum!')
    ]


class SadayaMitraSaham(models.Model):
    _name = 'sadaya_mitra.saham'
    _description = 'Kepemilikan Saham'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    susunan = fields.Char()
    nik = fields.Char()
    posisi = fields.Char()


class SadayaMitraKantor(models.Model):
    _name = 'sadaya_mitra.kantor'
    _description = 'Kantor'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True, ondelete='cascade')
    name = fields.Char()


class PendaftaranDPT(models.Model):
    _name = "sadaya_mitra.pendaftaran.dpt"
    _description = "Pendaftaran DPT"

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)
    kategori_id = fields.Selection([
        ('barang', 'Barang'),
        ('jasa', 'Jasa'),
        ('pekerjaan_konstruksi', 'Pekerjaan Konstruksi'),
        ('jasa_konsultasi', 'Jasa Konsultasi'),
        ('barang_printil', 'Barang Printil'),
        ('jasa_lainnya', 'Jasa Lainnya'),
    ], string='Kategori DPT', required=True)

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

    def _auto_init(self):
        """Handle schema migration: drop the old foreign key constraint if it exists."""
        cr = self.env.cr
        # Drop the old foreign key constraint if it exists.
        try:
            with cr.savepoint():
                cr.execute("""
                    ALTER TABLE sadaya_mitra_pendaftaran_dpt
                    DROP CONSTRAINT IF EXISTS sadaya_mitra_pendaftaran_dpt_kategori_id_fkey
                """)
        except Exception:
            _logger.exception("Failed to drop old kategori_id foreign key")
        return super()._auto_init()


class PengajuanTTE(models.Model):
    _name = "sadaya_mitra.tte"
    _description = "Pengajuan TTE"

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', required=True)

    email = fields.Char()
    pin = fields.Char()
    surat_kuasa = fields.Binary()

    status_verifikasi = fields.Selection([
        ('draft', 'Draft'),
        ('verifikasi', 'Verifikasi'),
        ('aktif', 'Aktif')
    ])
