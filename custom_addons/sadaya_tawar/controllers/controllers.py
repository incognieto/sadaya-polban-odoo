from odoo import http
from odoo.http import request

class SadayaTawarPortal(http.Controller):
    def _is_vendor_eligible(self, partner):
        if not partner:
            return False
            
        # 1. Cek apakah partner memiliki relasi ke penyedia (Alur standar)
        if 'sadaya_mitra_penyedia_id' in partner._fields and partner.sadaya_mitra_penyedia_id:
            return True
            
        # 2. Fallback: Tangani isu "Dummy Partner" & Vendor Perorangan
        PenyediaModel = request.env.get('sadaya_mitra.penyedia')
        if PenyediaModel is not None:
            # Lacak status vendor menggunakan email akun yang login
            penyedia = PenyediaModel.sudo().search([
                ('email', '=', partner.email), 
                ('status_verifikasi', '=', 'approved')
            ], limit=1)
            
            if penyedia:
                return True
                
        return False

    # 1. Endpoint Utama diubah menjadi /sadaya-tawar
    @http.route(['/sadaya-tawar'], type='http', auth="public", website=True)
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

    # 2. Endpoint Detail menggunakan prefix /sadaya-tawar
    @http.route(['/sadaya-tawar/<model("sadaya_tawar.paket"):paket>'], type='http', auth="public", website=True)
    def detail_paket_tawar(self, paket, **kwargs):
        paket = paket.sudo()
        
        if not paket.exists():
            return request.not_found()

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

    # 3. Endpoint Registrasi menggunakan prefix /sadaya-tawar
    @http.route([
        '/sadaya-tawar/<model("sadaya_tawar.paket"):paket>/daftar'
    ], type='http', auth='user', website=True, methods=['POST'])
    def daftar_peserta(self, paket, **kwargs):
        paket = paket.sudo()
        
        if not paket.exists() or paket.state not in ['published', 'eval']:
            return request.redirect('/sadaya-tawar?error=not_available')

        partner = request.env.user.partner_id
        if not self._is_vendor_eligible(partner):
            return request.redirect('/sadaya-tawar/%s?error=not_verified' % paket.id)

        # === BLOK VALIDASI KBLI ===
        if paket.syarat_kbli and partner.sadaya_mitra_penyedia_id:
            penyedia_id = partner.sadaya_mitra_penyedia_id.id
            # Ekstrak semua kode_kbli milik vendor dari model Sadaya Mitra
            vendor_kblis = request.env['sadaya_mitra.kbli'].sudo().search([
                ('izin_id.penyedia_id', '=', penyedia_id)
            ]).mapped('kode_kbli')
            
            # Parsing KBLI yang disyaratkan paket menjadi list (menghapus spasi)
            syarat_list = [k.strip() for k in paket.syarat_kbli.split(',') if k.strip()]
            
            # Cek kecocokan minimal 1 KBLI
            has_matching_kbli = any(kbli in vendor_kblis for kbli in syarat_list)
            if not has_matching_kbli:
                return request.redirect('/sadaya-tawar/%s?error=kbli_mismatch' % paket.id)
        # ==========================

        peserta_env = request.env['sadaya_tawar.peserta'].sudo()
        existing = peserta_env.search([
            ('paket_id', '=', paket.id),
            ('vendor_id', '=', partner.id)
        ], limit=1)
        
        if existing:
            return request.redirect('/sadaya-tawar/%s?error=already_registered' % paket.id)

        peserta_env.create({
            'paket_id': paket.id,
            'vendor_id': partner.id,
        })
        return request.redirect('/sadaya-tawar/%s?daftar=success' % paket.id)