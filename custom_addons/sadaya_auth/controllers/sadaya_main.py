# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SadayaMainController(http.Controller):

    @http.route('/sadaya', type='http', auth='public', website=True)
    def sadaya_index(self, **kwargs):
        if request.env.user._is_public():
            return request.redirect('/sadaya/login')
        return request.redirect('/sadaya/dashboard')

    @http.route('/sadaya/profile', type='http', auth='user', website=True, sitemap=False)
    def sadaya_profile(self, **kwargs):
        user = request.env.user
        registration = request.env['sadaya.registration'].sudo().search(
            [('user_id', '=', user.id)], limit=1)
        return request.render('sadaya_auth.sadaya_profile', {
            'user': user,
            'registration': registration,
        })
