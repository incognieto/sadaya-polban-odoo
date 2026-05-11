# from odoo import http


# class SiPlang(http.Controller):
#     @http.route('/si_plang/si_plang', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/si_plang/si_plang/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('si_plang.listing', {
#             'root': '/si_plang/si_plang',
#             'objects': http.request.env['si_plang.si_plang'].search([]),
#         })

#     @http.route('/si_plang/si_plang/objects/<model("si_plang.si_plang"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('si_plang.object', {
#             'object': obj
#         })

