import base64
from odoo import http
from odoo.http import request

class SadayaRancangPortal(http.Controller):

    # Route: Landing page portal rancang
    @http.route(['/sadaya-rancang'], type='http', auth="public", website=True)
    def index_rancang(self, **kwargs):
        Usulan = request.env['rancang.usulan'].sudo()
        values = {
            'active_page': 'dashboard',
            'total_usulan': Usulan.search_count([]),
            'usulan_draft': Usulan.search_count([('state', '=', 'draft')]),
            'usulan_submitted': Usulan.search_count([('state', '=', 'submitted')]),
            'usulan_approved': Usulan.search_count([('state', 'in', ['approved', 'published'])]),
        }
        return request.render('sadaya_rancang.portal_rancang_index', values)

    # Route: Daftar Pengajuan Kebutuhan
    @http.route(['/sadaya-rancang/pengajuan'], type='http', auth="public", website=True)
    def list_pengajuan(self, **kwargs):
        usulans = request.env['rancang.usulan'].sudo().search([])
        return request.render('sadaya_rancang.portal_rancang_pengajuan', {
            'usulans': usulans,
            'active_page': 'pengajuan',
            'total_usulan': len(usulans)
        })

    # Route: Form Buat Pengajuan Baru
    @http.route(['/sadaya-rancang/pengajuan/baru'], type='http', auth="public", website=True, methods=['GET', 'POST'])
    def form_baru_pengajuan(self, **kwargs):
        if request.httprequest.method == 'POST':
            vals = {
                'name': kwargs.get('name'),
                'pemohon': kwargs.get('pemohon'),
                'jenis_kebutuhan': kwargs.get('jenis_kebutuhan'),
                'rab': float(kwargs.get('rab', 0.0)),
                'deskripsi_kebutuhan': kwargs.get('deskripsi_kebutuhan'),
            }
            if 'kak' in request.params:
                attached_file = request.params.get('kak')
                if hasattr(attached_file, 'filename') and attached_file.filename:
                    vals['kak'] = base64.b64encode(attached_file.read())
                    vals['kak_filename'] = attached_file.filename

            new_usulan = request.env['rancang.usulan'].sudo().create(vals)
            return request.redirect('/sadaya-rancang/pengajuan')

        return request.render('sadaya_rancang.portal_rancang_form', {
            'active_page': 'pengajuan'
        })

    # Route: Detail Pengajuan
    @http.route(['/sadaya-rancang/pengajuan/<model("rancang.usulan"):usulan>'], type='http', auth="public", website=True)
    def detail_pengajuan(self, usulan, **kwargs):
        return request.render('sadaya_rancang.portal_rancang_detail', {
            'usulan': usulan,
            'active_page': 'pengajuan'
        })

    # Route: Revert Pengajuan (Kembali ke Draft)
    @http.route(['/sadaya-rancang/pengajuan/<model("rancang.usulan"):usulan>/revert'], type='http', auth="public", website=True)
    def revert_pengajuan(self, usulan, **kwargs):
        if usulan.state in ['submitted', 'returned', 'rejected']:
            usulan.sudo().action_draft()
        return request.redirect(f'/sadaya-rancang/pengajuan/{usulan.id}')

    # Route: Hapus Pengajuan
    @http.route(['/sadaya-rancang/pengajuan/<model("rancang.usulan"):usulan>/delete'], type='http', auth="public", website=True)
    def delete_pengajuan(self, usulan, **kwargs):
        if usulan.state in ['draft', 'returned']:
            usulan.sudo().unlink()
        return request.redirect('/sadaya-rancang/pengajuan')

    # Route: Ajukan Pengajuan
    @http.route(['/sadaya-rancang/pengajuan/<model("rancang.usulan"):usulan>/submit'], type='http', auth="public", website=True)
    def submit_pengajuan(self, usulan, **kwargs):
        if usulan.state in ['draft', 'returned']:
            usulan.sudo().action_submit()
        return request.redirect(f'/sadaya-rancang/pengajuan/{usulan.id}')

    # Route: Setujui Pengajuan
    @http.route(['/sadaya-rancang/pengajuan/<model("rancang.usulan"):usulan>/approve'], type='http', auth="public", website=True)
    def approve_pengajuan(self, usulan, **kwargs):
        if usulan.state == 'submitted':
            usulan.sudo().action_approve()
        return request.redirect(f'/sadaya-rancang/pengajuan/{usulan.id}')

    # Route: Tolak Pengajuan
    @http.route(['/sadaya-rancang/pengajuan/<model("rancang.usulan"):usulan>/reject'], type='http', auth="public", website=True, methods=['POST'])
    def reject_pengajuan(self, usulan, **kwargs):
        if usulan.state == 'submitted':
            alasan = kwargs.get('alasan', 'Tanpa alasan')
            usulan.sudo().write({'state': 'rejected'})
            usulan.sudo().message_post(body=f"Persetujuan ditolak dengan alasan: {alasan}")
        return request.redirect(f'/sadaya-rancang/pengajuan/{usulan.id}')

    # Route: Publikasi ke RUP
    @http.route(['/sadaya-rancang/pengajuan/<model("rancang.usulan"):usulan>/publish'], type='http', auth="public", website=True)
    def publish_pengajuan(self, usulan, **kwargs):
        if usulan.state == 'approved':
            usulan.sudo().action_publish_rup()
        return request.redirect(f'/sadaya-rancang/pengajuan/{usulan.id}')

    # Route: Persetujuan Manajemen (Menunggu Persetujuan)
    @http.route(['/sadaya-rancang/persetujuan_manajemen'], type='http', auth="public", website=True)
    def list_persetujuan(self, **kwargs):
        usulans = request.env['rancang.usulan'].sudo().search([('state', '=', 'submitted')])
        return request.render('sadaya_rancang.portal_rancang_persetujuan', {
            'usulans': usulans,
            'active_page': 'persetujuan',
            'total_usulan': len(usulans)
        })
