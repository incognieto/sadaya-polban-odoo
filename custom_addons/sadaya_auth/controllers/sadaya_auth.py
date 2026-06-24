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
                sitemap=False, methods=['POST'], csrf=False)
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

            # ── Simpan ke database ────────────────────
            vals = self._prepare_registration_vals(post, tipe)
            if swafoto_b64:
                vals['swafoto_ktp'] = swafoto_b64
                vals['swafoto_ktp_filename'] = swafoto_fname
            if bukti_npwp_b64:
                vals['bukti_npwp'] = bukti_npwp_b64
                vals['bukti_npwp_filename'] = bukti_npwp_fname

            # Simpan password plain SEBELUM approve (approve akan menghapusnya)
            plain_password = vals['password']
            plain_email = vals['email']

            # Buat record registrasi di database
            reg = request.env['sadaya.registration'].sudo().create(vals)
            reg.sudo().action_submit()
            reg.sudo().action_approve()

            # Commit transaksi database agar user baru ter-persis sebelum login otomatis
            request.env.cr.commit()

            # ── Login otomatis setelah register (dan redirect ke sadaya-mitra) ──────
            return self._do_login_and_redirect(plain_email, plain_password, '/sadaya-mitra')

        except ValidationError as e:
            request.env.cr.rollback()
            errors['general'] = str(e.args[0]) if e.args else 'Kesalahan validasi.'
        except AccessDenied:
            errors['general'] = 'Akun berhasil dibuat namun gagal login otomatis. Silakan login manual.'
            return request.redirect('/sadaya/login')
        except Exception as e:
            request.env.cr.rollback()
            _logger.exception("Sadaya register error: %s", e)
            errors['general'] = 'Terjadi kesalahan sistem: %s' % str(e)

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
                sitemap=False, methods=['POST'], csrf=False)
    def sadaya_login_submit(self, **post):
        email    = post.get('email', '').strip()
        password = post.get('password', '')
        redirect = post.get('redirect', '/sadaya/dashboard')
        errors   = {}

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
            return self._do_login_and_redirect(email, password, redirect)
        except AccessDenied:
            return request.render('sadaya_auth.sadaya_login', {
                'error': {'general': 'Email atau kata sandi salah. Pastikan akun sudah diverifikasi.'},
                'redirect': redirect,
                'form_data': {'email': email},
            })
        except Exception as e:
            _logger.exception("Sadaya login error: %s", e)
            return request.render('sadaya_auth.sadaya_login', {
                'error': {'general': 'Terjadi kesalahan: %s' % str(e)},
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
    # PRIVATE HELPERS
    # ══════════════════════════════════════════════════

    def _do_login_and_redirect(self, login, password, redirect='/sadaya/dashboard'):
        """
        Authenticate user dan redirect.
        Compatible Odoo 16, 17, 18, 19.
        Raise AccessDenied jika kredensial salah.
        """
        db = request.db
        _logger.info("DO_LOGIN: db=%s, login=%s, len_pwd=%d, redirect=%s", db, login, len(password) if password else 0, redirect)
        uid = None

        # ── Strategi 1: request.session.authenticate (Odoo 18/19 dengan env dan credential) ──
        try:
            credential = {'type': 'password', 'login': login, 'password': password}
            auth_info = request.session.authenticate(request.env, credential)
            if auth_info and isinstance(auth_info, dict):
                uid = auth_info.get('uid')
            else:
                uid = auth_info
        except TypeError:
            pass
        except AccessDenied:
            raise
        except Exception as e:
            _logger.warning("authenticate(env, credential) gagal: %s", e)

        # ── Strategi 2: request.session.authenticate (Odoo 17 dengan db) ──
        if not uid:
            try:
                uid = request.session.authenticate(db, login, password)
            except TypeError:
                pass
            except AccessDenied:
                raise
            except Exception as e:
                _logger.warning("authenticate(db, login, password) gagal: %s", e)

        # ── Strategi 3: request.session.authenticate (Odoo 16, tanpa db) ──
        if not uid:
            try:
                uid = request.session.authenticate(login, password)
            except TypeError:
                pass
            except AccessDenied:
                raise
            except Exception as e:
                _logger.warning("authenticate(login, password) gagal: %s", e)

        # ── Strategi 4: res.users._login (Odoo 19) ──
        if not uid:
            try:
                credential = {'type': 'password', 'login': login, 'password': password}
                wsgienv = {
                    'interactive': True,
                    'base_location': request.httprequest.url_root.rstrip('/'),
                    'HTTP_HOST': request.httprequest.environ['HTTP_HOST'],
                    'REMOTE_ADDR': request.httprequest.environ['REMOTE_ADDR'],
                }
                auth_info = request.env['res.users'].sudo()._login(credential, wsgienv)
                if auth_info and isinstance(auth_info, dict):
                    uid = auth_info.get('uid')
            except TypeError:
                pass
            except AccessDenied:
                raise
            except Exception as e:
                _logger.warning("_login(credential, wsgienv) gagal: %s", e)

        # ── Strategi 5: res.users._login langsung (Odoo 16/17) ──
        if not uid:
            try:
                uid = request.env['res.users'].sudo()._login(db, login, password)
            except AccessDenied:
                raise
            except Exception as e:
                _logger.warning("_login(db, login, password) gagal: %s", e)

        if not uid:
            raise AccessDenied()

        # ── Set session manual agar browser tahu user sudah login ──
        request.session['login'] = login
        request.session['uid'] = int(uid)
        request.session['password'] = password

        # Refresh env dengan uid baru (Odoo 17+ API)
        try:
            request.update_env(user=int(uid))
        except Exception:
            pass

        return request.redirect(redirect)

    def _validate_registration_data(self, post, tipe):
        errors = {}

        if not post.get('nama_lengkap', '').strip():
            errors['nama_lengkap'] = 'Nama Lengkap wajib diisi'

        email = post.get('email', '').strip()
        if not email:
            errors['email'] = 'Email wajib diisi'
        else:
            if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
                errors['email'] = 'Format email tidak valid'
            else:
                # Cek di tabel registrasi (belum diapprove)
                existing_reg = request.env['sadaya.registration'].sudo().search([
                    ('email', '=', email), ('state', 'not in', ['rejected'])
                ], limit=1)
                if existing_reg:
                    errors['email'] = 'Email ini sudah terdaftar dalam sistem'
                else:
                    # Cek di res.users (sudah jadi user aktif)
                    existing_user = request.env['res.users'].sudo().search([
                        ('login', '=', email), ('active', 'in', [True, False])
                    ], limit=1)
                    if existing_user:
                        errors['email'] = 'Email ini sudah terdaftar sebagai pengguna aktif'

        password = post.get('password', '')
        if not password:
            errors['password'] = 'Kata sandi wajib diisi'
        else:
            from odoo.addons.sadaya_auth.models.sadaya_registration import SadayaRegistration
            pwd_errors = SadayaRegistration.validate_password(password)
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
            'nama_lengkap':   post.get('nama_lengkap', '').strip(),
            'email':          post.get('email', '').strip().lower(),
            'password':       post.get('password', ''),
            'whatsapp_narahubung': post.get('whatsapp_narahubung', '').strip(),
            'nik_narahubung': re.sub(r'\D', '', post.get('nik_narahubung', '')),
        }
        if tipe == 'badan_usaha':
            vals['nama_badan_usaha']    = post.get('nama_badan_usaha', '').strip()
            vals['telepon_badan_usaha'] = post.get('telepon_badan_usaha', '').strip()
        npwp = re.sub(r'\D', '', post.get('npwp_perusahaan', ''))
        if npwp:
            vals['npwp_perusahaan'] = npwp
        return vals
