from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError  # Pastikan ini ditambahkan

class SadayaTawarPaket(models.Model):
    _name = 'sadaya_tawar.paket'
    _description = 'Paket Rencana Umum Pengadaan (RUP)'

    kode_paket = fields.Char(string='Kode Paket', readonly=True, copy=False, default=lambda self: '/')
    name = fields.Char(string='Nama Paket', required=True)
    nilai_hps = fields.Float(string='Nilai HPS (Rp)', required=True)
    
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
        self.ensure_one()
        
        if self.state not in ['published', 'eval']:
            raise UserError("Paket hanya dapat diteruskan ke modul eksekusi jika sudah dipublikasikan atau dievaluasi.")

        if self.nilai_hps < 50000000:
            model_name = 'sadaya_rutin.procurement_package'
            module_label = 'Sadaya Rutin'
            vals = {
                'name': self.name,
                'item_name': self.name,
                'procurement_type': 'goods',
                'amount_total': self.nilai_hps,
                'request_notes': self.deskripsi,
                'status': 'draft',
            }
        elif 50000000 <= self.nilai_hps <= 200000000:
            model_name = 'sadaya_langsung.paket'
            module_label = 'Sadaya Langsung'
            vals = {
                'name': self.name,
                'nilai_hps': self.nilai_hps,
                'keterangan': self.deskripsi,
                'dokumen_kak': self.dokumen_kak,
                'filename_kak': self.filename_kak, # Tambahan Wajib: Nama File KAK
                'dokumen_rab': self.dokumen_rab,
                'filename_rab': self.filename_rab, # Tambahan Wajib: Nama File RAB
                'status_paket': 'draft',
            }
        else:
            model_name = 'sadaya_lelang.paket'
            module_label = 'Sadaya Lelang'
            vals = {
                'name': self.name,
                'hps': self.nilai_hps,
                'description': self.deskripsi,
                'file_kebutuhan': self.dokumen_kak,
                'status': 'draft',
                'metode_pemilihan': 'tender',
            }

        try:
            target_model = self.env[model_name]
        except KeyError as exc:
            raise UserError(
                "Modul %s belum terpasang. Install modulnya terlebih dahulu sebelum routing." % module_label
            ) from exc

        target_model.sudo().create(vals)
        
        self.state = 'routed'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil Diteruskan!',
                'message': f'Paket "{self.name}" beserta dokumen terkait berhasil dikirim ke modul {module_label}.',
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