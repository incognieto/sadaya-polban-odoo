from odoo import models, fields, api


class si_plang(models.Model):
    _name = "si_plang.si_plang"
    _description = "si_plang.si_plang"

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends("value")
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
