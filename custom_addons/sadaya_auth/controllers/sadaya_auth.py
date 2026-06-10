# -*- coding: utf-8 -*-
import re
import base64
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError, AccessDenied

_logger = logging.getLogger(__name__)


class SadayaAuthController(http.Controller):

    # ══════════════════════════════════════════════════
    # REGISTER
    # ══════════════════════════════════════════════════

    @http.route('/sadaya/register', type='http', auth='public', website=True, sitemap=False)
    def sadaya_register_page(self, **kwargs):
        if not request.env.user._is_public():
            return request.redirect('/sadaya/dashboard')
        return request.render('sadaya_auth.sadaya_register_select', {})

    @http.route('/sadaya/register/badan-usaha', type='http', auth='public', website=True, sitemap=False)
    def sadaya_register_badan_usaha(self, **kwargs):
        if not request.env.user._is_public():
            return request.redirect('/sadaya/dashboard')
        return request.render('sadaya_auth.sadaya_register_badan_usaha',
                              {'error': {}, 'form_data': {}})

    @http.route('/sadaya/register/perorangan', type='http', auth='public', website=True, sitemap=False)
    def sadaya_register_perorangan(self, **kwargs):
        if not request.env.user._is_public():
            return request.redirect('/sadaya/dashboard')
        return request.render('sadaya_auth.sadaya_register_perorangan',
                              {'error': {}, 'form_data': {}})

    @http.route('/sadaya/register/submit', type='http', auth='public', website=True,
                sitemap=False, methods=['POST'], csrf=True)
    def sadaya_register_submit(self, **post):
        tipe = post.get('tipe_pendaftar', 'perorangan')
        errors = {}
        form_data = dict(post)

        try:
            errors = self._validate_registration_data(post, tipe)

            # ── File: Swafoto KTP ──────────────────────
            swafoto_file = request.httprequest.files.get('swafoto_ktp')
            swafoto_b64 = None
            swafoto_fname = None
            if swafoto_file and swafoto_file.filename:
                ext = swafoto_file.filename.rsplit('.', 1)[-1].lower()
                if ext not in ('jpg', 'jpeg', 'png'):
                    errors['swafoto_ktp'] = 'Format harus JPEG/JPG/PNG'
                else:
                    data = swafoto_file.read()
                    if len(data) > 10 * 1024 * 1024:
                        errors['swafoto_ktp'] = 'Ukuran file maksimal 10 MB'
                    else:
                        swafoto_b64 = base64.b64encode(data)
                        swafoto_fname = swafoto_file.filename
            else:
                errors['swafoto_ktp'] = 'Swafoto memegang KTP wajib diunggah'

            # ── File: Bukti NPWP (opsional) ───────────
            bukti_npwp_b64 = None
            bukti_npwp_fname = None
            bukti_npwp_file = request.httprequest.files.get('bukti_npwp')
            if bukti_npwp_file and bukti_npwp_file.filename:
                if not bukti_npwp_file.filename.lower().endswith('.pdf'):
                    errors['bukti_npwp'] = 'Bukti NPWP harus berformat PDF'
                else:
                    data = bukti_npwp_file.read()
                    if len(data) > 10 * 1024 * 1024:
                        errors['bukti_npwp'] = 'Ukuran file maksimal 10 MB'
                    else:
                        bukti_npwp_b64 = base64.b64encode(data)
                        bukti_npwp_fname = bukti_npwp_file.filename

            if errors:
                tmpl = ('sadaya_auth.sadaya_register_badan_usaha'
                        if tipe == 'badan_usaha'
                        else 'sadaya_auth.sadaya_register_perorangan')
                return request.render(tmpl, {'tipe': tipe, 'error': errors, 'form_data': form_data})

            # ── Simpan ────────────────────────────────
            vals = self._prepare_registration_vals(post, tipe)
            if swafoto_b64:
                vals['swafoto_ktp'] = swafoto_b64
                vals['swafoto_ktp_filename'] = swafoto_fname
            if bukti_npwp_b64:
                vals['bukti_npwp'] = bukti_npwp_b64
                vals['bukti_npwp_filename'] = bukti_npwp_fname

            reg = request.env['sadaya.registration'].sudo().create(vals)
            reg.sudo().action_submit()
            reg.sudo().action_approve()

            try:
                credential = {'login': vals['email'], 'password': vals['password'], 'type': 'password'}
                request.session.authenticate(request.env, credential)
                return request.redirect('/sadaya_mitra/lanjutan')
            except AccessDenied:
                return request.redirect('/sadaya/login?success=registered')

        except ValidationError as e:
            request.env.cr.rollback()
            errors['general'] = str(e.args[0]) if e.args else 'Kesalahan validasi.'
        except Exception as e:
            request.env.cr.rollback()
            _logger.exception("Sadaya register error: %s", e)
            errors['general'] = 'Terjadi kesalahan sistem. Silakan coba lagi.'

        tmpl = ('sadaya_auth.sadaya_register_badan_usaha'
                if tipe == 'badan_usaha'
                else 'sadaya_auth.sadaya_register_perorangan')
        return request.render(tmpl, {'tipe': tipe, 'error': errors, 'form_data': form_data})

    @http.route('/sadaya/register/success', type='http', auth='public', website=True, sitemap=False)
    def sadaya_register_success(self, **kwargs):
        return request.render('sadaya_auth.sadaya_register_success',
                              {'email': kwargs.get('email', '')})

    # ══════════════════════════════════════════════════
    # LOGIN
    # ══════════════════════════════════════════════════

    @http.route('/sadaya/login', type='http', auth='public', website=True, sitemap=False)
    def sadaya_login_page(self, **kwargs):
        if not request.env.user._is_public():
            return request.redirect('/sadaya/dashboard')
        return request.render('sadaya_auth.sadaya_login', {
            'error': {},
            'redirect': kwargs.get('redirect', '/sadaya/dashboard'),
            'form_data': {},
        })

    @http.route('/sadaya/login/submit', type='http', auth='public', website=True,
                sitemap=False, methods=['POST'], csrf=True)
    def sadaya_login_submit(self, **post):
        email = post.get('email', '').strip()
        password = post.get('password', '')
        redirect = post.get('redirect', '/sadaya/dashboard')
        errors = {}

        if not email:
            errors['email'] = 'Email wajib diisi'
        if not password:
            errors['password'] = 'Kata sandi wajib diisi'

        if errors:
            return request.render('sadaya_auth.sadaya_login', {
                'error': errors,
                'redirect': redirect,
                'form_data': {'email': email},
            })

        try:
            credential = {'login': email, 'password': password, 'type': 'password'}
            auth_info = request.session.authenticate(request.env, credential)
            if auth_info and auth_info.get('uid'):
                return request.redirect('/sadaya_mitra/lanjutan')
            else:
                return request.render('sadaya_auth.sadaya_login', {
                    'error': {'general': 'Email atau kata sandi tidak valid.'},
                    'redirect': redirect,
                    'form_data': {'email': email},
                })
        except AccessDenied:
            return request.render('sadaya_auth.sadaya_login', {
                'error': {'general': 'Email atau kata sandi salah. Pastikan akun sudah diverifikasi.'},
                'redirect': redirect,
                'form_data': {'email': email},
            })
        except Exception as e:
            _logger.exception("Sadaya login error: %s", e)
            return request.render('sadaya_auth.sadaya_login', {
                'error': {'general': 'Terjadi kesalahan sistem. Silakan coba lagi.'},
                'redirect': redirect,
                'form_data': {'email': email},
            })

    # ══════════════════════════════════════════════════
    # LOGOUT
    # ══════════════════════════════════════════════════

    @http.route('/sadaya/logout', type='http', auth='user', website=True, sitemap=False)
    def sadaya_logout(self, **kwargs):
        request.session.logout(keep_db=True)
        return request.redirect('/sadaya/login?success=logout')

    # ══════════════════════════════════════════════════
    # DASHBOARD
    # ══════════════════════════════════════════════════

    @http.route('/sadaya/dashboard', type='http', auth='user', website=True, sitemap=False)
    def sadaya_dashboard(self, **kwargs):
        user = request.env.user
        registration = request.env['sadaya.registration'].sudo().search(
            [('user_id', '=', user.id)], limit=1)
        return request.render('sadaya_auth.sadaya_dashboard', {
            'user': user,
            'registration': registration,
            'tipe': registration.tipe_pendaftar if registration else 'perorangan',
        })

    # ══════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════

    def _validate_registration_data(self, post, tipe):
        errors = {}
        Reg = request.env['sadaya.registration']

        if not post.get('nama_lengkap', '').strip():
            errors['nama_lengkap'] = 'Nama Lengkap wajib diisi'

        email = post.get('email', '').strip()
        if not email:
            errors['email'] = 'Email wajib diisi'
        else:
            if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
                errors['email'] = 'Format email tidak valid'
            else:
                if request.env['sadaya.registration'].sudo().search([
                    ('email', '=', email), ('state', 'not in', ['rejected'])
                ]):
                    errors['email'] = 'Email ini sudah terdaftar'
                elif request.env['res.users'].sudo().search([('login', '=', email)]):
                    errors['email'] = 'Email ini sudah terdaftar sebagai pengguna aktif'

        password = post.get('password', '')
        if not password:
            errors['password'] = 'Kata sandi wajib diisi'
        else:
            pwd_errors = Reg.validate_password(password)
            if pwd_errors:
                errors['password'] = 'Password harus: ' + ', '.join(pwd_errors)
        if password and post.get('password_confirm') and password != post.get('password_confirm'):
            errors['password_confirm'] = 'Konfirmasi kata sandi tidak sesuai'

        wa = post.get('whatsapp_narahubung', '').strip()
        if not wa:
            errors['whatsapp_narahubung'] = 'Nomor WhatsApp wajib diisi'
        elif len(re.sub(r'\D', '', wa)) < 12:
            errors['whatsapp_narahubung'] = 'Minimal 12 digit'

        nik = re.sub(r'\D', '', post.get('nik_narahubung', ''))
        if len(nik) != 16:
            errors['nik_narahubung'] = 'NIK harus 16 digit'

        if tipe == 'badan_usaha':
            if not post.get('nama_badan_usaha', '').strip():
                errors['nama_badan_usaha'] = 'Nama Badan Usaha wajib diisi'
            if not post.get('telepon_badan_usaha', '').strip():
                errors['telepon_badan_usaha'] = 'Telepon Badan Usaha wajib diisi'

        npwp = re.sub(r'\D', '', post.get('npwp_perusahaan', ''))
        if npwp and len(npwp) != 16:
            errors['npwp_perusahaan'] = 'NPWP harus 16 digit'

        return errors

    def _prepare_registration_vals(self, post, tipe):
        vals = {
            'tipe_pendaftar': tipe,
            'nama_lengkap': post.get('nama_lengkap', '').strip(),
            'email': post.get('email', '').strip().lower(),
            'password': post.get('password', ''),
            'whatsapp_narahubung': post.get('whatsapp_narahubung', '').strip(),
            'nik_narahubung': re.sub(r'\D', '', post.get('nik_narahubung', '')),
        }
        if tipe == 'badan_usaha':
            vals['nama_badan_usaha'] = post.get('nama_badan_usaha', '').strip()
            vals['telepon_badan_usaha'] = post.get('telepon_badan_usaha', '').strip()
        npwp = re.sub(r'\D', '', post.get('npwp_perusahaan', ''))
        if npwp:
            vals['npwp_perusahaan'] = npwp
        return vals
