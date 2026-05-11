from odoo import models, fields, api

class SadayaTawarPaket(models.Model):
    _name = 'sadaya_tawar.paket'
    _description = 'Paket Rencana Umum Pengadaan (RUP)'

    name = fields.Char(string='Nama Paket', required=True)
    nilai_hps = fields.Float(string='Nilai HPS (Rp)', required=True)
    jenis_kontrak = fields.Selection([
        ('lumsum', 'Lumsum'),
        ('harga_satuan', 'Harga Satuan')
    ], string='Jenis Kontrak', default='lumsum')
    
    # Status alur paket pengadaan
    state = fields.Selection([
        ('draft', 'Draft RUP'),
        ('published', 'Pengumuman / Masa Penawaran'),
        ('eval', 'Evaluasi / Routing'),
        ('routed', 'Terkirim ke Eksekusi')
    ], string='Status', default='draft')

    def action_route_paket(self):
        for record in self:
            if record.nilai_hps <= 50000000:
                # Ke Sadaya Rutin
                self.env['sadaya_rutin.procurement_package'].sudo().create({
                    'name': record.name,
                    'procurement_type': 'goods',
                    'status': 'draft',
                })
            elif record.nilai_hps < 200000000:
                # Ke Sadaya Langsung
                self.env['sadaya_langsung.paket'].sudo().create({
                    'name': record.name,
                    'nilai_hps': record.nilai_hps,
                    'status_paket': 'draft',
                    'jenis_pengadaan': 'barang',
                })
            else:
                # Ke Sadaya Lelang
                self.env['sadaya_lelang.paket'].sudo().create({
                    'name': record.name,
                    'hps': record.nilai_hps,
                    'status': 'draft',
                    'metode_pemilihan': 'sadaya_lelang',
                })
            record.state = 'routed'

class SadayaTawarPenawaran(models.Model):
    _name = 'sadaya_tawar.penawaran'
    _description = 'Dokumen Penawaran Vendor'

    # Relasi: 1 Paket bisa punya banyak Penawaran dari berbagai vendor
    paket_id = fields.Many2one('sadaya_tawar.paket', string='Paket Pengadaan', required=True)
    vendor_name = fields.Char(string='Nama Vendor', required=True)
    harga_penawaran = fields.Float(string='Harga Penawaran Final (Rp)', required=True)