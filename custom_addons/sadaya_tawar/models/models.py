from odoo import models, fields, api
from odoo.exceptions import ValidationError  # Pastikan ini ditambahkan

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
        return super(SadayaTawarPaket, self).create(vals_list)

    def action_publikasikan(self):
        for record in self:
            record.state = 'published'

    def action_route_paket(self):
        for record in self:
            record.state = 'routed'

    # =========================================================
    # BLOK VALIDASI LOGIKA METODE PEMILIHAN VS HPS
    # =========================================================

    @api.onchange('nilai_hps')
    def _onchange_nilai_hps(self):
        """ Logika Front-End: Otomatis mengubah dropdown saat user mengetik angka HPS """
        if self.nilai_hps > 0:
            if self.nilai_hps < 50000000:
                self.metode_pemilihan = 'e_purchasing'
            elif 50000000 <= self.nilai_hps <= 200000000:
                self.metode_pemilihan = 'pengadaan_langsung'
            elif self.nilai_hps > 200000000:
                self.metode_pemilihan = 'tender'

    @api.constrains('nilai_hps', 'metode_pemilihan')
    def _check_batasan_metode(self):
        """ Logika Back-End: Mencegah penyimpanan ke database jika input melanggar batasan """
        for record in self:
            # 1. Validasi E-Purchasing (< 50jt)
            if record.metode_pemilihan == 'e_purchasing' and record.nilai_hps >= 50000000:
                raise ValidationError("Aturan Sistem: Metode E-Purchasing hanya diizinkan untuk pengadaan dengan nilai HPS di bawah Rp 50.000.000.")
            
            # 2. Validasi Pengadaan Langsung (>= 50jt dan <= 200jt)
            elif record.metode_pemilihan == 'pengadaan_langsung' and (record.nilai_hps < 50000000 or record.nilai_hps > 200000000):
                raise ValidationError("Aturan Sistem: Metode Pengadaan Langsung harus berada di rentang nilai HPS Rp 50.000.000 hingga Rp 200.000.000.")
            
            # 3. Validasi Tender (> 200jt)
            elif record.metode_pemilihan == 'tender' and record.nilai_hps <= 200000000:
                raise ValidationError("Aturan Sistem: Metode Tender diwajibkan untuk pengadaan dengan nilai HPS di atas Rp 200.000.000.")