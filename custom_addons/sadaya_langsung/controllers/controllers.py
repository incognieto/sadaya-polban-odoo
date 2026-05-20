# from odoo import http


# class SadayaLangsung(http.Controller):
#     @http.route('/sadaya_langsung/sadaya_langsung', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sadaya_langsung/sadaya_langsung/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sadaya_langsung.listing', {
#             'root': '/sadaya_langsung/sadaya_langsung',
#             'objects': http.request.env['sadaya_langsung.sadaya_langsung'].search([]),
#         })

#     @http.route('/sadaya_langsung/sadaya_langsung/objects/<model("sadaya_langsung.sadaya_langsung"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sadaya_langsung.object', {
#             'object': obj
#         })

