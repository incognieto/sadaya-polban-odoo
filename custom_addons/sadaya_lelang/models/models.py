from odoo import models, fields, api


class sadaya_lelang(models.Model):
    _name = 'sadaya_lelang.sadaya_lelang'
    _description = 'sadaya_lelang.sadaya_lelang'

    kode = fields.Char(string="Kode SadayaLelang")
    nama = fields.Char(string="Nama SadayaLelang")
    tahap = fields.Char(string="Tahap SadayaLelang")
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

