from odoo import http
from odoo.http import request

class SadayaTawarPortal(http.Controller):

    # Membuat URL /sadaya_tawar/paket untuk melihat daftar pengumuman
    @http.route(['/sadaya_tawar/paket'], type='http', auth="public", website=True)
    def list_paket_tawar(self, **kwargs):
        # Hanya tarik paket yang statusnya 'published' (Pengumuman)
        pakets = request.env['sadaya_tawar.paket'].sudo().search([('state', '=', 'published')])
        return request.render('sadaya_tawar.portal_list_paket_template', {'pakets': pakets})

    # Membuat URL untuk melihat detail satu paket spesifik
    @http.route(['/sadaya_tawar/paket/<model("sadaya_tawar.paket"):paket>'], type='http', auth="public", website=True)
    def detail_paket_tawar(self, paket, **kwargs):
        return request.render('sadaya_tawar.portal_detail_paket_template', {'paket': paket})