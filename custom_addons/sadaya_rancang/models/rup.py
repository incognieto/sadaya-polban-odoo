from odoo import models, fields, api

class RancangRup(models.Model):
    _name = 'rancang.rup'
    _description = 'Rencana Umum Pengadaan (RUP)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama Paket', required=True, tracking=True)
    usulan_id = fields.Many2one('rancang.usulan', string='Dari Usulan Kebutuhan', required=True, readonly=True)
    
    jenis_pengadaan = fields.Selection([
        ('barang', 'Barang'),
        ('jasa_lainnya', 'Jasa Lainnya'),
        ('konstruksi', 'Konstruksi'),
        ('konsultansi', 'Konsultansi')
    ], string='Jenis Pengadaan', required=True, tracking=True)
    
    metode_pemilihan = fields.Selection([
        ('epurchasing', 'E-Purchasing'),
        ('pengadaan_langsung', 'Pengadaan Langsung'),
        ('penunjukan_langsung', 'Penunjukan Langsung'),
        ('tender_cepat', 'Tender Cepat'),
        ('tender', 'Tender')
    ], string='Metode Pemilihan', tracking=True)
    
    sumber_dana = fields.Char(string='Sumber Dana', tracking=True)
    kode_anggaran = fields.Char(string='Kode Anggaran (MAK)', tracking=True)
    nilai_pagu = fields.Float(string='Nilai Pagu (RAB Usulan)', required=True, tracking=True)
    lokasi = fields.Char(string='Lokasi Pekerjaan', tracking=True)
    
    tgl_mulai = fields.Date(string='Perkiraan Tanggal Mulai')
    tgl_selesai = fields.Date(string='Perkiraan Tanggal Selesai')

    hps_ids = fields.One2many('rancang.hps', 'rup_id', string='Harga Perkiraan Sendiri (HPS)')
    dokumen_persiapan_ids = fields.Many2many('ir.attachment', string='Dokumen Persiapan')

    state = fields.Selection([
        ('draft', 'Draft (Persiapan)'),
        ('active', 'Aktif (Disahkan)')
    ], string='Status', default='draft', tracking=True)

    @api.onchange('usulan_id')
    def _onchange_usulan_id(self):
        if self.usulan_id:
            self.name = self.usulan_id.name
            self.jenis_pengadaan = self.usulan_id.jenis_kebutuhan
            self.nilai_pagu = self.usulan_id.rab

    def action_sahkan_rup(self):
        paket_obj = self.env['sadaya_tawar.paket'].sudo()
        created_paket_ids = []

        for record in self:
            if record.state != 'draft':
                continue

            # Jika ada HPS, pakai total HPS; jika tidak, pakai nilai pagu
            total_hps = sum(record.hps_ids.mapped('total_hps')) if record.hps_ids else record.nilai_pagu

            paket = paket_obj.create({
                'name': record.name,
                'nilai_hps': total_hps,
                'metode_pemilihan': record.metode_pemilihan or 'e_purchasing',
                'deskripsi': record.name or '',
                'state': 'draft',
            })

            created_paket_ids.append(paket.id)

            # Setelah sah, status RUP jadi aktif
            record.write({'state': 'active'})

        if not created_paket_ids:
            return True

        # Biar langsung terlihat setelah klik tombol
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sadaya Tawar',
            'res_model': 'sadaya_tawar.paket',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_paket_ids)],
            'target': 'current',
        }
