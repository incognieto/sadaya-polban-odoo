# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class TenderPortal(http.Controller):

    @http.route('/sadaya-lelang/tender', type='http', auth='public', website=True)
    def tender_list(self, **kwargs):
        tenders = request.env['sadaya_lelang.paket'].sudo().search([('status', 'not in', ['draft', 'menunggu_persetujuan'])])
        return request.render('sadaya_lelang.portal_tender_list', {
            'tenders': tenders
        })

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>'], type='http', auth='public', website=True)
    def tender_detail(self, tender, **kwargs):
        partner = request.env.user.partner_id
        is_vendor = False
        if partner and request.env.user.id != request.env.ref('base.public_user').id:
            is_vendor = getattr(partner, 'is_vendor_tender', False) or getattr(partner, 'is_sadaya_mitra_vendor', False)
            
        return request.render('sadaya_lelang.portal_tender_detail', {
            'tender': tender.sudo(),
            'is_vendor': is_vendor
        })

    @http.route('/sadaya-lelang', type='http', auth='user', website=True)
    def my_tenders(self, **kwargs):
        partner = request.env.user.partner_id
        is_vendor = getattr(partner, 'is_vendor_tender', False) or getattr(partner, 'is_sadaya_mitra_vendor', False)
            
        bids = request.env['sadaya_lelang.penawaran'].sudo().search([('vendor_id', '=', partner.id)])
        return request.render('sadaya_lelang.portal_my_tenders', {
            'bids': bids,
            'partner': partner,
            'is_vendor': is_vendor
        })

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>/submit_bid'], type='http', auth='user', website=True)
    def submit_bid(self, tender, **kwargs):
        partner = request.env.user.partner_id
        is_vendor = getattr(partner, 'is_vendor_tender', False) or getattr(partner, 'is_sadaya_mitra_vendor', False)
            
        # Check if bid already exists
        existing_bid = request.env['sadaya_lelang.penawaran'].sudo().search([
            ('paket_id', '=', tender.id),
            ('vendor_id', '=', partner.id)
        ], limit=1)
        
        return request.render('sadaya_lelang.portal_tender_submit_bid', {
            'tender': tender,
            'existing_bid': existing_bid,
            'is_vendor': is_vendor
        })

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>/process_bid'], type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def process_bid(self, tender, **post):
        import base64
        partner = request.env.user.partner_id
        is_vendor = getattr(partner, 'is_vendor_tender', False) or getattr(partner, 'is_sadaya_mitra_vendor', False)
        
        if not is_vendor:
            return request.redirect('/sadaya-lelang/tender/%s' % tender.id)
        
        harga_penawaran = post.get('harga_penawaran')
        file_kualifikasi = post.get('file_kualifikasi')
        file_penawaran = post.get('file_penawaran')
        
        vals = {
            'paket_id': tender.id,
            'vendor_id': partner.id,
            'harga_penawaran': float(harga_penawaran.replace('.', '').replace(',', '')) if harga_penawaran else 0.0,
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

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>/submit_sanggahan'], type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def submit_sanggahan(self, tender, **post):
        partner = request.env.user.partner_id
        is_vendor = getattr(partner, 'is_vendor_tender', False) or getattr(partner, 'is_sadaya_mitra_vendor', False)
        
        if not is_vendor or tender.status != 'masa_sanggah':
            return request.redirect('/sadaya-lelang/tender/%s' % tender.id)
            
        pertanyaan = post.get('pertanyaan')
        if pertanyaan:
            request.env['sadaya_lelang.sanggah'].sudo().create({
                'paket_id': tender.id,
                'vendor_id': partner.id,
                'pertanyaan': pertanyaan,
                'status_sanggah': 'masuk'
            })
            
        return request.redirect('/sadaya-lelang/tender/%s' % tender.id)

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>/submit_penjelasan'], type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def submit_penjelasan(self, tender, **post):
        partner = request.env.user.partner_id
        is_vendor = False
        if partner and request.env.user.id != request.env.ref('base.public_user').id:
            is_vendor = getattr(partner, 'is_vendor_tender', False) or getattr(partner, 'is_sadaya_mitra_vendor', False)
        
        if not is_vendor or tender.status != 'penjelasan':
            return request.redirect('/sadaya-lelang/tender/%s' % tender.id)
            
        pertanyaan = post.get('pertanyaan')
        if pertanyaan:
            request.env['sadaya_lelang.penjelasan'].sudo().create({
                'paket_id': tender.id,
                'vendor_id': partner.id,
                'pertanyaan': pertanyaan,
                'status_penjelasan': 'masuk'
            })
            
        return request.redirect('/sadaya-lelang/tender/%s' % tender.id)

    @http.route(['/sadaya-lelang/tender/<model("sadaya_lelang.paket"):tender>/submit_kontrak_jaminan'], type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def submit_kontrak_jaminan(self, tender, **post):
        import base64
        partner = request.env.user.partner_id
        is_vendor = False
        if partner and request.env.user.id != request.env.ref('base.public_user').id:
            is_vendor = getattr(partner, 'is_vendor_tender', False) or getattr(partner, 'is_sadaya_mitra_vendor', False)
        
        # Check if winner
        winning_bid = request.env['sadaya_lelang.penawaran'].sudo().search([('paket_id', '=', tender.id), ('status', '=', 'winner')], limit=1)
        if not is_vendor or not winning_bid or winning_bid.vendor_id.id != partner.id:
            return request.redirect('/sadaya-lelang/tender/%s' % tender.id)
            
        upload_type = post.get('upload_type')
        file_upload = post.get('file_upload')
        
        if file_upload:
            file_content = base64.b64encode(file_upload.read())
            file_name = file_upload.filename
            if upload_type == 'jaminan':
                tender.sudo().write({
                    'file_jaminan_pelaksanaan': file_content,
                    'file_jaminan_pelaksanaan_name': file_name
                })
            elif upload_type == 'kontrak':
                update_vals = {
                    'file_kontrak': file_content,
                    'file_kontrak_name': file_name
                }
                if tender.status in ['sppbj', 'pam']:
                    update_vals['status'] = 'kontrak'
                tender.sudo().write(update_vals)
                
        return request.redirect('/sadaya-lelang/tender/%s' % tender.id)
