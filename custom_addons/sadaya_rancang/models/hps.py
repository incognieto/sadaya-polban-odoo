from odoo import models, fields, api

class RancangHps(models.Model):
    _name = 'rancang.hps'
    _description = 'Harga Perkiraan Sendiri (HPS)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Deskripsi HPS', required=True, tracking=True)
    rup_id = fields.Many2one('rancang.rup', string='Rencana Umum Pengadaan', required=True, ondelete='cascade')
    line_ids = fields.One2many('rancang.hps.line', 'hps_id', string='Rincian HPS')
    
    total_hps = fields.Float(string='Total HPS', compute='_compute_total_hps', store=True, tracking=True)

    tim_teknis_id = fields.Many2one('res.users', string='Tim Teknis (Delegasi)', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('delegated', 'Didelegasikan'),
        ('in_review', 'Dalam Review'),
        ('approved', 'Disetujui PPK')
    ], string='Status', default='draft', tracking=True)

    def action_delegate(self):
        self.state = 'delegated'

    def action_submit_laporan(self):
        self.state = 'in_review'
        
    def action_approve_hps(self):
        self.state = 'approved'

    @api.depends('line_ids.total')
    def _compute_total_hps(self):
        for record in self:
            record.total_hps = sum(line.total for line in record.line_ids)

class RancangHpsLine(models.Model):
    _name = 'rancang.hps.line'
    _description = 'Rincian Komponen HPS'

    hps_id = fields.Many2one('rancang.hps', string='HPS', required=True, ondelete='cascade')
    name = fields.Char(string='Uraian Barang/Jasa', required=True)
    satuan = fields.Char(string='Satuan', required=True)
    volume = fields.Float(string='Volume', required=True, default=1.0)
    harga_satuan = fields.Float(string='Harga Satuan', required=True)
    
    total = fields.Float(string='Total Harga', compute='_compute_total', store=True)

    @api.depends('volume', 'harga_satuan')
    def _compute_total(self):
        for line in self:
            line.total = line.volume * line.harga_satuan
