import base64
import re

from odoo import http
from odoo.http import request


FORM_CONFIG = {
	'landasan_hukum': {
		'title': 'Landasan Hukum',
		'description': 'Akta, pengesahan, dan perubahan akta.',
		'model': 'sadaya_mitra.landasan.hukum',
		'unique_per_penyedia': True,
		'fields': [
			{'name': 'nomor_akta', 'label': 'Nomor Akta', 'type': 'text'},
			{'name': 'tanggal_akta', 'label': 'Tanggal Akta', 'type': 'date'},
			{'name': 'nama_notaris', 'label': 'Nama Notaris', 'type': 'text'},
			{'name': 'nomor_pengesahan', 'label': 'Nomor Pengesahan', 'type': 'text'},
			{'name': 'tanggal_pengesahan', 'label': 'Tanggal Pengesahan', 'type': 'date'},
			{'name': 'perubahan_akta', 'label': 'Perubahan Akta', 'type': 'textarea', 'full_width': True},
			{'name': 'scan_bukti', 'label': 'Scan Bukti (PDF)', 'type': 'binary', 'full_width': True},
		],
	},
	'pengurus': {
		'title': 'Pengurus',
		'description': 'Direksi dan komisaris.',
		'model': 'sadaya_mitra.pengurus',
		'fields': [
			{
				'name': 'jabatan',
				'label': 'Jabatan',
				'type': 'selection',
				'options': [
					{'value': 'direksi', 'label': 'Direksi'},
					{'value': 'komisaris', 'label': 'Komisaris'},
				],
			},
			{'name': 'nama_lengkap', 'label': 'Nama Lengkap', 'type': 'text', 'required': True},
			{'name': 'nomor_hp', 'label': 'Nomor HP', 'type': 'text', 'required': True},
			{'name': 'nik', 'label': 'NIK', 'type': 'text', 'required': True, 'pattern': r'^\d{16}$', 'maxlength': 16, 'placeholder': '16 digit angka', 'invalid_feedback': 'NIK wajib diisi dan harus tepat 16 digit angka.'},
			{'name': 'scan_ktp', 'label': 'Scan KTP', 'type': 'binary', 'full_width': True},
		],
	},
	'izin_usaha': {
		'title': 'Izin Usaha',
		'description': 'NIB, SBU, dan dokumen izin lainnya.',
		'model': 'sadaya_mitra.izin.usaha',
		'fields': [
			{
				'name': 'tipe_izin',
				'label': 'Tipe Izin',
				'type': 'selection',
				'options': [
					{'value': 'nib', 'label': 'NIB'},
					{'value': 'sbu', 'label': 'SBU'},
					{'value': 'lainnya', 'label': 'Lainnya'},
				],
			},
			{'name': 'nama_izin', 'label': 'Nama/Judul Izin', 'type': 'text'},
			{'name': 'nomor_izin', 'label': 'Nomor Izin', 'type': 'text'},
			{'name': 'scan_dokumen', 'label': 'Scan Dokumen', 'type': 'binary', 'full_width': True},
			{'name': 'masa_berlaku', 'label': 'Masa Berlaku', 'type': 'date'},
		],
	},
	'sertifikat_perusahaan': {
		'title': 'Sertifikat Perusahaan',
		'description': 'Data sertifikat yang dimiliki perusahaan.',
		'model': 'sadaya_mitra.sertifikat.perusahaan',
		'fields': [
			{'name': 'name', 'label': 'Nama Sertifikat', 'type': 'text'},
		],
	},
	'saham': {
		'title': 'Kepemilikan Saham',
		'description': 'Informasi kepemilikan saham.',
		'model': 'sadaya_mitra.saham',
		'fields': [
			{'name': 'susunan', 'label': 'Susunan', 'type': 'text'},
			{'name': 'nik', 'label': 'NIK', 'type': 'text', 'required': True, 'pattern': r'^\d{16}$', 'maxlength': 16, 'placeholder': '16 digit angka', 'invalid_feedback': 'NIK wajib diisi dan harus tepat 16 digit angka.'},
			{'name': 'posisi', 'label': 'Posisi', 'type': 'text'},
		],
	},
	'personalia': {
		'title': 'Personalia',
		'description': 'Tenaga ahli dan pendukung beserta pengalaman & sertifikat.',
		'model': 'sadaya_mitra.personalia',
		'fields': [
			{
				'name': 'tipe_personalia',
				'label': 'Tipe Personalia',
				'type': 'selection',
				'options': [
					{'value': 'ahli', 'label': 'Ahli'},
					{'value': 'pendukung', 'label': 'Pendukung'},
				],
			},
			{'name': 'tenaga_ahli', 'label': 'Tenaga Ahli', 'type': 'text'},
			{'name': 'nik', 'label': 'NIK', 'type': 'text', 'required': True, 'pattern': r'^\d{16}$', 'maxlength': 16, 'placeholder': '16 digit angka', 'invalid_feedback': 'NIK wajib diisi dan harus tepat 16 digit angka.'},
			{'name': 'tempat_lahir', 'label': 'Tempat Lahir', 'type': 'text'},
			{'name': 'tanggal_lahir', 'label': 'Tanggal Lahir', 'type': 'date'},
			{'name': 'jenjang_pendidikan', 'label': 'Jenjang Pendidikan', 'type': 'text'},
			{'name': 'program_studi', 'label': 'Program Studi', 'type': 'text'},
			{'name': 'posisi', 'label': 'Posisi', 'type': 'text'},
			{'name': 'scan_ktp', 'label': 'Scan KTP', 'type': 'binary', 'full_width': True},
			{'name': 'scan_ijazah', 'label': 'Scan Ijazah', 'type': 'binary', 'full_width': True},
			{'name': 'cv_pdf', 'label': 'CV (PDF)', 'type': 'binary', 'full_width': True},
			{'name': 'cv_tanggal', 'label': 'Tanggal CV', 'type': 'date'},
			{'name': 'pengalaman', 'label': 'Pengalaman', 'type': 'text'},
			{'name': 'bukti_pengalaman', 'label': 'Bukti Pengalaman (PDF)', 'type': 'binary', 'full_width': True},
			{'name': 'nama_sertifikat', 'label': 'Nama Sertifikat', 'type': 'text'},
			{'name': 'bukti_sertifikat', 'label': 'Bukti Sertifikat (PDF)', 'type': 'binary', 'full_width': True},
		],
	},
	'kantor': {
		'title': 'Kantor',
		'description': 'Alamat atau data kantor.',
		'model': 'sadaya_mitra.kantor',
		'fields': [
			{'name': 'name', 'label': 'Keterangan Kantor', 'type': 'text'},
		],
	},
	'fasilitas': {
		'title': 'Fasilitas',
		'description': 'Fasilitas yang dimiliki.',
		'model': 'sadaya_mitra.fasilitas',
		'fields': [
			{'name': 'name', 'label': 'Keterangan Fasilitas', 'type': 'text'},
		],
	},
	'pengalaman_perusahaan': {
		'title': 'Pengalaman Perusahaan',
		'description': 'Daftar pengalaman proyek.',
		'model': 'sadaya_mitra.pengalaman.perusahaan',
		'fields': [
			{'name': 'name', 'label': 'Keterangan Pengalaman', 'type': 'text'},
		],
	},
	'keuangan': {
		'title': 'Keuangan',
		'description': 'Data rekening dan laporan keuangan.',
		'model': 'sadaya_mitra.keuangan',
		'unique_per_penyedia': True,
		'fields': [
			{'name': 'nama_pemilik_rekening', 'label': 'Nama Pemilik Rekening', 'type': 'text'},
			{'name': 'nomor_rekening', 'label': 'Nomor Rekening', 'type': 'text'},
			{'name': 'kode_bank', 'label': 'Kode Bank', 'type': 'text'},
			{'name': 'nama_bank', 'label': 'Nama Bank', 'type': 'text'},
			{'name': 'scan_buku_rekening', 'label': 'Scan Buku Rekening', 'type': 'binary', 'full_width': True},
			{'name': 'scan_laporan_keuangan', 'label': 'Scan Laporan Keuangan', 'type': 'binary', 'full_width': True},
			{'name': 'masa_berlaku_laporan', 'label': 'Masa Berlaku Laporan', 'type': 'date'},
			{'name': 'scan_laporan_audited', 'label': 'Scan Laporan Audited', 'type': 'binary', 'full_width': True},
			{'name': 'masa_berlaku_audited', 'label': 'Masa Berlaku Audited', 'type': 'date'},
		],
	},
	'pajak': {
		'title': 'Pajak',
		'description': 'Dokumen pajak dan NPWP.',
		'model': 'sadaya_mitra.pajak',
		'fields': [
			{'name': 'npwp', 'label': 'NPWP', 'type': 'text', 'required': True, 'pattern': r'^(\d{15}|\d{16})$', 'maxlength': 16, 'placeholder': '15 atau 16 digit angka', 'invalid_feedback': 'NPWP wajib diisi dan harus tepat 15 atau 16 digit angka.'},
			{'name': 'bukti_kswp', 'label': 'Bukti KSWP', 'type': 'binary', 'full_width': True},
			{'name': 'bukti_spt', 'label': 'Bukti SPT', 'type': 'binary', 'full_width': True},
			{'name': 'bukti_bebas_pph23', 'label': 'Bukti Bebas PPh23', 'type': 'binary', 'full_width': True},
			{'name': 'bukti_pp23', 'label': 'Bukti PPh23', 'type': 'binary', 'full_width': True},
			{'name': 'bukti_non_pkp', 'label': 'Bukti Non PKP', 'type': 'binary', 'full_width': True},
		],
	},
	'pendaftaran_dpt': {
		'title': 'Pendaftaran DPT',
		'description': 'Status dan kategori pendaftaran DPT.',
		'model': 'sadaya_mitra.pendaftaran.dpt',
		'fields': [
			{
				'name': 'kategori_id',
				'label': 'Kategori DPT',
				'type': 'selection',
				'required': True,
				'options': [
					{'value': 'barang', 'label': 'Barang'},
					{'value': 'jasa', 'label': 'Jasa'},
					{'value': 'pekerjaan_konstruksi', 'label': 'Pekerjaan Konstruksi'},
					{'value': 'jasa_konsultasi', 'label': 'Jasa Konsultasi'},
					{'value': 'barang_printil', 'label': 'Barang Printil'},
					{'value': 'jasa_lainnya', 'label': 'Jasa Lainnya'},
				],
			},
			{
				'name': 'status_proses',
				'label': 'Status Proses',
				'type': 'selection',
				'options': [
					{'value': 'pendaftaran', 'label': 'Pendaftaran'},
					{'value': 'verifikasi', 'label': 'Verifikasi'},
					{'value': 'perbaikan', 'label': 'Perbaikan'},
					{'value': 'evaluasi', 'label': 'Evaluasi'},
					{'value': 'pengumuman', 'label': 'Pengumuman'},
				],
			},
			{'name': 'tanggal_daftar', 'label': 'Tanggal Daftar', 'type': 'datetime'},
			{'name': 'waktu_verifikasi', 'label': 'Waktu Verifikasi', 'type': 'datetime'},
			{
				'name': 'hasil_akhir',
				'label': 'Hasil Akhir',
				'type': 'selection',
				'options': [
					{'value': 'terpilih', 'label': 'Terpilih'},
					{'value': 'tidak', 'label': 'Tidak'},
				],
			},
			{'name': 'catatan_perbaikan', 'label': 'Catatan Perbaikan', 'type': 'textarea', 'full_width': True},
		],
	},
	'tte': {
		'title': 'Pengajuan TTE',
		'description': 'Email, PIN, dan surat kuasa.',
		'model': 'sadaya_mitra.tte',
		'fields': [
			{'name': 'email', 'label': 'Email', 'type': 'text'},
			{'name': 'pin', 'label': 'PIN', 'type': 'text'},
			{'name': 'surat_kuasa', 'label': 'Surat Kuasa', 'type': 'binary', 'full_width': True},
			{
				'name': 'status_verifikasi',
				'label': 'Status Verifikasi',
				'type': 'selection',
				'options': [
					{'value': 'draft', 'label': 'Draft'},
					{'value': 'verifikasi', 'label': 'Verifikasi'},
					{'value': 'aktif', 'label': 'Aktif'},
				],
			},
		],
	},
}


FORM_ORDER = [
	'landasan_hukum',
	'pengurus',
	'izin_usaha',
	'sertifikat_perusahaan',
	'saham',
	'personalia',
	'kantor',
	'fasilitas',
	'pengalaman_perusahaan',
	'keuangan',
	'pajak',
	'pendaftaran_dpt',
	'tte',
]

# Daftar field teks wajib di form pendaftaran penyedia
PENYEDIA_REQUIRED_FIELDS = [
    {'name': 'jenis_penyedia',         'label': 'Jenis Penyedia'},
    {'name': 'nama_badan_usaha',       'label': 'Nama Badan Usaha'},
    {'name': 'email',                  'label': 'Email'},
    {'name': 'nomor_telepon',          'label': 'Nomor Telepon'},
    {'name': 'nomor_whatsapp',         'label': 'Nomor WhatsApp'},
    {'name': 'narahubung',             'label': 'Nama Narahubung'},
    {'name': 'nomor_nik_narahubung',   'label': 'NIK Narahubung', 'nik': True},
    {'name': 'alamat',                 'label': 'Alamat'},
    {'name': 'nomor_npwp_perusahaan',  'label': 'Nomor NPWP Perusahaan', 'npwp': True},
]

# Daftar file wajib di form pendaftaran penyedia
PENYEDIA_REQUIRED_FILES = [
    {'name': 'swafoto_narahubung', 'label': 'Swafoto Narahubung', 'accept': 'image/png, image/jpeg'},
    {'name': 'bukti_npwp',         'label': 'Bukti NPWP', 'accept': 'application/pdf'},
]

def _normalize_datetime(value):
	if not value:
		return False
	if 'T' in value:
		if len(value) == 16:
			return value.replace('T', ' ') + ':00'
		return value.replace('T', ' ')
	return value


def _build_form_config(form_key):
	base_config = FORM_CONFIG.get(form_key)
	if not base_config:
		return None
	config = dict(base_config)
	config['key'] = form_key
	
	# Make all fields required dynamically to match penyedia form validation
	config['fields'] = []
	for field in base_config['fields']:
		new_field = dict(field)
		new_field['required'] = True
		config['fields'].append(new_field)


	return config


class SadayaMitraWebsite(http.Controller):
	@http.route('/sadaya_mitra/lanjutan', auth='public', website=True, methods=['GET'])
	def lanjutan_landing(self, **kwargs):
		email = request.session.get('penyedia_email')
		penyedia = None
		if email:
			penyedia = request.env['sadaya_mitra.penyedia'].sudo().search([('email', '=', email)], limit=1)
			
		forms = []
		completed_count = 0
		for key in FORM_ORDER:
			config = FORM_CONFIG.get(key)
			if not config:
				continue
				
			is_completed = False
			if penyedia:
				model = request.env[config['model']].sudo()
				count = model.search_count([('penyedia_id', '=', penyedia.id)])
				is_completed = count > 0
				if is_completed:
					completed_count += 1
					
			forms.append({
				'key': key,
				'title': config.get('title', key),
				'description': config.get('description', ''),
				'url': '/sadaya_mitra/lanjutan/%s' % key,
				'is_completed': is_completed,
			})
			
		total_forms = len(FORM_ORDER)
		progress_percent = int((completed_count / total_forms) * 100) if total_forms > 0 else 0

		return request.render('sadaya_mitra.sadaya_mitra_lanjutan_landing', {
			'forms': forms,
			'penyedia_email': email,
			'completed_count': completed_count,
			'total_forms': total_forms,
			'progress_percent': progress_percent,
		})

	@http.route('/sadaya_mitra/lanjutan/set_email', auth='public', website=True, methods=['POST'], csrf=True)
	def lanjutan_set_email(self, **post):
		email = post.get('email')
		if email:
			request.session['penyedia_email'] = email
		return request.redirect('/sadaya_mitra/lanjutan')

	@http.route('/sadaya_mitra/status', auth='public', website=True, methods=['GET'])
	def status_pendaftaran(self, **kwargs):
		email = request.session.get('penyedia_email')
		if not email:
			return request.redirect('/sadaya_mitra/lanjutan')
			
		penyedia = request.env['sadaya_mitra.penyedia'].sudo().search([('email', '=', email)], limit=1)
		if not penyedia:
			return request.redirect('/sadaya_mitra/lanjutan')

		completed_count = 0
		for key in FORM_ORDER:
			config = FORM_CONFIG.get(key)
			if config:
				model = request.env[config['model']].sudo()
				if model.search_count([('penyedia_id', '=', penyedia.id)]) > 0:
					completed_count += 1
					
		is_complete = completed_count == len(FORM_ORDER)
		
		return request.render('sadaya_mitra.sadaya_mitra_status_pendaftaran', {
			'is_complete': is_complete,
			'penyedia_email': email,
			'completed_count': completed_count,
			'total_forms': len(FORM_ORDER)
		})

	@http.route('/sadaya_mitra/lanjutan/<string:form_key>', auth='public', website=True, methods=['GET'])
	def lanjutan_form(self, form_key, **kwargs):
		config = _build_form_config(form_key)
		if not config:
			return request.not_found()
		return request.render('sadaya_mitra.sadaya_mitra_lanjutan_form', {
			'config': config,
			'values': kwargs,
			'errors': [],
			'session_email': request.session.get('penyedia_email', ''),
		})

	@http.route('/sadaya_mitra/lanjutan/<string:form_key>/submit', auth='public', website=True, methods=['POST'], csrf=True)
	def lanjutan_submit(self, form_key, **post):
		config = _build_form_config(form_key)
		if not config:
			return request.not_found()

		errors = []
		email = post.get('penyedia_email')
		if not email:
			errors.append('Email penyedia wajib diisi.')
			penyedia = None
		else:
			penyedia = request.env['sadaya_mitra.penyedia'].sudo().search([
				('email', '=', email)
			], limit=1)
			if not penyedia:
				errors.append('Email penyedia tidak ditemukan.')

		values = {}
		if penyedia:
			values['penyedia_id'] = penyedia.id

		for field in config['fields']:
			field_name = field['name']
			field_type = field.get('type')
			if field_type == 'binary':
				file_obj = request.httprequest.files.get(field_name)
				if file_obj and file_obj.filename:
					values[field_name] = base64.b64encode(file_obj.read())
				continue
			value = post.get(field_name)
			if field_type == 'many2one':
				values[field_name] = int(value) if value else False
			elif field_type == 'datetime':
				values[field_name] = _normalize_datetime(value)
			else:
				values[field_name] = value or False
			if field.get('required') and not values.get(field_name):
				errors.append('%s wajib diisi.' % field.get('label', field_name))

		if errors:
			return request.render('sadaya_mitra.sadaya_mitra_lanjutan_form', {
				'config': config,
				'values': post,
				'errors': errors,
			})

		model = request.env[config['model']].sudo()
		if config.get('unique_per_penyedia') and penyedia:
			existing = model.search([('penyedia_id', '=', penyedia.id)], limit=1)
			if existing:
				existing.write(values)
				record = existing
			else:
				record = model.create(values)
		else:
			record = model.create(values)

		# Save email to session in case it was not set
		request.session['penyedia_email'] = email

		return request.render('sadaya_mitra.sadaya_mitra_lanjutan_success', {
			'record': record,
			'config': config,
		})
	@http.route('/sadaya_mitra/penyedia', auth='public', website=True, methods=['GET'])
	def penyedia_form(self, **kwargs):
		return request.render('sadaya_mitra.sadaya_mitra_penyedia_form', {
			'values': kwargs,
			'errors': [],
		})

	@http.route('/sadaya_mitra/penyedia/submit', auth='public', website=True, methods=['POST'], csrf=True)
	def penyedia_submit(self, **post):
		errors = []

		# ── Validasi field teks wajib ──────────────────────────────────────
		for field_def in PENYEDIA_REQUIRED_FIELDS:
			raw = (post.get(field_def['name']) or '').strip()
			if not raw:
				errors.append('%s wajib diisi.' % field_def['label'])
			elif field_def.get('nik'):
				if not re.match(r'^\d{16}$', raw):
					errors.append(
						'%s wajib diisi dan harus tepat 16 digit angka.'
						% field_def['label']
					)
			elif field_def.get('npwp'):
				if not re.match(r'^(\d{15}|\d{16})$', raw):
					errors.append(
						'%s wajib diisi dan harus tepat 15 atau 16 digit angka.'
						% field_def['label']
					)
					
		# ── Validasi kata sandi ────────────────────────────────────────────
		password = (post.get('kata_sandi') or '').strip()
		password_confirm = (post.get('kata_sandi_confirm') or '').strip()
		if not password:
			errors.append('Kata sandi wajib diisi.')
		if not password_confirm:
			errors.append('Konfirmasi kata sandi wajib diisi.')
		if password and password_confirm and password != password_confirm:
			errors.append('Kata sandi dan konfirmasi kata sandi harus sama.')

		# ── Validasi file wajib ────────────────────────────────────────────
		file_values = {}
		for file_def in PENYEDIA_REQUIRED_FILES:
			file_obj = request.httprequest.files.get(file_def['name'])
			if not file_obj or not file_obj.filename:
				errors.append('%s wajib diunggah.' % file_def['label'])
			elif file_def.get('accept'):
				accepted = file_def['accept'] if isinstance(file_def['accept'], list) else [a.strip() for a in file_def['accept'].split(',')]
				if file_obj.mimetype not in accepted:
					errors.append('%s harus berformat %s (diunggah: %s).' % (
						file_def['label'], ', '.join(accepted), file_obj.mimetype
					))
				else:
					file_values[file_def['name']] = base64.b64encode(file_obj.read())
			else:
				file_values[file_def['name']] = base64.b64encode(file_obj.read())
				
		# ── Kembalikan form jika ada error ─────────────────────────────────
		if errors:
			return request.render('sadaya_mitra.sadaya_mitra_penyedia_form', {
				'values': post,
				'errors': errors,
			})

		# ── Simpan password untuk user creation ────────────────────────────
		password = post.get('kata_sandi')
		email = post.get('email')

		# ── Simpan data penyedia (tanpa password) ──────────────────────────
		values = {
			'jenis_penyedia':        post.get('jenis_penyedia') or False,
			'nama_badan_usaha':      post.get('nama_badan_usaha') or False,
			'email':                 email or False,
			'nomor_telepon':         post.get('nomor_telepon') or False,
			'nomor_whatsapp':        post.get('nomor_whatsapp') or False,
			'narahubung':            post.get('narahubung') or False,
			'nomor_nik_narahubung':  post.get('nomor_nik_narahubung') or False,
			'alamat':                post.get('alamat') or False,
			'nomor_npwp_perusahaan': post.get('nomor_npwp_perusahaan') or False,
		}
		values.update(file_values)

		penyedia = request.env['sadaya_mitra.penyedia'].sudo().create(values)

		# ── Buat user account dengan password ───────────────────────────────
		request.env['res.users'].sudo().create({
			'name': post.get('narahubung') or post.get('nama_badan_usaha'),
			'login': email,
			'password': password,
			'email': email,
		})

		request.session['penyedia_email'] = email
		return request.redirect('/sadaya_mitra/lanjutan')