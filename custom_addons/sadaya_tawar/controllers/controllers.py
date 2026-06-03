from odoo import http
from odoo.http import request

class SadayaTawarPortal(http.Controller):
    def _is_vendor_eligible(self, partner):
        if not partner or not partner.is_company:
            return False
        if 'is_sadaya_mitra_vendor' in partner._fields:
            return bool(partner.is_sadaya_mitra_vendor)
        if 'sadaya_mitra_penyedia_id' in partner._fields:
            return bool(partner.sadaya_mitra_penyedia_id)
        return True

    # Membuat URL /sadaya_tawar/paket untuk melihat daftar pengumuman
    @http.route(['/sadaya_tawar/paket'], type='http', auth="public", website=True)
    def list_paket_tawar(self, **kwargs):
        domain = [('state', '=', 'published')]
        search = kwargs.get('search')
        metode = kwargs.get('metode')

        if search:
            domain += ['|', ('name', 'ilike', search), ('kode_paket', 'ilike', search)]
        if metode in ['e_purchasing', 'pengadaan_langsung', 'tender']:
            domain.append(('metode_pemilihan', '=', metode))

        pakets = request.env['sadaya_tawar.paket'].sudo().search(domain, order='batas_pendaftaran asc, id desc')
        return request.render('sadaya_tawar.portal_list_paket_template', {
            'pakets': pakets,
            'search': search,
            'metode': metode,
        })

    # Membuat URL untuk melihat detail satu paket spesifik
    @http.route(['/sadaya_tawar/paket/<model("sadaya_tawar.paket"):paket>'], type='http', auth="public", website=True)
    def detail_paket_tawar(self, paket, **kwargs):
        paket = paket.sudo()
        if paket.state != 'published':
            return request.not_found()

        is_public = request.env.user.has_group('base.group_public')
        partner = None if is_public else request.env.user.partner_id
        peserta_env = request.env['sadaya_tawar.peserta']

        is_registered = False
        can_register = False
        if partner:
            is_registered = bool(peserta_env.search([
                ('paket_id', '=', paket.id),
                ('vendor_id', '=', partner.id)
            ], limit=1))
            can_register = self._is_vendor_eligible(partner)

        return request.render('sadaya_tawar.portal_detail_paket_template', {
            'paket': paket,
            'is_registered': is_registered,
            'can_register': can_register,
            'daftar': kwargs.get('daftar'),
            'error': kwargs.get('error'),
        })

    # Endpoint untuk memproses aksi klik "Daftar Sebagai Peserta"
    @http.route([
        '/sadaya_tawar/paket/<model("sadaya_tawar.paket"):paket>/daftar'
    ], type='http', auth='user', website=True, methods=['POST'])
    def daftar_peserta(self, paket, **kwargs):
        paket = paket.sudo()
        if paket.state != 'published':
            return request.redirect('/sadaya_tawar/paket?error=not_available')

        partner = request.env.user.partner_id
        if not self._is_vendor_eligible(partner):
            return request.redirect('/sadaya_tawar/paket/%s?error=not_verified' % paket.id)

        peserta_env = request.env['sadaya_tawar.peserta']
        existing = peserta_env.search([
            ('paket_id', '=', paket.id),
            ('vendor_id', '=', partner.id)
        ], limit=1)
        if existing:
            return request.redirect('/sadaya_tawar/paket/%s?error=already_registered' % paket.id)

        peserta_env.create({
            'paket_id': paket.id,
            'vendor_id': partner.id,
        })
        return request.redirect('/sadaya_tawar/paket/%s?daftar=success' % paket.id)