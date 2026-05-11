# from odoo import http


# class SadayaTawarPolban(http.Controller):
#     @http.route('/sadaya_tawar_polban/sadaya_tawar_polban', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sadaya_tawar_polban/sadaya_tawar_polban/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sadaya_tawar_polban.listing', {
#             'root': '/sadaya_tawar_polban/sadaya_tawar_polban',
#             'objects': http.request.env['sadaya_tawar_polban.sadaya_tawar_polban'].search([]),
#         })

#     @http.route('/sadaya_tawar_polban/sadaya_tawar_polban/objects/<model("sadaya_tawar_polban.sadaya_tawar_polban"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sadaya_tawar_polban.object', {
#             'object': obj
#         })

