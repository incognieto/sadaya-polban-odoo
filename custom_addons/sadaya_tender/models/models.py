from odoo import models, fields, api


class sadaya_tender(models.Model):
    _name = 'sadaya_tender.sadaya_tender'
    _description = 'sadaya_tender.sadaya_tender'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

