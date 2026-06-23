from odoo import fields, http
from odoo.http import request
from urllib.parse import quote_plus
import base64


class SadayaLangsungController(http.Controller):
	def _selection_options(self, record, field_name):
		field = record._fields.get(field_name)
		if not field:
			return []
		return [{"value": value, "label": label} for value, label in field.selection or []]

	def _safe_float(self, value):
		if value in (None, ""):
			return 0.0
		try:
			return float(str(value).replace(",", "."))
		except (TypeError, ValueError):
			return 0.0

	def _safe_int(self, value):
		if value in (None, ""):
			return 0
		try:
			return int(value)
		except (TypeError, ValueError):
			return 0

	def _safe_selection(self, value, options):
		allowed = {item["value"] for item in options}
		if value in allowed:
			return value
		return False

	def _format_money(self, amount):
		amount = amount or 0.0
		return "Rp {:,.0f}".format(amount).replace(",", ".")

	def _redirect_with_message(self, path, success=None, error=None):
		if success:
			return request.redirect(f"{path}?success={quote_plus(success)}")
		if error:
			return request.redirect(f"{path}?error={quote_plus(error)}")
		return request.redirect(path)

	def _paket_actions(self, record):
		actions = []
		user = request.env.user
		is_ppk = user.has_group('sadaya_langsung.group_langsung_ppk')
		is_pp = user.has_group('sadaya_langsung.group_langsung_pp')
		is_pphp = user.has_group('sadaya_langsung.group_langsung_pphp')
		is_user = user.has_group('sadaya_langsung.group_langsung_unit_kerja')

		if record.status_paket == "draft" and is_ppk:
			actions.append({"key": "ajukan", "label": "Ajukan Persetujuan", "class": "btn-primary"})
		elif record.status_paket == "menunggu_persetujuan" and is_pp:
			actions.append({"key": "pengumuman", "label": "Publikasikan Pengumuman", "class": "btn-primary"})
			actions.append({"key": "revisi", "label": "Minta Revisi", "class": "btn-outline-warning"})
		elif record.status_paket == "pengumuman" and is_ppk:
			actions.append({"key": "buat_spk", "label": "Terbitkan SPK", "class": "btn-success"})
		elif record.status_paket == "spk_dibuat" and is_ppk:
			actions.append({"key": "pam", "label": "Pre-Award Meeting (PAM)", "class": "btn-primary"})
		elif record.status_paket == "pam" and is_ppk:
			actions.append({"key": "persiapan_kontrak", "label": "Persiapan Kontrak", "class": "btn-primary"})
		elif record.status_paket == "persiapan_kontrak" and is_ppk:
			actions.append({"key": "proses_kontrak", "label": "Proses Kontrak", "class": "btn-primary"})
		elif record.status_paket == "proses_kontrak" and is_ppk:
			actions.append({"key": "pelaksanaan", "label": "Mulai Pelaksanaan", "class": "btn-primary"})
		elif record.status_paket == "pelaksanaan" and is_pphp:
			actions.append({"key": "pemeriksaan", "label": "Pemeriksaan (PPHP)", "class": "btn-primary"})
		elif record.status_paket == "pemeriksaan" and is_user:
			actions.append({"key": "selesai", "label": "Selesai", "class": "btn-success"})
		elif record.status_paket == "selesai" and is_ppk:
			actions.append({"key": "addendum", "label": "Addendum Kontrak", "class": "btn-warning"})
		elif record.status_paket == "addendum_kontrak" and is_ppk:
			actions.append({"key": "selesai", "label": "Selesaikan Addendum", "class": "btn-success"})
		elif record.status_paket == "revisi" and is_ppk:
			actions.append({"key": "reset_draft", "label": "Reset ke Draft", "class": "btn-outline-secondary"})

		if record.status_paket not in ("selesai", "batal", "revisi") and is_ppk:
			actions.append({"key": "batal", "label": "Batalkan", "class": "btn-outline-danger"})
		if record.status_paket == "batal" and is_ppk:
			actions.append({"key": "reset_draft", "label": "Reset ke Draft", "class": "btn-outline-secondary"})
		return actions

	def _kontrak_actions(self, record):
		actions = []
		user = request.env.user
		is_ppk = user.has_group('sadaya_langsung.group_langsung_ppk')
		is_pphp = user.has_group('sadaya_langsung.group_langsung_pphp')

		if record.status_kontrak == "persiapan_kontrak" and is_ppk:
			actions.append({"key": "proses_kontrak", "label": "Proses Kontrak", "class": "btn-primary"})
		elif record.status_kontrak == "proses_kontrak" and is_pphp:
			actions.append({"key": "selesai_kontrak", "label": "Selesai Kontrak", "class": "btn-success"})
		elif record.status_kontrak == "selesai_kontrak" and is_ppk:
			actions.append({"key": "addendum", "label": "Addendum", "class": "btn-warning"})

		if record.status_kontrak not in ("selesai_kontrak", "revisi") and (is_ppk or is_pphp):
			actions.append({"key": "revisi", "label": "Revisi", "class": "btn-outline-secondary"})
		return actions

	def _group_count(self, item, field_name):
		return item.get("__count") or item.get(f"{field_name}_count") or 0

	def _format_date(self, value):
		if not value:
			return "-"
		return fields.Date.to_string(value)

	def _selection_label(self, record, field_name, value):
		field = record._fields.get(field_name)
		if not field:
			return value or "-"
		return dict(field.selection or []).get(value, value or "-")

	def _vendor_options(self):
		vendors = request.env["res.partner"].sudo().search(
			[("is_sadaya_mitra_vendor", "=", True)], order="name asc"
		)
		return [{"id": vendor.id, "name": vendor.name} for vendor in vendors]

	def _penawaran_actions(self, record):
		actions = []
		if record.status_penawaran == "diajukan":
			actions.append({"key": "tolak", "label": "Tolak", "class": "btn-outline-danger"})
		if record.status_penawaran != "dipilih":
			actions.append({"key": "pilih", "label": "Pilih Pemenang", "class": "btn-success"})
		if record.status_penawaran in ("ditolak", "dipilih"):
			actions.append({"key": "reset", "label": "Reset Status", "class": "btn-outline-secondary"})
		return actions

	def _build_penawaran_rows(self, records):
		rows = []
		for record in records:
			rows.append(
				{
					"id": record.id,
					"vendor": record.vendor_id.name,
					"harga_penawaran": self._format_money(record.harga_penawaran),
					"status_penawaran": self._selection_label(
						record, "status_penawaran", record.status_penawaran
					),
					"evaluasi_administrasi": record.evaluasi_administrasi or "",
					"evaluasi_teknis": record.evaluasi_teknis or "",
					"evaluasi_harga": record.evaluasi_harga or "",
					"lulus_evaluasi": "Lulus" if record.lulus_evaluasi else "Belum",
					"actions": self._penawaran_actions(record),
				}
			)
		return rows

	def _check_edit_permission(self):
		return (
			request.env.user.has_group('sadaya_langsung.group_langsung_ppk') or
			request.env.user.has_group('sadaya_langsung.group_langsung_pp')
		)

	def _build_paket_cards(self, records):
		cards = []
		Paket = request.env["sadaya_langsung.paket"]
		Penawaran = request.env["sadaya_langsung.penawaran"]
		is_editor = self._check_edit_permission()
		for record in records:
			status_options = self._selection_options(Paket, "status_paket")
			penawaran_records = record.penawaran_ids.sorted(lambda p: (p.harga_penawaran, p.id))
			cards.append(
				{
					"id": record.id,
					"name": record.name,
					"unit_pengusul": record.unit_pengusul or "-",
					"keterangan": record.keterangan or "",
					"tanggal_mulai": fields.Date.to_string(record.tanggal_mulai) if record.tanggal_mulai else "",
					"tanggal_selesai": fields.Date.to_string(record.tanggal_selesai) if record.tanggal_selesai else "",
					"status_code": record.status_paket,
					"status_options": status_options,
					"jenis_pengadaan": self._selection_label(
						record, "jenis_pengadaan", record.jenis_pengadaan
					),
					"jenis_pengadaan_code": record.jenis_pengadaan,
					"status_paket": self._selection_label(
						record, "status_paket", record.status_paket
					),
					"nilai_hps": self._format_money(record.nilai_hps),
					"nilai_hps_raw": record.nilai_hps or 0.0,
					"tanggal": self._format_date(record.tanggal),
					"tanggal_raw": fields.Date.to_string(record.tanggal) if record.tanggal else "",
					"vendor_pemenang_id": record.vendor_pemenang_id.id if record.vendor_pemenang_id else 0,
					"vendor_pemenang": record.vendor_pemenang_id.name
					if record.vendor_pemenang_id
					else "-",
					"penawaran_rows": self._build_penawaran_rows(penawaran_records),
					"item_rows": [
						{
							"id": item.id,
							"name": item.name,
							"deskripsi": item.deskripsi or "",
							"qty": item.qty,
							"satuan": item.satuan,
							"harga_satuan": item.harga_satuan,
							"subtotal": item.subtotal,
						}
						for item in record.item_ids.sorted(key=lambda r: r.id)
					],
					"evaluasi_options": self._selection_options(Penawaran, "evaluasi_administrasi"),
					"actions": self._paket_actions(record) if is_editor else [],
				}
			)
		return cards

	def _build_kontrak_cards(self, records):
		cards = []
		Kontrak = request.env["sadaya_langsung.kontrak"]
		for record in records:
			cards.append(
				{
					"id": record.id,
					"name": record.name,
					"paket": record.paket_id.name if record.paket_id else "-",
					"paket_id": record.paket_id.id if record.paket_id else 0,
					"pejabat_pembuat": record.pejabat_pembuat or "-",
					"penyedia": record.penyedia or "-",
					"status_code": record.status_kontrak,
					"status_options": self._selection_options(Kontrak, "status_kontrak"),
					"jenis_pengadaan_code": record.jenis_pengadaan,
					"status_kontrak": self._selection_label(
						record, "status_kontrak", record.status_kontrak
					),
					"nilai_hps": self._format_money(record.nilai_hps),
					"nilai_hps_raw": record.nilai_hps or 0.0,
					"tanggal": self._format_date(record.tanggal),
					"tanggal_raw": fields.Date.to_string(record.tanggal) if record.tanggal else "",
					"tanggal_mulai": fields.Date.to_string(record.tanggal_mulai) if record.tanggal_mulai else "",
					"tanggal_selesai": fields.Date.to_string(record.tanggal_selesai) if record.tanggal_selesai else "",
					"keterangan": record.keterangan or "",
					"actions": self._kontrak_actions(record),
				}
			)
		return cards

	def _get_user_vendor_partners(self):
		user = request.env.user
		emails = list(filter(None, [user.login, user.email, user.partner_id.email]))
		if not emails:
			return user.partner_id
		domain = ['|', ('id', '=', user.partner_id.id), '&', ('email', 'in', emails), ('is_sadaya_mitra_vendor', '=', True)]
		return request.env['res.partner'].sudo().search(domain)

	def _is_vendor_user(self):
		user = request.env.user
		if user.has_group('sadaya_langsung.group_sadaya_langsung_vendor'):
			return True
		vendor_partners = self._get_user_vendor_partners()
		if any(p.is_sadaya_mitra_vendor for p in vendor_partners):
			return True
		if 'vendor' in (user.login or '') or 'vendor' in (user.email or ''):
			return True
		return False

	def _get_dashboard_payload(self):
		Paket = request.env["sadaya_langsung.paket"].sudo()
		Kontrak = request.env["sadaya_langsung.kontrak"].sudo()

		is_vendor = self._is_vendor_user()
		paket_domain = []
		kontrak_domain = []
		if is_vendor:
			partner_ids = self._get_user_vendor_partners().ids
			paket_domain = [
				('penawaran_ids.vendor_id', 'in', partner_ids),
				('status_paket', 'not in', ['draft', 'menunggu_persetujuan', 'revisi'])
			]
			kontrak_domain = [('paket_id.vendor_pemenang_id', 'in', partner_ids)]

		paket_breakdown = Paket.read_group(
			paket_domain, ["status_paket"], ["status_paket"], lazy=False
		)
		kontrak_breakdown = Kontrak.read_group(
			kontrak_domain, ["status_kontrak"], ["status_kontrak"], lazy=False
		)

		return {
			"total_paket": Paket.search_count(paket_domain),
			"total_kontrak": Kontrak.search_count(kontrak_domain),
			"paket_aktif": Paket.search_count(
				paket_domain + [("status_paket", "not in", ["selesai", "batal"])]
			),
			"paket_selesai": Paket.search_count(paket_domain + [("status_paket", "=", "selesai")]),
			"kontrak_persiapan": Kontrak.search_count(
				kontrak_domain + [("status_kontrak", "=", "persiapan_kontrak")]
			),
			"kontrak_selesai": Kontrak.search_count(
				kontrak_domain + [("status_kontrak", "=", "selesai_kontrak")]
			),
			"recent_paket": self._build_paket_cards(
				Paket.search(paket_domain, order="tanggal desc, id desc", limit=5)
			),
			"recent_kontrak": self._build_kontrak_cards(
				Kontrak.search(kontrak_domain, order="tanggal desc, id desc", limit=5)
			),
			"paket_breakdown": [
				{
					"label": dict(Paket._fields["status_paket"].selection).get(
						item["status_paket"], item["status_paket"]
					),
					"count": self._group_count(item, "status_paket"),
				}
				for item in paket_breakdown
				if item.get("status_paket")
			],
			"kontrak_breakdown": [
				{
					"label": dict(Kontrak._fields["status_kontrak"].selection).get(
						item["status_kontrak"], item["status_kontrak"]
					),
					"count": self._group_count(item, "status_kontrak"),
				}
				for item in kontrak_breakdown
				if item.get("status_kontrak")
			],
		}

	@http.route("/sadaya-langsung", type="http", auth="user", website=True)
	def dashboard(self, **kwargs):
		return request.render(
			"sadaya_langsung.frontend_dashboard",
			{"active_page": "dashboard", **self._get_dashboard_payload()},
		)

	@http.route("/sadaya-langsung/paket", type="http", auth="user", website=True)
	def paket_page(self, **kwargs):
		Paket = request.env["sadaya_langsung.paket"].sudo()
		is_vendor = self._is_vendor_user()
		domain = []
		if is_vendor:
			partner_ids = self._get_user_vendor_partners().ids
			domain = [
				('penawaran_ids.vendor_id', 'in', partner_ids),
				('status_paket', 'not in', ['draft', 'menunggu_persetujuan', 'revisi'])
			]
		return request.render(
			"sadaya_langsung.frontend_paket_page",
			{
				"active_page": "paket",
				"notice_success": kwargs.get("success"),
				"notice_error": kwargs.get("error"),
				"paket_cards": self._build_paket_cards(
					Paket.search(domain, order="tanggal desc, id desc")
				),
				"total_paket": Paket.search_count([]),
				"jenis_pengadaan_options": self._selection_options(
					Paket, "jenis_pengadaan"
				),
				"status_paket_options": self._selection_options(Paket, "status_paket"),
				"vendor_options": self._vendor_options(),
			},
		)

	@http.route(
		"/sadaya-langsung/paket/create",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def create_paket(self, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_ppk'):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk membuat paket.")
		Paket = request.env["sadaya_langsung.paket"].sudo()
		jenis_options = self._selection_options(Paket, "jenis_pengadaan")
		values = {
			"name": post.get("name") or "Paket Baru",
			"unit_pengusul": post.get("unit_pengusul") or False,
			"jenis_pengadaan": self._safe_selection(
				post.get("jenis_pengadaan"), jenis_options
			),
			"nilai_hps": self._safe_float(post.get("nilai_hps")),
			"tanggal": post.get("tanggal") or False,
			"keterangan": post.get("keterangan") or False,
			"tanggal_mulai": post.get("tanggal_mulai") or False,
			"tanggal_selesai": post.get("tanggal_selesai") or False,
		}
		new = Paket.create(values)
		# Handle file uploads: dokumen_kak, dokumen_rab
		if request.httprequest.files:
			f_kak = request.httprequest.files.get("dokumen_kak")
			f_rab = request.httprequest.files.get("dokumen_rab")
			write_vals = {}
			if f_kak:
				data = f_kak.read()
				if data:
					write_vals["dokumen_kak"] = base64.b64encode(data).decode("utf-8")
					write_vals["filename_kak"] = getattr(f_kak, "filename", None)
			if f_rab:
				data = f_rab.read()
				if data:
					write_vals["dokumen_rab"] = base64.b64encode(data).decode("utf-8")
					write_vals["filename_rab"] = getattr(f_rab, "filename", None)
			if write_vals:
				try:
					new.sudo().write(write_vals)
				except Exception:
					pass
		return self._redirect_with_message(
			"/sadaya-langsung/paket", success="Paket berhasil ditambahkan"
		)

	@http.route(
		"/sadaya-langsung/paket/<int:paket_id>/update",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def update_paket(self, paket_id, **post):
		if not (request.env.user.has_group('sadaya_langsung.group_langsung_ppk') or request.env.user.has_group('sadaya_langsung.group_langsung_pp')):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk mengubah paket.")
		Paket = request.env["sadaya_langsung.paket"].sudo()
		record = Paket.browse(paket_id)
		if not record.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Paket tidak ditemukan"
			)

		jenis_options = self._selection_options(Paket, "jenis_pengadaan")
		status_options = self._selection_options(Paket, "status_paket")
		values = {
			"name": post.get("name") or record.name,
			"unit_pengusul": post.get("unit_pengusul") or False,
			"jenis_pengadaan": self._safe_selection(post.get("jenis_pengadaan"), jenis_options),
			"nilai_hps": self._safe_float(post.get("nilai_hps")),
			"tanggal": post.get("tanggal") or False,
			"tanggal_mulai": post.get("tanggal_mulai") or False,
			"tanggal_selesai": post.get("tanggal_selesai") or False,
			"keterangan": post.get("keterangan") or False,
		}
		status_input = self._safe_selection(post.get("status_paket"), status_options)
		if status_input:
			values["status_paket"] = status_input

		vendor_id = self._safe_int(post.get("vendor_pemenang_id"))
		values["vendor_pemenang_id"] = vendor_id or False

		try:
			record.write(values)
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))

		# Handle file uploads on update
		if request.httprequest.files:
			f_kak = request.httprequest.files.get("dokumen_kak")
			f_rab = request.httprequest.files.get("dokumen_rab")
			write_vals = {}
			if f_kak:
				data = f_kak.read()
				if data:
					write_vals["dokumen_kak"] = base64.b64encode(data).decode("utf-8")
					write_vals["filename_kak"] = getattr(f_kak, "filename", None)
			if f_rab:
				data = f_rab.read()
				if data:
					write_vals["dokumen_rab"] = base64.b64encode(data).decode("utf-8")
					write_vals["filename_rab"] = getattr(f_rab, "filename", None)
			if write_vals:
				try:
					record.sudo().write(write_vals)
				except Exception:
					pass

		return self._redirect_with_message(
			"/sadaya-langsung/paket", success="Paket berhasil diperbarui"
		)

	@http.route(
		"/sadaya-langsung/paket/<int:paket_id>/penawaran/create",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def create_penawaran(self, paket_id, **post):
		is_ppk = request.env.user.has_group('sadaya_langsung.group_langsung_ppk')
		is_pp = request.env.user.has_group('sadaya_langsung.group_langsung_pp')
		is_vendor = self._is_vendor_user()
		if not (is_ppk or is_pp or is_vendor):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk menambahkan penawaran.")
		paket = request.env["sadaya_langsung.paket"].sudo().browse(paket_id)
		if not paket.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Paket tidak ditemukan"
			)

		vendor_id = self._safe_int(post.get("vendor_id"))
		if not vendor_id:
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Vendor wajib dipilih"
			)

		values = {
			"paket_id": paket.id,
			"vendor_id": vendor_id,
			"harga_penawaran": self._safe_float(post.get("harga_penawaran")),
			"tanggal": post.get("tanggal") or False,
			"catatan": post.get("catatan") or False,
		}
		# Handle optional dokumen_penawaran file
		penawaran = None
		try:
			penawaran = request.env["sadaya_langsung.penawaran"].sudo().create(values)
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))
		if penawaran and request.httprequest.files:
			f_doc = request.httprequest.files.get("dokumen_penawaran")
			if f_doc:
				data = f_doc.read()
				if data:
					try:
						penawaran.sudo().write({
							"dokumen_penawaran": base64.b64encode(data).decode("utf-8"),
							"dokumen_filename": getattr(f_doc, "filename", None),
						})
					except Exception:
						pass

		return self._redirect_with_message(
			"/sadaya-langsung/paket", success="Penawaran vendor berhasil ditambahkan"
		)

	@http.route(
		"/sadaya-langsung/penawaran/<int:penawaran_id>/evaluate",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def evaluate_penawaran(self, penawaran_id, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_pp'):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk melakukan evaluasi.")
		Penawaran = request.env["sadaya_langsung.penawaran"].sudo()
		record = Penawaran.browse(penawaran_id)
		if not record.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Penawaran tidak ditemukan"
			)

		eval_options = self._selection_options(Penawaran, "evaluasi_administrasi")
		values = {
			"evaluasi_administrasi": self._safe_selection(
				post.get("evaluasi_administrasi"), eval_options
			),
			"evaluasi_teknis": self._safe_selection(post.get("evaluasi_teknis"), eval_options),
			"evaluasi_harga": self._safe_selection(post.get("evaluasi_harga"), eval_options),
		}
		try:
			record.write(values)
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))

		return self._redirect_with_message(
			"/sadaya-langsung/paket", success="Evaluasi penawaran diperbarui"
		)

	@http.route(
		"/sadaya-langsung/penawaran/<int:penawaran_id>/action",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def penawaran_action(self, penawaran_id, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_pp'):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk memproses penawaran ini.")
		action_map = {
			"pilih": "action_pilih_pemenang",
			"tolak": "action_tolak",
			"reset": "action_reset_masuk",
		}
		record = request.env["sadaya_langsung.penawaran"].sudo().browse(penawaran_id)
		if not record.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Penawaran tidak ditemukan"
			)
		action_key = post.get("action")
		method_name = action_map.get(action_key)
		if not method_name:
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Aksi penawaran tidak valid"
			)

		try:
			getattr(record, method_name)()
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))

		return self._redirect_with_message(
			"/sadaya-langsung/paket", success="Aksi penawaran berhasil diproses"
		)

	@http.route(
		"/sadaya-langsung/paket/<int:paket_id>/workflow",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def paket_workflow(self, paket_id, **post):
		action_key = post.get("action")
		user = request.env.user
		is_ppk = user.has_group('sadaya_langsung.group_langsung_ppk')
		is_pp = user.has_group('sadaya_langsung.group_langsung_pp')
		is_pphp = user.has_group('sadaya_langsung.group_langsung_pphp')
		is_user = user.has_group('sadaya_langsung.group_langsung_unit_kerja')

		allowed = False
		if action_key in ("ajukan", "buat_spk", "pam", "persiapan_kontrak", "proses_kontrak", "pelaksanaan", "addendum", "reset_draft", "batal"):
			allowed = is_ppk
		elif action_key in ("pengumuman", "revisi"):
			allowed = is_pp
		elif action_key == "pemeriksaan":
			allowed = is_pphp
		elif action_key == "selesai":
			allowed = is_user

		if not allowed:
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk melakukan aksi ini.")
		action_map = {
			"ajukan": "action_ajukan",
			"pengumuman": "action_pengumuman",
			"buat_spk": "action_buat_spk",
			"pam": "action_pam",
			"persiapan_kontrak": "action_persiapan_kontrak",
			"proses_kontrak": "action_proses_kontrak",
			"pelaksanaan": "action_pelaksanaan",
			"pemeriksaan": "action_pemeriksaan",
			"selesai": "action_selesai",
			"addendum": "action_addendum",
			"revisi": "action_revisi",
			"batal": "action_batal",
			"reset_draft": "action_reset_draft",
		}
		record = request.env["sadaya_langsung.paket"].sudo().browse(paket_id)
		if not record.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Paket tidak ditemukan"
			)
		action_key = post.get("action")
		method_name = action_map.get(action_key)
		if not method_name:
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Aksi paket tidak valid"
			)

		try:
			getattr(record, method_name)()
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))

		return self._redirect_with_message(
			"/sadaya-langsung/paket", success="Status paket berhasil diperbarui"
		)

	@http.route(
		"/sadaya-langsung/paket/<int:paket_id>/item/create",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def paket_item_create(self, paket_id, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_ppk'):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk menambah item.")
		Paket = request.env["sadaya_langsung.paket"].sudo()
		paket = Paket.browse(paket_id)
		if not paket.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/paket", error="Paket tidak ditemukan"
			)
		values = {
			"paket_id": paket.id,
			"name": post.get("name") or "Item",
			"deskripsi": post.get("deskripsi") or False,
			"qty": self._safe_float(post.get("qty")) or 0.0,
			"satuan": post.get("satuan") or False,
			"harga_satuan": self._safe_float(post.get("harga_satuan")) or 0.0,
		}
		try:
			request.env["sadaya_langsung.paket.line"].sudo().create(values)
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))
		return self._redirect_with_message("/sadaya-langsung/paket", success="Item berhasil ditambahkan")

	@http.route(
		"/sadaya-langsung/paket/<int:paket_id>/item/<int:item_id>/update",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def paket_item_update(self, paket_id, item_id, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_ppk'):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk mengubah item.")
		item = request.env["sadaya_langsung.paket.line"].sudo().browse(item_id)
		if not item.exists() or item.paket_id.id != paket_id:
			return self._redirect_with_message("/sadaya-langsung/paket", error="Item tidak ditemukan")
		values = {
			"name": post.get("name") or item.name,
			"deskripsi": post.get("deskripsi") or False,
			"qty": self._safe_float(post.get("qty")) or 0.0,
			"satuan": post.get("satuan") or item.satuan,
			"harga_satuan": self._safe_float(post.get("harga_satuan")) or 0.0,
		}
		try:
			item.write(values)
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))
		return self._redirect_with_message("/sadaya-langsung/paket", success="Item berhasil diperbarui")

	@http.route(
		"/sadaya-langsung/paket/<int:paket_id>/item/<int:item_id>/delete",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def paket_item_delete(self, paket_id, item_id, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_ppk'):
			return self._redirect_with_message("/sadaya-langsung/paket", error="Anda tidak memiliki hak akses untuk menghapus item.")
		item = request.env["sadaya_langsung.paket.line"].sudo().browse(item_id)
		if not item.exists() or item.paket_id.id != paket_id:
			return self._redirect_with_message("/sadaya-langsung/paket", error="Item tidak ditemukan")
		try:
			item.unlink()
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/paket", error=str(exc))
		return self._redirect_with_message("/sadaya-langsung/paket", success="Item berhasil dihapus")

	@http.route("/sadaya-langsung/kontrak", type="http", auth="user", website=True)
	def kontrak_page(self, **kwargs):
		Kontrak = request.env["sadaya_langsung.kontrak"].sudo()
		Paket = request.env["sadaya_langsung.paket"].sudo()
		is_vendor = self._is_vendor_user()
		domain = []
		paket_domain = []
		if is_vendor:
			partner_ids = self._get_user_vendor_partners().ids
			domain = [('paket_id.vendor_pemenang_id', 'in', partner_ids)]
			paket_domain = [('vendor_pemenang_id', 'in', partner_ids)]
		return request.render(
			"sadaya_langsung.frontend_kontrak_page",
			{
				"active_page": "kontrak",
				"notice_success": kwargs.get("success"),
				"notice_error": kwargs.get("error"),
				"kontrak_cards": self._build_kontrak_cards(
					Kontrak.search(domain, order="tanggal desc, id desc")
				),
				"total_kontrak": Kontrak.search_count(domain),
				"paket_options": [
					{"id": paket.id, "name": paket.name}
					for paket in Paket.search(paket_domain, order="tanggal desc, id desc")
				],
				"jenis_pengadaan_options": self._selection_options(
					Kontrak, "jenis_pengadaan"
				),
				"status_kontrak_options": self._selection_options(Kontrak, "status_kontrak"),
			},
		)

	@http.route(
		"/sadaya-langsung/kontrak/create",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def create_kontrak(self, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_ppk'):
			return self._redirect_with_message("/sadaya-langsung/kontrak", error="Anda tidak memiliki hak akses untuk membuat kontrak.")
		paket_id = self._safe_int(post.get("paket_id"))
		paket = False
		if paket_id:
			paket = request.env["sadaya_langsung.paket"].sudo().browse(paket_id)
			if not paket.exists():
				paket = False

		Kontrak = request.env["sadaya_langsung.kontrak"].sudo()
		jenis_options = self._selection_options(Kontrak, "jenis_pengadaan")

		values = {
			"name": post.get("name") or (paket.name if paket else "Kontrak Baru"),
			"paket_id": paket.id if paket else False,
			"pejabat_pembuat": post.get("pejabat_pembuat") or request.env.user.name,
			"penyedia": post.get("penyedia") or (paket.vendor_pemenang_id.name if paket and paket.vendor_pemenang_id else False),
			"jenis_pengadaan": self._safe_selection(post.get("jenis_pengadaan"), jenis_options) or (paket.jenis_pengadaan if paket else False),
			"nilai_hps": self._safe_float(post.get("nilai_hps") or (paket.nilai_hps if paket else 0.0)),
			"tanggal": post.get("tanggal") or False,
			"tanggal_mulai": post.get("tanggal_mulai") or (paket.tanggal_mulai if paket else False),
			"tanggal_selesai": post.get("tanggal_selesai") or (paket.tanggal_selesai if paket else False),
			"status_kontrak": "persiapan_kontrak",
			"keterangan": post.get("keterangan") or False,
		}
		Kontrak.create(values)
		return self._redirect_with_message(
			"/sadaya-langsung/kontrak", success="Kontrak berhasil ditambahkan"
		)

	@http.route(
		"/sadaya-langsung/kontrak/<int:kontrak_id>/update",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def update_kontrak(self, kontrak_id, **post):
		if not request.env.user.has_group('sadaya_langsung.group_langsung_ppk'):
			return self._redirect_with_message("/sadaya-langsung/kontrak", error="Anda tidak memiliki hak akses untuk mengubah kontrak.")
		Kontrak = request.env["sadaya_langsung.kontrak"].sudo()
		record = Kontrak.browse(kontrak_id)
		if not record.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/kontrak", error="Kontrak tidak ditemukan"
			)

		jenis_options = self._selection_options(Kontrak, "jenis_pengadaan")
		status_options = self._selection_options(Kontrak, "status_kontrak")
		paket_id = self._safe_int(post.get("paket_id"))
		values = {
			"name": post.get("name") or record.name,
			"paket_id": paket_id or False,
			"pejabat_pembuat": post.get("pejabat_pembuat") or False,
			"penyedia": post.get("penyedia") or False,
			"jenis_pengadaan": self._safe_selection(post.get("jenis_pengadaan"), jenis_options),
			"nilai_hps": self._safe_float(post.get("nilai_hps")),
			"tanggal": post.get("tanggal") or False,
			"tanggal_mulai": post.get("tanggal_mulai") or False,
			"tanggal_selesai": post.get("tanggal_selesai") or False,
			"keterangan": post.get("keterangan") or False,
		}
		status_input = self._safe_selection(post.get("status_kontrak"), status_options)
		if status_input:
			values["status_kontrak"] = status_input

		try:
			record.write(values)
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/kontrak", error=str(exc))

		return self._redirect_with_message(
			"/sadaya-langsung/kontrak", success="Kontrak berhasil diperbarui"
		)

	@http.route(
		"/sadaya-langsung/kontrak/<int:kontrak_id>/workflow",
		type="http",
		auth="user",
		website=True,
		methods=["POST"],
	)
	def kontrak_workflow(self, kontrak_id, **post):
		action_key = post.get("action")
		user = request.env.user
		is_ppk = user.has_group('sadaya_langsung.group_langsung_ppk')
		is_pphp = user.has_group('sadaya_langsung.group_langsung_pphp')

		allowed = False
		if action_key in ("proses_kontrak", "addendum"):
			allowed = is_ppk
		elif action_key == "selesai_kontrak":
			allowed = is_pphp
		elif action_key == "revisi":
			allowed = is_ppk or is_pphp

		if not allowed:
			return self._redirect_with_message("/sadaya-langsung/kontrak", error="Anda tidak memiliki hak akses untuk memproses kontrak ini.")
		action_map = {
			"proses_kontrak": "action_proses_kontrak",
			"selesai_kontrak": "action_selesai_kontrak",
			"revisi": "action_revisi",
			"addendum": "action_addendum",
		}
		record = request.env["sadaya_langsung.kontrak"].sudo().browse(kontrak_id)
		if not record.exists():
			return self._redirect_with_message(
				"/sadaya-langsung/kontrak", error="Kontrak tidak ditemukan"
			)
		action_key = post.get("action")
		method_name = action_map.get(action_key)
		if not method_name:
			return self._redirect_with_message(
				"/sadaya-langsung/kontrak", error="Aksi kontrak tidak valid"
			)

		try:
			getattr(record, method_name)()
		except Exception as exc:
			return self._redirect_with_message("/sadaya-langsung/kontrak", error=str(exc))

		return self._redirect_with_message(
			"/sadaya-langsung/kontrak", success="Status kontrak berhasil diperbarui"
		)

