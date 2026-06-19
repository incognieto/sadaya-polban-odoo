from odoo import models, fields, api

class RancangRup(models.Model):
    _name = 'rancang.rup'
    _description = 'Rencana Umum Pengadaan (RUP)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama Paket', required=True, tracking=True)
    usulan_id = fields.Many2one('rancang.usulan', string='Dari Usulan Kebutuhan', required=True, readonly=True)
    unit_pengusul = fields.Char(string='Unit Pengusul', tracking=True)
    
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
            self.unit_pengusul = self.usulan_id.pemohon

    def action_sahkan_rup(self):
        paket_obj = self.env['sadaya_tawar.paket'].sudo()
        created_paket_ids = []

        jenis_map = {
            'barang': 'barang',
            'jasa_lainnya': 'jasa',
            'konstruksi': 'konstruksi',
            'konsultansi': 'konsultansi',
        }

        for record in self:
            if record.state != 'draft':
                continue

            total_hps = (
                sum(record.hps_ids.mapped('total_hps'))
                if record.hps_ids
                else record.nilai_pagu
            )

            deskripsi_lines = [
                f"Sumber Dana: {record.sumber_dana or '-'}",
                f"Kode Anggaran: {record.kode_anggaran or '-'}",
                f"Lokasi: {record.lokasi or '-'}",
                f"Tanggal Mulai: {record.tgl_mulai or '-'}",
                f"Tanggal Selesai: {record.tgl_selesai or '-'}",
            ]

            unit_pemohon = False
            if record.usulan_id:
                unit_pemohon = getattr(record.usulan_id, 'pemohon', False) or getattr(record.usulan_id, 'name', False)
                if unit_pemohon:
                    deskripsi_lines.insert(0, f"Unit Pemohon: {unit_pemohon}")

            # Penggabungan (Merge) dilakukan di blok ini
            paket = paket_obj.create({
                'name': record.name,
                'nilai_hps': total_hps,
                # Dari branch sadaya-tawar
                'jenis_pengadaan': jenis_map.get(record.jenis_pengadaan, 'barang'),
                'deskripsi': '\n'.join(deskripsi_lines),
                # Dari branch main
                'metode_pemilihan': record.metode_pemilihan or 'e_purchasing',
                'unit_pengusul': record.unit_pengusul or unit_pemohon,
                'tgl_mulai': record.tgl_mulai,
                'tgl_selesai': record.tgl_selesai,
                'state': 'draft',
            })

            created_paket_ids.append(paket.id)
            record.write({'state': 'active'})

        if not created_paket_ids:
            return True

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sadaya Tawar',
            'res_model': 'sadaya_tawar.paket',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_paket_ids)],
            'target': 'current',
        }
