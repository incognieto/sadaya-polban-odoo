# from odoo import http


# class SiqutPolban(http.Controller):
#     @http.route('/siqut_polban/siqut_polban', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/siqut_polban/siqut_polban/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('siqut_polban.listing', {
#             'root': '/siqut_polban/siqut_polban',
#             'objects': http.request.env['siqut_polban.siqut_polban'].search([]),
#         })

#     @http.route('/siqut_polban/siqut_polban/objects/<model("siqut_polban.siqut_polban"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('siqut_polban.object', {
#             'object': obj
#         })

