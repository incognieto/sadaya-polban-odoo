# pyrefly: ignore [missing-import]
from odoo import models, fields, api, exceptions

class RancangUsulan(models.Model):
    _name = 'rancang.usulan'
    _description = 'Usulan Kebutuhan Barang/Jasa'

    name = fields.Char(string='Judul Usulan', required=True)
    pemohon = fields.Char(string='Unit Kerja / Pemohon', required=True)
    rab = fields.Float(string='Anggaran (RAB)', required=True)
    kak = fields.Text(string='Kerangka Acuan Kerja (KAK)', required=True)
    klasifikasi = fields.Selection([
        ('operasional', 'Belanja Operasional Cepat'),
        ('non_tender', 'Nilai Dibawah Rp200 Juta (Non-Tender)'),
        ('tender', 'Nilai Diatas Rp200 Juta (Tender)')
    ], string='Klasifikasi Paket', compute='_compute_klasifikasi', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('published', 'Dipublikasi ke RUP')
    ], string='Status', default='draft')

    @api.depends('rab')
    def _compute_klasifikasi(self):
        for record in self:
            if record.rab <= 50000000: # Contoh batas untuk operasional cepat (bisa disesuaikan)
                record.klasifikasi = 'operasional'
            elif record.rab < 200000000:
                record.klasifikasi = 'non_tender'
            else:
                record.klasifikasi = 'tender'

    def action_submit(self):
        self.state = 'submitted'

    def action_approve(self):
        self.state = 'approved'

    def action_publish_rup(self):
        # Create record in sadaya-tawar (sadaya_tawar.paket)
        paket_obj = self.env['sadaya_tawar.paket']
        for record in self:
            if record.state == 'approved':
                paket_obj.create({
                    'name': record.name,
                    'nilai_hps': record.rab,
                    'state': 'draft',
                })
                record.state = 'published'
