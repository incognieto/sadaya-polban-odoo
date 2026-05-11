# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class TenderPortal(http.Controller):

    @http.route('/tenders', type='http', auth='public', website=True)
    def tender_list(self, **kwargs):
        tenders = request.env['sadaya_lelang.paket'].sudo().search([('status', '!=', 'draft')])
        return request.render('sadaya_lelang.portal_tender_list', {
            'tenders': tenders
        })

    @http.route(['/tenders/<model("sadaya_lelang.paket"):sadaya_lelang>'], type='http', auth='public', website=True)
    def tender_detail(self, sadaya_lelang, **kwargs):
        return request.render('sadaya_lelang.portal_tender_detail', {
            'sadaya_lelang': sadaya_lelang
        })

    @http.route('/my/tenders', type='http', auth='user', website=True)
    def my_tenders(self, **kwargs):
        partner = request.env.user.partner_id
        if not partner.is_vendor_tender:
            return request.render('sadaya_lelang.portal_vendor_registration', {
                'partner': partner
            })
            
        bids = request.env['sadaya_lelang.penawaran'].sudo().search([('vendor_id', '=', partner.id)])
        return request.render('sadaya_lelang.portal_my_tenders', {
            'bids': bids,
            'partner': partner
        })
