import base64

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
			{'name': 'nama_lengkap', 'label': 'Nama Lengkap', 'type': 'text'},
			{'name': 'nomor_hp', 'label': 'Nomor HP', 'type': 'text'},
			{'name': 'nik', 'label': 'NIK', 'type': 'text'},
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
			{'name': 'name', 'label': 'Keterangan Saham', 'type': 'text'},
		],
	},
	'personalia': {
		'title': 'Personalia',
		'description': 'Tenaga ahli dan pendukung.',
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
			{'name': 'nama', 'label': 'Nama', 'type': 'text'},
			{'name': 'nik', 'label': 'NIK', 'type': 'text'},
			{'name': 'tempat_lahir', 'label': 'Tempat Lahir', 'type': 'text'},
			{'name': 'tanggal_lahir', 'label': 'Tanggal Lahir', 'type': 'date'},
			{'name': 'jenjang_pendidikan', 'label': 'Jenjang Pendidikan', 'type': 'text'},
			{'name': 'program_studi', 'label': 'Program Studi', 'type': 'text'},
			{'name': 'posisi', 'label': 'Posisi', 'type': 'text'},
			{'name': 'scan_ktp', 'label': 'Scan KTP', 'type': 'binary', 'full_width': True},
			{'name': 'scan_ijazah', 'label': 'Scan Ijazah', 'type': 'binary', 'full_width': True},
			{'name': 'cv_tanggal', 'label': 'Tanggal CV', 'type': 'date'},
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
			{'name': 'npwp', 'label': 'NPWP', 'type': 'text'},
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
			{'name': 'kategori_id', 'label': 'Kategori DPT', 'type': 'many2one', 'required': True, 'options': []},
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
	config['fields'] = [dict(field) for field in base_config['fields']]
	if form_key == 'pendaftaran_dpt':
		categories = request.env['sadaya_mitra.kategori.dpt'].sudo().search([])
		options = [
			{'id': cat.id, 'label': cat.nama_kategori or ('Kategori %s' % cat.id)}
			for cat in categories
		]
		for field in config['fields']:
			if field['name'] == 'kategori_id':
				field['options'] = options
	return config


class SadayaMitraWebsite(http.Controller):
	@http.route('/sadaya_mitra/lanjutan', auth='public', website=True, methods=['GET'])
	def lanjutan_landing(self, **kwargs):
		forms = []
		for key in FORM_ORDER:
			config = FORM_CONFIG.get(key)
			if not config:
				continue
			forms.append({
				'key': key,
				'title': config.get('title', key),
				'description': config.get('description', ''),
				'url': '/sadaya_mitra/lanjutan/%s' % key,
			})
		return request.render('sadaya_mitra.sadaya_mitra_lanjutan_landing', {
			'forms': forms,
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
		values = {
			'jenis_penyedia': post.get('jenis_penyedia') or False,
			'nama_badan_usaha': post.get('nama_badan_usaha') or False,
			'email': post.get('email') or False,
			'nomor_telepon': post.get('nomor_telepon') or False,
			'nomor_whatsapp': post.get('nomor_whatsapp') or False,
			'narahubung': post.get('narahubung') or False,
			'alamat': post.get('alamat') or False,
			'kualifikasi_usaha': post.get('kualifikasi_usaha') or False,
			'masa_berlaku_domisili': post.get('masa_berlaku_domisili') or False,
		}

		password = post.get('password') or ''
		password_confirm = post.get('password_confirm') or ''

		errors = []
		if not values['jenis_penyedia']:
			errors.append('Jenis penyedia wajib diisi.')
		if not values['nama_badan_usaha']:
			errors.append('Nama badan usaha wajib diisi.')
		if not values['email']:
			errors.append('Email wajib diisi.')
		if not password:
			errors.append('Kata sandi wajib diisi.')
		if password and password != password_confirm:
			errors.append('Konfirmasi kata sandi tidak sama.')

		scan_file = request.httprequest.files.get('scan_domisili')
		if scan_file and scan_file.filename:
			values['scan_domisili'] = base64.b64encode(scan_file.read())

		if password:
			values['password'] = password

		if errors:
			return request.render('sadaya_mitra.sadaya_mitra_penyedia_form', {
				'values': post,
				'errors': errors,
			})

		request.env['sadaya_mitra.penyedia'].sudo().create(values)
		return request.redirect('/sadaya_mitra/lanjutan')

