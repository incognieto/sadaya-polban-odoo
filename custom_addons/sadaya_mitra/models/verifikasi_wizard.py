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
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning(f"--- WIZARD ACTION CONFIRM CALLED ---")
        _logger.warning(f"penyedia_id: {self.penyedia_id}, action_type: {self.action_type}, catatan: {self.catatan}")
        if self.action_type == 'reject':
            self.penyedia_id.write({
                'status_verifikasi': 'rejected',
                'catatan_verifikasi': self.catatan,
                'tanggal_verifikasi': fields.Datetime.now(),
            })
            _logger.warning(f"Successfully rejected!")
        else:
            _logger.warning(f"action_type is not 'reject', it is {self.action_type}")
            
        return {'type': 'ir.actions.client', 'tag': 'reload'}
