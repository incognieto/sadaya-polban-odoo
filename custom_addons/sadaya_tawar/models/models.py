from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError  # Pastikan ini ditambahkan

class SadayaTawarPaket(models.Model):
    _name = 'sadaya_tawar.paket'
    _description = 'Paket Rencana Umum Pengadaan (RUP)'

    kode_paket = fields.Char(string='Kode Paket', readonly=True, copy=False, default=lambda self: '/')
    name = fields.Char(string='Nama Paket', required=True)
    nilai_hps = fields.Float(string='Nilai HPS (Rp)', required=True)
    
    unit_pengusul = fields.Char(string='Unit Pengusul')
    tgl_mulai = fields.Date(string='Perkiraan Tanggal Mulai')
    tgl_selesai = fields.Date(string='Perkiraan Tanggal Selesai')

    
    # === TAMBAHAN PERSYARATAN VENDOR ===
    syarat_kbli = fields.Char(string='Persyaratan KBLI', help='Pisahkan dengan koma, contoh: 6201, 6202, 6203')
    syarat_dokumen = fields.Text(string='Dokumen yang Harus Disiapkan')

    jadwal_ids = fields.One2many(
        'sadaya_tawar.jadwal',
        'paket_id',
        string='Jadwal Tahapan Pengadaan'
    )

    jenis_kontrak = fields.Selection([
        ('lumsum', 'Lumsum'),
        ('harga_satuan', 'Harga Satuan'),
        ('gabungan', 'Gabungan')
    ], string='Jenis Kontrak', default='lumsum')

    metode_pemilihan = fields.Selection([
        ('e_purchasing', 'E-Purchasing'),
        ('pengadaan_langsung', 'Pengadaan Langsung'),
        ('tender', 'Tender')
    ], string='Metode Pemilihan', default='e_purchasing')

    jenis_pengadaan = fields.Selection([
        ('barang', 'Barang'),
        ('jasa', 'Jasa Lainnya'),
        ('konstruksi', 'Konstruksi'),
        ('konsultansi', 'Jasa Konsultansi')
    ], string='Jenis Pengadaan', default='barang', required=True)

    batas_pendaftaran = fields.Datetime(string='Batas Pendaftaran')

    peserta_ids = fields.One2many(
        'sadaya_tawar.peserta',
        'paket_id',
        string='Peserta Terdaftar'
    )
    addendum_ids = fields.One2many(
        'sadaya_tawar.addendum',
        'paket_id',
        string='Dokumen Addendum'
    )
    
    # === TAMBAHAN DOKUMEN PERSIAPAN PENGADAAN ===
    deskripsi = fields.Text(string='Deskripsi Singkat Paket')
    
    dokumen_kak = fields.Binary(string='Dokumen KAK', attachment=True)
    filename_kak = fields.Char(string='Nama File KAK')
    
    dokumen_spektek = fields.Binary(string='Spesifikasi Teknis', attachment=True)
    filename_spektek = fields.Char(string='Nama File Spektek')
    
    dokumen_rab = fields.Binary(string='Dokumen RAB/BoQ', attachment=True)
    filename_rab = fields.Char(string='Nama File RAB')
    # ============================================

    state = fields.Selection([
        ('draft', 'Draft RUP'),
        ('published', 'Pengumuman / Masa Penawaran'),
        ('eval', 'Evaluasi / Routing'),
        ('routed', 'Terkirim ke Eksekusi')
    ], string='Status', default='draft')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('kode_paket', '/') == '/':
                vals['kode_paket'] = self.env['ir.sequence'].next_by_code('sadaya.tawar.paket.seq') or '/'
                
            # [AUTO-FILL] Pastikan metode_pemilihan terisi otomatis saat dibuat dari modul Rancang
            if 'nilai_hps' in vals:
                hps = vals['nilai_hps']
                if hps < 50000000:
                    vals['metode_pemilihan'] = 'e_purchasing'
                elif 50000000 <= hps <= 200000000:
                    vals['metode_pemilihan'] = 'pengadaan_langsung'
                else:
                    vals['metode_pemilihan'] = 'tender'
                    
        return super(SadayaTawarPaket, self).create(vals_list)

    def write(self, vals):
        # [AUTO-FILL] Pastikan update HPS dari backend juga mengubah metode
        if 'nilai_hps' in vals:
            hps = vals['nilai_hps']
            if hps < 50000000:
                vals['metode_pemilihan'] = 'e_purchasing'
            elif 50000000 <= hps <= 200000000:
                vals['metode_pemilihan'] = 'pengadaan_langsung'
            else:
                vals['metode_pemilihan'] = 'tender'
        return super(SadayaTawarPaket, self).write(vals)

    def action_publikasikan(self):
        for record in self:
            record.state = 'published'

    def action_set_eval(self):
        for record in self:
            record.state = 'eval'

    def action_route_paket(self):
        for rec in self:
            # 1. Validasi Status
            if rec.state not in ['published', 'eval']:
                raise UserError("Paket hanya dapat diteruskan ke modul eksekusi jika sudah dipublikasikan atau dievaluasi.")

            # 2. Tarik Data Sumber RUP
            rup = self.env['rancang.rup'].sudo().search([
                ('name', '=', rec.name),
                ('nilai_pagu', '=', rec.nilai_hps),
            ], order='id desc', limit=1)

            if not rup:
                raise UserError(
                    f"Data sumber RUP tidak ditemukan untuk paket '{rec.name}'. "
                    "Pastikan paket ini berasal dari Sadaya Rancang."
                )

            unit_pemohon = False
            if rup.usulan_id:
                unit_pemohon = getattr(rup.usulan_id, 'pemohon', False) or getattr(rup.usulan_id, 'name', False)

            # 3. Mapping Kategori Pengadaan
            jenis_langsung_map = {
                'barang': 'barang',
                'jasa': 'jasa_lainnya',
                'konstruksi': 'konstruksi',
                'konsultansi': 'jasa_konsultansi',
            }
            jenis_rutin_map = {
                'barang': 'goods',
                'jasa': 'services',
                'konstruksi': 'construction',
                'konsultansi': 'consulting',
            }

            info_rup = (
                f"Unit Pemohon: {unit_pemohon or '-'}\n"
                f"Sumber Dana: {rup.sumber_dana or '-'}\n"
                f"Kode Anggaran: {rup.kode_anggaran or '-'}\n"
                f"Lokasi: {rup.lokasi or '-'}\n"
                f"Tanggal Mulai: {rup.tgl_mulai or '-'}\n"
                f"Tanggal Selesai: {rup.tgl_selesai or '-'}"
            )
            keterangan_gabungan = f"{rec.deskripsi or ''}\n\n{info_rup}".strip()

            # 4. Routing Berdasarkan Metode Pemilihan dgn Proteksi Modul
            try:
                if rec.metode_pemilihan == 'e_purchasing':
                    self.env['sadaya_rutin.procurement_package'].sudo().create({
                        'name': rec.name,
                        'item_name': rec.name,
                        'proposing_unit': unit_pemohon or rec.unit_pengusul,
                        'procurement_type': jenis_rutin_map.get(rec.jenis_pengadaan, 'goods'),
                        'amount_total': rec.nilai_hps,
                        'request_notes': keterangan_gabungan,
                        'start_date': rup.tgl_mulai or rec.tgl_mulai,
                        'end_date': rup.tgl_selesai or rec.tgl_selesai,
                        'status': 'draft',
                    })

                elif rec.metode_pemilihan == 'pengadaan_langsung':
                    self.env['sadaya_langsung.paket'].sudo().create({
                        'name': rec.name,
                        'unit_pengusul': unit_pemohon or rec.unit_pengusul,
                        'jenis_pengadaan': jenis_langsung_map.get(rec.jenis_pengadaan, 'barang'),
                        'nilai_hps': rec.nilai_hps,
                        'tanggal_mulai': rup.tgl_mulai or rec.tgl_mulai,
                        'tanggal_selesai': rup.tgl_selesai or rec.tgl_selesai,
                        'dokumen_kak': rec.dokumen_kak,
                        'filename_kak': rec.filename_kak,
                        'dokumen_rab': rec.dokumen_rab,
                        'filename_rab': rec.filename_rab,
                        'keterangan': keterangan_gabungan,
                        'status_paket': 'draft',
                    })

                elif rec.metode_pemilihan == 'tender':
                    self.env['sadaya_lelang.paket'].sudo().create({
                        'name': rec.name,
                        'hps': rec.nilai_hps,
                        'description': keterangan_gabungan,
                        'file_kebutuhan': rec.dokumen_kak,
                        'status': 'draft',
                        'metode_pemilihan': 'tender',
                    })
                else:
                    raise UserError("Metode pemilihan tidak dikenali atau belum disetting.")
                    
            except KeyError:
                raise UserError("Modul tujuan (Rutin/Langsung/Lelang) belum terpasang di sistem. Silakan install terlebih dahulu sebelum melakukan routing.")

            # Update status setelah routing berhasil
            rec.state = 'routed'

        # 5. Tampilkan Notifikasi Sukses (Dari branch sadaya-auth)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Routing Berhasil!',
                'message': 'Paket beserta dokumen terkait telah sukses dikirim ke modul eksekusi pengadaan.',
                'type': 'success',
                'sticky': False,
            }
        }
      
    # =========================================================
    # BLOK VALIDASI LOGIKA METODE PEMILIHAN VS HPS
    # =========================================================

    @api.onchange('nilai_hps')
    def _onchange_nilai_hps(self):
        """ Logika Front-End: Otomatis mengubah dropdown saat user mengetik angka HPS """
        if self.nilai_hps > 0:
            # Perhatikan: gunakan < bukan <=
            if self.nilai_hps < 50000000:
                self.metode_pemilihan = 'e_purchasing'
            elif 50000000 <= self.nilai_hps <= 200000000:
                self.metode_pemilihan = 'pengadaan_langsung'
            else:
                self.metode_pemilihan = 'tender'

    @api.constrains('nilai_hps', 'metode_pemilihan')
    def _check_batasan_metode(self):
        """ Logika Back-End: Mencegah penyimpanan ke database jika input melanggar batasan """
        for record in self:
            if record.metode_pemilihan == 'e_purchasing' and record.nilai_hps >= 50000000:
                raise ValidationError("Aturan Sistem: Metode E-Purchasing hanya diizinkan untuk pengadaan dengan nilai HPS di bawah Rp 50.000.000.")
            
            elif record.metode_pemilihan == 'pengadaan_langsung' and (record.nilai_hps < 50000000 or record.nilai_hps > 200000000):
                raise ValidationError("Aturan Sistem: Metode Pengadaan Langsung harus berada di rentang nilai HPS Rp 50.000.000 hingga Rp 200.000.000.")
            
            elif record.metode_pemilihan == 'tender' and record.nilai_hps <= 200000000:
                raise ValidationError("Aturan Sistem: Metode Tender diwajibkan untuk pengadaan dengan nilai HPS di atas Rp 200.000.000.")


class SadayaTawarPeserta(models.Model):
    _name = 'sadaya_tawar.peserta'
    _description = 'Pendaftaran Vendor'
    _order = 'tanggal_daftar desc'

    paket_id = fields.Many2one(
        'sadaya_tawar.paket',
        string='Paket',
        required=True,
        ondelete='cascade'
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
        domain="[('is_company', '=', True)]",
        index=True
    )
    tanggal_daftar = fields.Datetime(
        string='Tanggal Daftar',
        default=fields.Datetime.now,
        required=True
    )
    status = fields.Selection(
        [
            ('daftar', 'Terdaftar'),
            ('verifikasi', 'Verifikasi'),
            ('ditolak', 'Ditolak')
        ],
        string='Status',
        default='daftar'
    )
    catatan = fields.Text(string='Catatan')

    _sql_constraints = [
        (
            'unique_vendor_paket',
            'unique(paket_id, vendor_id)',
            'Vendor sudah terdaftar pada paket ini.'
        )
    ]


class SadayaTawarAddendum(models.Model):
    _name = 'sadaya_tawar.addendum'
    _description = 'Dokumen Addendum'
    _order = 'tanggal desc, id desc'

    paket_id = fields.Many2one(
        'sadaya_tawar.paket',
        string='Paket',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(string='Judul Addendum', required=True)
    tanggal = fields.Date(string='Tanggal Addendum', default=fields.Date.context_today)
    dokumen = fields.Binary(string='File Addendum (PDF)', required=True, attachment=True)
    dokumen_filename = fields.Char(string='Nama File')
    keterangan = fields.Text(string='Keterangan')

class SadayaTawarJadwal(models.Model):
    _name = 'sadaya_tawar.jadwal'
    _description = 'Jadwal Tahapan Pengadaan'
    _order = 'start_date asc'

    paket_id = fields.Many2one(
        'sadaya_tawar.paket', 
        string='Paket RUP', 
        required=True, 
        ondelete='cascade'
    )
    name = fields.Char(string='Nama Tahapan', required=True)
    start_date = fields.Datetime(string='Waktu Mulai', required=True)
    end_date = fields.Datetime(string='Waktu Selesai', required=True)