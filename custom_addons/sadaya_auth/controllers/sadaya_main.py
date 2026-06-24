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

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def sadaya_home(self, **kwargs):
        return request.render('sadaya_auth.sadaya_homepage', {})

    @http.route('/about', type='http', auth='public', website=True, sitemap=True)
    def sadaya_about(self, **kwargs):
        return request.render('sadaya_auth.sadaya_about', {})

try:
    from odoo.addons.web.controllers.home import Home
except ImportError:
    Home = http.Controller

class SadayaHomeOverride(Home):
    @http.route('/web/login', type='http', auth="public", website=True, sitemap=False)
    def web_login(self, *args, **kw):
        return request.redirect('/sadaya/login')
