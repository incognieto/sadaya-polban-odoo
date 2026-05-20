from odoo import http
from odoo.http import request


class SadayaController(http.Controller):

    @http.route('/sadaya', auth='public', website=True)
    def sadaya_home(self, **kw):
        return request.render('sadaya_auth.sadaya_homepage')

    @http.route('/sadaya/login', auth='public', website=True)
    def sadaya_login(self, **kw):
        return request.render('sadaya_auth.sadaya_login')

    @http.route('/sadaya/dashboard', auth='user', website=True)
    def sadaya_dashboard(self, **kw):
        return request.render('sadaya_auth.sadaya_dashboard')