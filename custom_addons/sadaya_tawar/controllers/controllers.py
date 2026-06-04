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

    @http.route(['/sadaya_tawar/paket'], type='http', auth="public", website=True)
    def list_paket_tawar(self, **kwargs):
        search = kwargs.get('search')
        metode = kwargs.get('metode')
        jenis = kwargs.get('jenis')
        status = kwargs.get('status')
        min_hps = kwargs.get('min_hps')
        max_hps = kwargs.get('max_hps')

        if status in ['published', 'eval', 'routed']:
            domain = [('state', '=', status)]
        else:
            domain = [('state', 'in', ['published', 'eval', 'routed'])]

        if search:
            domain += ['|', ('name', 'ilike', search), ('kode_paket', 'ilike', search)]
        
        if metode in ['e_purchasing', 'pengadaan_langsung', 'tender']:
            domain.append(('metode_pemilihan', '=', metode))
            
        if jenis in ['barang', 'jasa', 'konstruksi', 'konsultansi']: 
            domain.append(('jenis_pengadaan', '=', jenis))

        if min_hps and min_hps.isdigit():
            domain.append(('nilai_hps', '>=', float(min_hps)))
            
        if max_hps and max_hps.isdigit():
            domain.append(('nilai_hps', '<=', float(max_hps)))

        pakets = request.env['sadaya_tawar.paket'].sudo().search(domain, order='batas_pendaftaran asc, id desc')
        
        return request.render('sadaya_tawar.portal_list_paket_template', {
            'pakets': pakets,
            'search': search,
            'metode': metode,
            'jenis': jenis,
            'status': status,
            'min_hps': min_hps,
            'max_hps': max_hps,
        })

    # --- KEMBALI MENGGUNAKAN MODEL SLUG CONVERTER ODOO ---
    @http.route(['/sadaya_tawar/paket/<model("sadaya_tawar.paket"):paket>'], type='http', auth="public", website=True)
    def detail_paket_tawar(self, paket, **kwargs):
        # Sudo agar bypass limitasi hak akses
        paket = paket.sudo()
        
        if not paket.exists():
            return request.not_found()

        # Izinkan paket dengan status Pengumuman, Evaluasi, atau Terkirim Eksekusi
        if paket.state not in ['published', 'eval', 'routed']:
            return request.not_found()

        is_public = request.env.user.has_group('base.group_public')
        partner = None if is_public else request.env.user.partner_id
        peserta_env = request.env['sadaya_tawar.peserta'].sudo()

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

    @http.route([
        '/sadaya_tawar/paket/<model("sadaya_tawar.paket"):paket>/daftar'
    ], type='http', auth='user', website=True, methods=['POST'])
    def daftar_peserta(self, paket, **kwargs):
        paket = paket.sudo()
        
        # Pendaftaran hanya bisa dilakukan jika status masih pengumuman atau evaluasi awal
        if not paket.exists() or paket.state not in ['published', 'eval']:
            return request.redirect('/sadaya_tawar/paket?error=not_available')

        partner = request.env.user.partner_id
        if not self._is_vendor_eligible(partner):
            return request.redirect('/sadaya_tawar/paket/%s?error=not_verified' % paket.id)

        peserta_env = request.env['sadaya_tawar.peserta'].sudo()
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