from odoo import fields, models


class VerifikasiWizard(models.TransientModel):
    _name = 'sadaya_mitra.verifikasi.wizard'
    _description = 'Wizard Verifikasi Penyedia'

    penyedia_id = fields.Many2one('sadaya_mitra.penyedia', string='Penyedia', required=True)
    action_type = fields.Selection([
        ('reject', 'Tolak'),
    ], string='Tindakan', required=True)
    catatan = fields.Text(string='Catatan', required=True, help='Jelaskan alasan penolakan')

    def action_confirm(self):
        if self.action_type == 'reject':
            self.penyedia_id.write({
                'status_verifikasi': 'rejected',
                'catatan_verifikasi': self.catatan,
                'tanggal_verifikasi': fields.Datetime.now(),
            })
