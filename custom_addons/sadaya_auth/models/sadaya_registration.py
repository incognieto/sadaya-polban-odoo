# -*- coding: utf-8 -*-
import re
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class SadayaRegistration(models.Model):
    """
    Model pendaftaran Sadaya.
    Mendukung dua tipe: Badan Usaha dan Perorangan.
    """
    _name = 'sadaya.registration'
    _description = 'Sadaya Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nama_lengkap'
    _order = 'create_date desc'

    # ── Umum ──────────────────────────────────────────
    tipe_pendaftar = fields.Selection([
        ('badan_usaha', 'Badan Usaha'),
        ('perorangan', 'Perorangan'),
    ], string='Tipe Pendaftar', required=True, default='perorangan', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Menunggu Verifikasi'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ], string='Status', default='draft', tracking=True)

    # ── Badan Usaha ────────────────────────────────────
    nama_badan_usaha = fields.Char(string='Nama Badan Usaha')
    telepon_badan_usaha = fields.Char(string='Telepon Badan Usaha')
    npwp_perusahaan = fields.Char(string='Nomor NPWP Perusahaan')
    bukti_npwp = fields.Binary(string='Bukti NPWP', attachment=True)
    bukti_npwp_filename = fields.Char(string='Nama File NPWP')

    # ── Narahubung / Perorangan ────────────────────────
    nama_lengkap = fields.Char(string='Nama Lengkap Narahubung', required=True)
    email = fields.Char(string='Email', required=True)
    whatsapp_narahubung = fields.Char(string='Nomor WhatsApp', required=True)
    nik_narahubung = fields.Char(string='Nomor NIK', required=True)
    swafoto_ktp = fields.Binary(string='Swafoto Memegang KTP', attachment=True)
    swafoto_ktp_filename = fields.Char(string='Nama File Swafoto')

    # ── Password (disimpan sementara, dihapus setelah user dibuat) ──
    password = fields.Char(string='Kata Sandi', groups='base.group_system')

    # ── Relasi ────────────────────────────────────────
    user_id = fields.Many2one('res.users', string='User Terkait',
                              readonly=True, ondelete='set null')
    rejection_reason = fields.Text(string='Alasan Penolakan')

    # ══════════════════════════════════════════════════
    # CONSTRAINTS
    # ══════════════════════════════════════════════════

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if not rec.email:
                continue
            pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, rec.email):
                raise ValidationError(_('Format email tidak valid: %s') % rec.email)
            existing = self.search([
                ('email', '=', rec.email),
                ('id', '!=', rec.id),
                ('state', 'not in', ['rejected']),
            ])
            if existing:
                raise ValidationError(_('Email %s sudah terdaftar.') % rec.email)

    @api.constrains('nik_narahubung')
    def _check_nik(self):
        for rec in self:
            if rec.nik_narahubung:
                nik = re.sub(r'\D', '', rec.nik_narahubung)
                if len(nik) != 16:
                    raise ValidationError(_('NIK harus terdiri dari 16 digit angka.'))

    @api.constrains('npwp_perusahaan')
    def _check_npwp(self):
        for rec in self:
            if rec.npwp_perusahaan:
                npwp = re.sub(r'\D', '', rec.npwp_perusahaan)
                if len(npwp) != 16:
                    raise ValidationError(_('NPWP harus terdiri dari 16 digit angka.'))

    @api.constrains('whatsapp_narahubung')
    def _check_whatsapp(self):
        for rec in self:
            if not rec.whatsapp_narahubung:
                continue
            wa = re.sub(r'\D', '', rec.whatsapp_narahubung)
            if len(wa) < 12:
                raise ValidationError(_('Nomor WhatsApp minimal 12 digit.'))

    # ══════════════════════════════════════════════════
    # STATIC HELPER
    # ══════════════════════════════════════════════════

    @staticmethod
    def validate_password(password):
        """Return list of error strings; empty = valid."""
        errors = []
        if len(password) < 8:
            errors.append('Minimal 8 karakter')
        if not re.search(r'[0-9]', password):
            errors.append('Minimal satu angka')
        if not re.search(r'[A-Z]', password):
            errors.append('Minimal satu huruf besar')
        if not re.search(r'[a-z]', password):
            errors.append('Minimal satu huruf kecil')
        return errors

    # ══════════════════════════════════════════════════
    # ACTIONS
    # ══════════════════════════════════════════════════

    def action_submit(self):
        for rec in self:
            rec.state = 'pending'
            rec.message_post(body=_('Pendaftaran diajukan untuk verifikasi.'))

    def action_approve(self):
        for rec in self:
            if rec.state != 'pending':
                raise UserError(_('Hanya registrasi berstatus Menunggu Verifikasi yang dapat disetujui.'))

            display_name = rec.nama_badan_usaha if rec.tipe_pendaftar == 'badan_usaha' else rec.nama_lengkap
            user_vals = {
                'name': display_name,
                'login': rec.email,
                'email': rec.email,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                'active': True,
            }
            user = self.env['res.users'].sudo().create(user_vals)
            if rec.password:
                user.sudo().write({'password': rec.password})

            rec.write({
                'state': 'approved',
                'user_id': user.id,
                'password': False,          # hapus password plaintext
            })
            rec.message_post(body=_('Registrasi disetujui. Akun pengguna telah dibuat.'))

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec.message_post(body=_('Registrasi ditolak. Alasan: %s') % (rec.rejection_reason or '-'))

    def action_reset_draft(self):
        self.write({'state': 'draft'})
