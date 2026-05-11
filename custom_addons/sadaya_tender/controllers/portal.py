# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class TenderPortal(http.Controller):

    @http.route('/tenders', type='http', auth='public', website=True)
    def tender_list(self, **kwargs):
        tenders = request.env['tender.paket'].sudo().search([('status', '!=', 'draft')])
        return request.render('sadaya_tender.portal_tender_list', {
            'tenders': tenders
        })

    @http.route(['/tenders/<model("tender.paket"):tender>'], type='http', auth='public', website=True)
    def tender_detail(self, tender, **kwargs):
        return request.render('sadaya_tender.portal_tender_detail', {
            'tender': tender
        })

    @http.route('/my/tenders', type='http', auth='user', website=True)
    def my_tenders(self, **kwargs):
        partner = request.env.user.partner_id
        if not partner.is_vendor_tender:
            return request.render('sadaya_tender.portal_vendor_registration', {
                'partner': partner
            })
            
        bids = request.env['tender.penawaran'].sudo().search([('vendor_id', '=', partner.id)])
        return request.render('sadaya_tender.portal_my_tenders', {
            'bids': bids,
            'partner': partner
        })
