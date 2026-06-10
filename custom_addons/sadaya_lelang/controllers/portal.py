# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class TenderPortal(http.Controller):

    @http.route('/sadaya-lelang/tender', type='http', auth='public', website=False)
    def tender_list(self, **kwargs):
        tenders = request.env['sadaya_lelang.paket'].sudo().search([('status', 'not in', ['draft', 'menunggu_persetujuan'])])
        return request.render('sadaya_lelang.portal_tender_list', {
            'tenders': tenders
        })

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>'], type='http', auth='public', website=False)
    def tender_detail(self, tender, **kwargs):
        return request.render('sadaya_lelang.portal_tender_detail', {
            'tender': tender
        })

    @http.route('/sadaya-lelang/dashboard', type='http', auth='user', website=False)
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

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>/submit_bid'], type='http', auth='user', website=False)
    def submit_bid(self, tender, **kwargs):
        partner = request.env.user.partner_id
        if not getattr(partner, 'is_vendor_tender', True):
            return request.redirect('/my')
            
        # Check if bid already exists
        existing_bid = request.env['sadaya_lelang.penawaran'].sudo().search([
            ('paket_id', '=', tender.id),
            ('vendor_id', '=', partner.id)
        ], limit=1)
        
        return request.render('sadaya_lelang.portal_tender_submit_bid', {
            'tender': tender,
            'existing_bid': existing_bid
        })

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>/process_bid'], type='http', auth='user', methods=['POST'], website=False, csrf=False)
    def process_bid(self, tender, **post):
        import base64
        partner = request.env.user.partner_id
        
        harga_penawaran = post.get('harga_penawaran')
        file_kualifikasi = post.get('file_kualifikasi')
        file_penawaran = post.get('file_penawaran')
        
        vals = {
            'paket_id': tender.id,
            'vendor_id': partner.id,
            'harga_penawaran': float(harga_penawaran) if harga_penawaran else 0.0,
        }
        
        if file_kualifikasi:
            vals['file_kualifikasi'] = base64.b64encode(file_kualifikasi.read())
        if file_penawaran:
            vals['file_penawaran'] = base64.b64encode(file_penawaran.read())
            
        existing_bid = request.env['sadaya_lelang.penawaran'].sudo().search([
            ('paket_id', '=', tender.id),
            ('vendor_id', '=', partner.id)
        ], limit=1)
        
        if existing_bid:
            existing_bid.sudo().write(vals)
        else:
            request.env['sadaya_lelang.penawaran'].sudo().create(vals)
            
        return request.redirect('/sadaya-lelang/dashboard')
