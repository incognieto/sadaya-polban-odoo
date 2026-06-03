from odoo import models, fields, api

class WizardCatatan(models.TransientModel):
    _name = 'rancang.wizard.catatan'
    _description = 'Wizard Catatan Penolakan / Revisi'

    usulan_id = fields.Many2one('rancang.usulan', string='Usulan', required=True)
    action_type = fields.Selection([
        ('returned', 'Kembalikan (Revisi)'),
        ('rejected', 'Tolak')
    ], string='Tindakan', required=True)
    catatan = fields.Text(string='Catatan', required=True)

    def action_confirm(self):
        self.ensure_one()
        # Ubah status usulan
        self.usulan_id.write({'state': self.action_type})
        
        # Tambahkan catatan ke chatter (log note)
        pesan = "<b>Usulan %s</b><br/>Alasan/Catatan: %s" % (
            dict(self._fields['action_type'].selection).get(self.action_type),
            self.catatan
        )
        self.usulan_id.message_post(body=pesan)
        return {'type': 'ir.actions.act_window_close'}
