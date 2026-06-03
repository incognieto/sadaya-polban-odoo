# pyrefly: ignore [missing-import]
from odoo import models, fields, api, exceptions

class RancangUsulan(models.Model):
    _name = 'rancang.usulan'
    _description = 'Usulan Kebutuhan Barang/Jasa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Judul Usulan', required=True, tracking=True)
    pemohon = fields.Char(string='Unit Kerja / Pemohon', required=True, tracking=True)
    jenis_kebutuhan = fields.Selection([
        ('barang', 'Barang'),
        ('jasa_lainnya', 'Jasa Lainnya'),
        ('konstruksi', 'Konstruksi'),
        ('konsultansi', 'Konsultansi')
    ], string='Jenis Kebutuhan', required=True, tracking=True)
    deskripsi_kebutuhan = fields.Text(string='Deskripsi Kebutuhan', tracking=True)
    rab = fields.Float(string='Anggaran (RAB)', required=True, tracking=True)
    kak = fields.Text(string='Kerangka Acuan Kerja (KAK)', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Lampiran Pendukung')
    
    klasifikasi = fields.Selection([
        ('operasional', 'Belanja Operasional Cepat'),
        ('non_tender', 'Nilai Dibawah Rp200 Juta (Non-Tender)'),
        ('tender', 'Nilai Diatas Rp200 Juta (Tender)')
    ], string='Klasifikasi Paket', compute='_compute_klasifikasi', store=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Menunggu Persetujuan'),
        ('returned', 'Dikembalikan (Revisi)'),
        ('rejected', 'Ditolak'),
        ('approved', 'Disetujui'),
        ('published', 'Dipublikasi ke RUP')
    ], string='Status', default='draft', tracking=True)

    @api.depends('rab')
    def _compute_klasifikasi(self):
        for record in self:
            if record.rab <= 50000000: # Contoh batas untuk operasional cepat (bisa disesuaikan)
                record.klasifikasi = 'operasional'
            elif record.rab <= 200000000:
                record.klasifikasi = 'non_tender'
            else:
                record.klasifikasi = 'tender'

    def action_submit(self):
        self.state = 'submitted'

    def action_approve(self):
        self.state = 'approved'

    def action_return(self):
        self.ensure_one()
        return {
            'name': 'Catatan Pengembalian (Revisi)',
            'type': 'ir.actions.act_window',
            'res_model': 'rancang.wizard.catatan',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_usulan_id': self.id,
                'default_action_type': 'returned',
            }
        }

    def action_reject(self):
        self.ensure_one()
        return {
            'name': 'Catatan Penolakan',
            'type': 'ir.actions.act_window',
            'res_model': 'rancang.wizard.catatan',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_usulan_id': self.id,
                'default_action_type': 'rejected',
            }
        }

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
