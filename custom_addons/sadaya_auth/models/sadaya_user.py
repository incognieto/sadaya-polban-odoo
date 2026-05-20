# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResUsersSadaya(models.Model):
    """
    Extend res.users dengan field tambahan Sadaya
    """
    _inherit = 'res.users'

    sadaya_tipe = fields.Selection([
        ('badan_usaha', 'Badan Usaha'),
        ('perorangan', 'Perorangan'),
    ], string='Tipe Akun Sadaya', default='perorangan')

    sadaya_registration_id = fields.Many2one(
        'sadaya.registration',
        string='Data Registrasi Sadaya',
        readonly=True
    )

    sadaya_verified = fields.Boolean(
        string='Terverifikasi Sadaya',
        default=False
    )
