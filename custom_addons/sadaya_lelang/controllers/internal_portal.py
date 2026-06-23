from odoo import fields, http
from odoo.http import request
from urllib.parse import quote_plus
import base64

class SadayaLelangInternalController(http.Controller):
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

    def _check_edit_permission(self):
        # We assume PPK and Pokja have editing rights for internal workflow
        return request.env.user.has_group('sadaya_lelang.group_lelang_ppk') or \
               request.env.user.has_group('sadaya_lelang.group_lelang_pokja') or \
               request.env.user.has_group('sadaya_lelang.group_lelang_manajemen')

    # Dashboard
    def _get_dashboard_payload(self):
        Paket = request.env["sadaya_lelang.paket"].sudo()

        paket_breakdown = Paket.read_group(
            [], ["status"], ["status"], lazy=False
        )

        total_paket = Paket.search_count([])
        paket_aktif = Paket.search_count([("status", "not in", ["selesai", "draft"])])
        paket_draft = Paket.search_count([("status", "=", "draft")])
        paket_selesai = Paket.search_count([("status", "=", "selesai")])

        recent_paket = Paket.search([], order="create_date desc, id desc", limit=10)

        recent_cards = []
        for record in recent_paket:
            recent_cards.append({
                "id": record.id,
                "name": record.name,
                "kode_tender": record.kode_tender or "-",
                "status_label": self._selection_label(record, "status", record.status),
                "hps": self._format_money(record.hps),
                "metode_pemilihan": self._selection_label(record, "metode_pemilihan", record.metode_pemilihan)
            })

        return {
            "total_paket": total_paket,
            "paket_aktif": paket_aktif,
            "paket_draft": paket_draft,
            "paket_selesai": paket_selesai,
            "recent_paket": recent_cards,
            "paket_breakdown": [
                {
                    "label": dict(Paket._fields["status"].selection).get(
                        item["status"], item["status"]
                    ),
                    "count": self._group_count(item, "status"),
                }
                for item in paket_breakdown
                if item.get("status")
            ],
        }

    @http.route("/sadaya-lelang/internal", type="http", auth="user", website=True)
    def dashboard(self, **kwargs):
        if not self._check_edit_permission():
            return request.render("http_routing.403")
        return request.render(
            "sadaya_lelang.internal_dashboard",
            {"active_page": "dashboard", **self._get_dashboard_payload()},
        )

    @http.route("/sadaya-lelang/internal/paket", type="http", auth="user", website=True)
    def paket_page(self, **kwargs):
        if not self._check_edit_permission():
            return request.render("http_routing.403")
            
        Paket = request.env["sadaya_lelang.paket"].sudo()
        records = Paket.search([], order="create_date desc, id desc")
        
        cards = []
        for record in records:
            cards.append({
                "id": record.id,
                "name": record.name,
                "kode_tender": record.kode_tender or "-",
                "status_code": record.status,
                "status_label": self._selection_label(record, "status", record.status),
                "hps": self._format_money(record.hps),
                "metode_pemilihan": self._selection_label(record, "metode_pemilihan", record.metode_pemilihan)
            })

        return request.render(
            "sadaya_lelang.internal_paket_list",
            {
                "active_page": "paket",
                "notice_success": kwargs.get("success"),
                "notice_error": kwargs.get("error"),
                "paket_cards": cards,
                "total_paket": len(cards),
            },
        )

    @http.route("/sadaya-lelang/internal/paket/<int:paket_id>", type="http", auth="user", website=True)
    def paket_detail(self, paket_id, **kwargs):
        if not self._check_edit_permission():
            return request.render("http_routing.403")
            
        record = request.env["sadaya_lelang.paket"].sudo().browse(paket_id)
        if not record.exists():
            return self._redirect_with_message("/sadaya-lelang/internal/paket", error="Paket tidak ditemukan")
            
        # Compile actions based on status
        actions = []
        st = record.status
        if st == "draft": actions.append({"key": "menunggu_persetujuan", "label": "Kirim ke Manajemen", "class": "btn-primary"})
        elif st == "menunggu_persetujuan":
            actions.append({"key": "pengumuman", "label": "Setujui (Manajemen)", "class": "btn-success"})
            actions.append({"key": "batal", "label": "Tolak (Manajemen)", "class": "btn-danger"})
        elif st == "pengumuman": actions.append({"key": "pendaftaran", "label": "Mulai Pendaftaran", "class": "btn-primary"})
        elif st == "pendaftaran": actions.append({"key": "lelang", "label": "Tutup Pendaftaran & Mulai Lelang", "class": "btn-primary"})
        elif st == "lelang": actions.append({"key": "pemasukan_penawaran", "label": "Mulai Pemasukan Penawaran", "class": "btn-primary"})
        elif st == "pemasukan_penawaran": actions.append({"key": "pembukaan", "label": "Tutup Penawaran (Buka Penawaran)", "class": "btn-primary"})
        elif st == "pembukaan": actions.append({"key": "eval_administrasi", "label": "Mulai Evaluasi Administrasi", "class": "btn-primary"})
        elif st == "eval_administrasi": actions.append({"key": "eval_teknis", "label": "Mulai Evaluasi Teknis", "class": "btn-primary"})
        elif st == "eval_teknis": actions.append({"key": "eval_harga", "label": "Mulai Evaluasi Harga", "class": "btn-primary"})
        elif st == "eval_harga": actions.append({"key": "pembuktian_kualifikasi", "label": "Mulai Pembuktian Kualifikasi", "class": "btn-primary"})
        elif st == "pembuktian_kualifikasi": actions.append({"key": "penetapan_pemenang", "label": "Penetapan Pemenang", "class": "btn-success"})
        elif st == "penetapan_pemenang": actions.append({"key": "masa_sanggah", "label": "Mulai Masa Sanggah", "class": "btn-warning"})
        elif st == "masa_sanggah": actions.append({"key": "sppbj", "label": "Terbitkan SPPBJ", "class": "btn-primary"})
        elif st == "sppbj": actions.append({"key": "pam", "label": "Pelaksanaan PAM", "class": "btn-primary"})
        elif st == "pam": actions.append({"key": "kontrak", "label": "Penandatanganan Kontrak", "class": "btn-primary"})
        elif st == "kontrak": actions.append({"key": "pelaksanaan", "label": "Mulai Pelaksanaan", "class": "btn-primary"})
        elif st == "pelaksanaan": actions.append({"key": "selesai", "label": "Selesai (BAST)", "class": "btn-success"})

        if st not in ("selesai", "batal"):
            actions.append({"key": "batal", "label": "Batalkan Tender", "class": "btn-outline-danger"})
            
        penawaran_records = record.penawaran_ids.sorted(lambda p: (p.harga_penawaran, p.id))
        penawaran_rows = []
        for p in penawaran_records:
            penawaran_rows.append({
                "id": p.id,
                "vendor": p.vendor_id.name,
                "harga_penawaran": self._format_money(p.harga_penawaran),
                "status": p.status,
                "eval_administrasi": p.eval_administrasi or "",
                "eval_kualifikasi": p.eval_kualifikasi or "",
                "eval_harga_wajar": "Ya" if p.eval_harga_wajar else "Tidak",
                "skor_teknis": p.skor_teknis,
                "skor_harga": p.skor_harga,
            })
            
        return request.render(
            "sadaya_lelang.internal_paket_detail",
            {
                "active_page": "paket",
                "notice_success": kwargs.get("success"),
                "notice_error": kwargs.get("error"),
                "paket": record,
                "status_label": self._selection_label(record, "status", record.status),
                "metode_pemilihan": self._selection_label(record, "metode_pemilihan", record.metode_pemilihan),
                "hps": self._format_money(record.hps),
                "actions": actions,
                "penawaran_rows": penawaran_rows,
                "evaluasi_options": self._selection_options(request.env['sadaya_lelang.penawaran'], "eval_administrasi"),
                "evaluasi_kual_options": self._selection_options(request.env['sadaya_lelang.penawaran'], "eval_kualifikasi"),
            },
        )

    @http.route("/sadaya-lelang/internal/paket/<int:paket_id>/workflow", type="http", auth="user", website=True, methods=["POST"])
    def paket_workflow(self, paket_id, **post):
        if not self._check_edit_permission():
            return self._redirect_with_message("/sadaya-lelang/internal/paket", error="Hak Akses Ditolak")
            
        record = request.env["sadaya_lelang.paket"].sudo().browse(paket_id)
        if not record.exists():
            return self._redirect_with_message("/sadaya-lelang/internal/paket", error="Paket tidak ditemukan")
            
        action_key = post.get("action")
        if not action_key:
            return self._redirect_with_message(f"/sadaya-lelang/internal/paket/{paket_id}", error="Aksi paket tidak valid")

        try:
            record.write({"status": action_key})
        except Exception as exc:
            return self._redirect_with_message(f"/sadaya-lelang/internal/paket/{paket_id}", error=str(exc))

        return self._redirect_with_message(
            f"/sadaya-lelang/internal/paket/{paket_id}", success="Status paket berhasil diperbarui"
        )
        
    @http.route("/sadaya-lelang/internal/paket/<int:paket_id>/upload_dokumen", type="http", auth="user", website=True, methods=["POST"])
    def upload_dokumen(self, paket_id, **post):
        if not self._check_edit_permission():
            return self._redirect_with_message("/sadaya-lelang/internal/paket", error="Hak Akses Ditolak")
            
        record = request.env["sadaya_lelang.paket"].sudo().browse(paket_id)
        if not record.exists():
            return self._redirect_with_message("/sadaya-lelang/internal/paket", error="Paket tidak ditemukan")
            
        if request.httprequest.files:
            f_doc = request.httprequest.files.get("file_dokumen")
            if f_doc:
                data = f_doc.read()
                if data:
                    try:
                        request.env['sadaya_lelang.dokumen'].sudo().create({
                            'paket_id': record.id,
                            'name': post.get('name') or 'Dokumen Tanpa Nama',
                            'description': post.get('description'),
                            'file_dokumen': base64.b64encode(data).decode('utf-8'),
                            'file_name': getattr(f_doc, 'filename', 'document.pdf'),
                        })
                        return self._redirect_with_message(f"/sadaya-lelang/internal/paket/{paket_id}", success="Dokumen POKJA berhasil diunggah")
                    except Exception as e:
                        return self._redirect_with_message(f"/sadaya-lelang/internal/paket/{paket_id}", error=str(e))
                        
        return self._redirect_with_message(f"/sadaya-lelang/internal/paket/{paket_id}", error="Gagal mengunggah dokumen")

    @http.route("/sadaya-lelang/internal/penawaran/<int:penawaran_id>/evaluate", type="http", auth="user", website=True, methods=["POST"])
    def evaluate_penawaran(self, penawaran_id, **post):
        if not self._check_edit_permission():
            return self._redirect_with_message("/sadaya-lelang/internal/paket", error="Hak Akses Ditolak")
            
        Penawaran = request.env["sadaya_lelang.penawaran"].sudo()
        record = Penawaran.browse(penawaran_id)
        if not record.exists():
            return self._redirect_with_message("/sadaya-lelang/internal/paket", error="Penawaran tidak ditemukan")
            
        eval_options = self._selection_options(Penawaran, "eval_administrasi")
        eval_kual_options = self._selection_options(Penawaran, "eval_kualifikasi")
        
        values = {}
        
        if post.get("eval_administrasi"):
            values["eval_administrasi"] = self._safe_selection(post.get("eval_administrasi"), eval_options)
        
        if post.get("skor_teknis"):
            values["skor_teknis"] = self._safe_float(post.get("skor_teknis"))
            
        if post.get("skor_harga"):
            values["skor_harga"] = self._safe_float(post.get("skor_harga"))
            
        if "eval_harga_wajar" in post:
            values["eval_harga_wajar"] = post.get("eval_harga_wajar") == "on"
            
        if post.get("eval_kualifikasi"):
            values["eval_kualifikasi"] = self._safe_selection(post.get("eval_kualifikasi"), eval_kual_options)

        try:
            record.write(values)
            # Recompute winning status if needed based on the workflow, but usually Odoo compute/workflow does it.
        except Exception as exc:
            return self._redirect_with_message(f"/sadaya-lelang/internal/paket/{record.paket_id.id}", error=str(exc))

        return self._redirect_with_message(
            f"/sadaya-lelang/internal/paket/{record.paket_id.id}", success="Evaluasi penawaran berhasil diperbarui"
        )
