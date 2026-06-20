# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SadayaMainController(http.Controller):

    @http.route('/sadaya', type='http', auth='public', website=True, sitemap=False)
    def sadaya_index(self, **kwargs):
        if request.env.user._is_public():
            return request.redirect('/sadaya/login')
        return request.redirect('/sadaya/dashboard')
