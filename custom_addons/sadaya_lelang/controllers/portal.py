# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class TenderPortal(http.Controller):

    @http.route('/tender-portal/tenders', type='http', auth='public', website=False)
    def tender_list(self, **kwargs):
        tenders = request.env['sadaya_lelang.paket'].sudo().search([('status', '!=', 'persiapan_lelang')])
        return request.render('sadaya_lelang.portal_tender_list', {
            'tenders': tenders
        })

    @http.route(['/tenders/<model("sadaya_lelang.paket"):tender>'], type='http', auth='public', website=False)
    def tender_detail(self, tender, **kwargs):
        return request.render('sadaya_lelang.portal_tender_detail', {
            'tender': tender
        })

    @http.route('/tender-portal/dashboard', type='http', auth='user', website=False)
    def my_tenders(self, **kwargs):
        partner = request.env.user.partner_id
        if not partner.is_vendor_tender:
            # We don't have portal_vendor_registration yet, just fallback or create it
            return request.redirect('/my')
            
        bids = request.env['sadaya_lelang.penawaran'].sudo().search([('vendor_id', '=', partner.id)])
        return request.render('sadaya_lelang.portal_my_tenders', {
            'bids': bids,
            'partner': partner
        })
