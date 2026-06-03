# pyrefly: ignore [missing-import]
from odoo import models, fields, api, exceptions

class RancangUsulan(models.Model):
    _name = 'rancang.usulan'
    _description = 'Usulan Kebutuhan Barang/Jasa'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    def _compute_access_url(self):
        super(RancangUsulan, self)._compute_access_url()
        for record in self:
            record.access_url = f'/sadaya_rancang/pengajuan/{record.id}'

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
    kak = fields.Binary(string='Kerangka Acuan Kerja (KAK)', required=True, attachment=True)
    kak_filename = fields.Char(string='Nama File KAK')
    attachment_ids = fields.Many2many('ir.attachment', string='Dokumen Pendukung', tracking=True)
    
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

    @api.constrains('kak_filename')
    def _check_kak_extension(self):
        for record in self:
            if record.kak_filename and not record.kak_filename.lower().endswith('.pdf'):
                raise exceptions.ValidationError("File KAK harus berformat .pdf!")

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
        # Create record in rancang.rup
        rup_obj = self.env['rancang.rup']
        for record in self:
            if record.state == 'approved':
                rup_obj.create({
                    'name': record.name,
                    'usulan_id': record.id,
                    'jenis_pengadaan': record.jenis_kebutuhan,
                    'nilai_pagu': record.rab,
                    'state': 'draft',
                })
                record.state = 'published'

    def action_draft(self):
        self.state = 'draft'

    def action_delete(self):
        self.ensure_one()
        self.unlink()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pengajuan Kebutuhan',
            'res_model': 'rancang.usulan',
            'view_mode': 'list,form',
            'target': 'current'
        }
