# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


class SadayaRutinPortal(http.Controller):
    def _get_selection(self, model_name, field_name):
        model = request.env[model_name]
        field = model.fields_get([field_name])[field_name]
        return field.get("selection", [])

    def _parse_date(self, value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _build_package_domain(self, params):
        domain = [("status", "!=", "draft")]
        if params.get("procurement_type"):
            domain.append(("procurement_type", "=", params["procurement_type"]))
        if params.get("status"):
            domain.append(("status", "=", params["status"]))
        if params.get("proposing_unit"):
            domain.append(("proposing_unit", "=", params["proposing_unit"]))
        start_date = self._parse_date(params.get("start_date"))
        end_date = self._parse_date(params.get("end_date"))
        if start_date:
            domain.append(("start_date", ">=", start_date))
        if end_date:
            domain.append(("end_date", "<=", end_date))
        if params.get("query"):
            domain.append("|")
            domain.append(("name", "ilike", params["query"]))
            domain.append(("code", "ilike", params["query"]))
            
        if params.get("my_packages"):
            user_partner_id = request.env.user.partner_id.id
            domain.append("|")
            domain.append(("vendor_id", "=", user_partner_id))
            domain.append(("vendor_id.parent_id", "=", user_partner_id))
            
        return domain

    def _build_contract_domain(self, params):
        domain = []
        if params.get("procurement_type"):
            domain.append(("procurement_type", "=", params["procurement_type"]))
        if params.get("status"):
            domain.append(("status", "=", params["status"]))
        start_date = self._parse_date(params.get("start_date"))
        end_date = self._parse_date(params.get("end_date"))
        if start_date:
            domain.append(("start_date", ">=", start_date))
        if end_date:
            domain.append(("end_date", "<=", end_date))
        if params.get("query"):
            domain.append("|")
            domain.append(("name", "ilike", params["query"]))
            domain.append(("package_id.name", "ilike", params["query"]))
        if params.get("vendor_name"):
            domain.append(("vendor_name", "ilike", params["vendor_name"]))
        if params.get("officer_name"):
            domain.append(("officer_name", "ilike", params["officer_name"]))
        return domain

    def _get_units(self):
        package_model = request.env["sadaya_rutin.procurement_package"].sudo()
        units = package_model.search_read([], ["proposing_unit"])
        return sorted({item["proposing_unit"] for item in units if item.get("proposing_unit")})

    def _get_action_id(self, xmlid):
        try:
            return request.env.ref(xmlid).id
        except ValueError:
            return False

    def _get_month_range(self, today):
        first_day = date(today.year, today.month, 1)
        if today.month == 12:
            last_day = date(today.year, 12, 31)
        else:
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return first_day, last_day

    @http.route(
        [
            "/sadaya-rutin",
            "/sadaya-rutin/dashboard",
            "/purchase-portal",
            "/purchase-portal/dashboard",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_dashboard(self, **params):
        package_model = request.env["sadaya_rutin.procurement_package"].sudo()
        visible_domain = [("status", "!=", "draft")]
        packages = package_model.search(visible_domain, order="start_date desc", limit=20)
        today = date.today()
        first_day, last_day = self._get_month_range(today)
        active_domain = [("status", "not in", ["draft", "done", "cancelled"])]
        pending_spk_domain = [("status", "in", ["spk_preparation", "spk_process"])]
        done_month_domain = [
            ("status", "=", "done"),
            ("end_date", ">=", first_day),
            ("end_date", "<=", last_day),
        ]
        return request.render(
            "sadaya_rutin.portal_dashboard",
            {
                "packages": packages,
                "package_active_count": package_model.search_count(active_domain),
                "package_pending_spk_count": package_model.search_count(pending_spk_domain),
                "package_done_month_count": package_model.search_count(done_month_domain),
                "package_action_id": self._get_action_id(
                    "sadaya_rutin.action_sadaya_rutin_packages"
                ),
            },
        )

    @http.route(
        ["/sadaya-rutin/paket", "/sadaya-rutin/packages", "/purchase-portal/packages"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_packages(self, **params):
        package_model = request.env["sadaya_rutin.procurement_package"].sudo()
        domain = self._build_package_domain(params)
        packages = package_model.search(domain, order="start_date desc", limit=100)
        return request.render(
            "sadaya_rutin.portal_packages",
            {
                "packages": packages,
                "filters": params,
                "procurement_types": self._get_selection(
                    "sadaya_rutin.procurement_package", "procurement_type"
                ),
                "statuses": [
                    item
                    for item in self._get_selection("sadaya_rutin.procurement_package", "status")
                    if item[0] != "draft"
                ],
                "units": self._get_units(),
            },
        )

    @http.route(
        [
            "/sadaya-rutin/paket/<int:package_id>",
            "/sadaya-rutin/packages/<int:package_id>",
            "/purchase-portal/packages/<int:package_id>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_package_detail(self, package_id, **params):
        package = request.env["sadaya_rutin.procurement_package"].sudo().browse(package_id)
        if not package.exists() or package.status == "draft":
            return request.not_found()
        return request.render(
            "sadaya_rutin.portal_package_detail",
            {
                "package": package,
            },
        )

    @http.route(
        [
            "/sadaya-rutin/paket/<int:package_id>/submit-offer",
            "/sadaya-rutin/packages/<int:package_id>/submit-offer",
        ],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_submit_offer(self, package_id, **post):
        package = request.env["sadaya_rutin.procurement_package"].sudo().browse(package_id)
        if not package.exists() or package.status != "negotiation_vendor":
            return request.not_found()
        if package.vendor_id and request.env.user.partner_id.id not in (package.vendor_id.id, package.vendor_id.parent_id.id):
            raise ValidationError("Anda tidak memiliki akses untuk memberikan penawaran pada paket ini.")
        negotiation_price = float(post.get("negotiation_price") or 0.0)
        if negotiation_price <= 0:
            raise ValidationError("Harga penawaran wajib diisi dan harus lebih dari nol.")
        if not post.get("vendor_stock_confirmed"):
            raise ValidationError("Vendor harus mengonfirmasi stok tersedia sebelum mengirim penawaran.")
        package.write(
            {
                "negotiation_price": negotiation_price,
                "vendor_stock_confirmed": True,
                "vendor_offer_notes": post.get("vendor_offer_notes"),
            }
        )
        package.action_vendor_submit_offer()
        return request.redirect("/sadaya-rutin/paket/%s" % package_id)

    @http.route(
        [
            "/sadaya-rutin/paket/<int:package_id>/reject-offer",
            "/sadaya-rutin/packages/<int:package_id>/reject-offer",
        ],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_reject_offer(self, package_id, **post):
        package = request.env["sadaya_rutin.procurement_package"].sudo().browse(package_id)
        if not package.exists() or package.status != "negotiation_vendor":
            return request.not_found()
        if package.vendor_id and request.env.user.partner_id.id not in (package.vendor_id.id, package.vendor_id.parent_id.id):
            raise ValidationError("Anda tidak memiliki akses untuk memberikan penawaran pada paket ini.")
        
        # Save rejection reason if provided
        if post.get("vendor_offer_notes"):
            package.write({
                "vendor_offer_notes": post.get("vendor_offer_notes"),
            })
        
        package.action_vendor_reject_offer()
        return request.redirect("/sadaya-rutin/paket/%s" % package_id)

    @http.route(
        [
            "/sadaya-rutin/paket/<int:package_id>/submit-delivery",
            "/sadaya-rutin/packages/<int:package_id>/submit-delivery",
        ],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_submit_delivery(self, package_id, **post):
        package = request.env["sadaya_rutin.procurement_package"].sudo().browse(package_id)
        if not package.exists() or package.status != "delivery":
            return request.not_found()
        if package.vendor_id and request.env.user.partner_id.id not in (package.vendor_id.id, package.vendor_id.parent_id.id):
            raise ValidationError("Anda tidak memiliki akses untuk mengajukan jadwal pengiriman.")
        
        delivery_date = self._parse_date(post.get("delivery_date"))
        if not delivery_date:
            return request.redirect("/sadaya-rutin/paket/%s?error=Tanggal pengiriman tidak valid." % package_id)
            
        # Validation for weekday
        if delivery_date.weekday() >= 5:
            return request.redirect("/sadaya-rutin/paket/%s?error=Pengiriman hanya dapat dilakukan pada hari kerja (Senin-Jumat)." % package_id)
            
        package.write({
            "delivery_date": delivery_date,
            "delivery_notes": post.get("delivery_notes"),
        })
        
        return request.redirect("/sadaya-rutin/paket/%s" % package_id)

    @http.route(
        [
            "/sadaya-rutin/paket/<int:package_id>/request-revision",
            "/sadaya-rutin/packages/<int:package_id>/request-revision",
        ],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_request_revision(self, package_id, **post):
        package = request.env["sadaya_rutin.procurement_package"].sudo().browse(package_id)
        if not package.exists() or package.status != "inspection":
            return request.not_found()
        if package.vendor_id and request.env.user.partner_id.id not in (package.vendor_id.id, package.vendor_id.parent_id.id):
            raise ValidationError("Anda tidak memiliki akses untuk meminta revisi pada paket ini.")
        
        if package.inspection_status != 'not_ok':
            raise ValidationError("Revisi hanya dapat diajukan jika hasil pemeriksaan tidak sesuai.")

        # Tambahkan pesan log ke chatter atas nama vendor
        package.message_post(
            body=(
                "<p><b>Konfirmasi Vendor: Mengajukan Revisi</b></p>"
                "<p>Vendor telah menerima pemberitahuan ketidaksesuaian barang/jasa dan sepakat untuk "
                "melakukan pengiriman ulang/perbaikan (Revisi). Menunggu persetujuan Tim Teknis/PP.</p>"
            ),
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=request.env.user.partner_id.id,
        )
        
        package.write({'vendor_revision_requested': True, 'vendor_cancellation_requested': False})
        return request.redirect("/sadaya-rutin/paket/%s" % package_id)

    @http.route(
        [
            "/sadaya-rutin/paket/<int:package_id>/request-cancellation",
            "/sadaya-rutin/packages/<int:package_id>/request-cancellation",
        ],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_request_cancellation(self, package_id, **post):
        package = request.env["sadaya_rutin.procurement_package"].sudo().browse(package_id)
        if not package.exists() or package.status != "inspection":
            return request.not_found()
        if package.vendor_id and request.env.user.partner_id.id not in (package.vendor_id.id, package.vendor_id.parent_id.id):
            raise ValidationError("Anda tidak memiliki akses untuk meminta pembatalan pada paket ini.")
        
        if package.inspection_status != 'not_ok':
            raise ValidationError("Pembatalan hanya dapat diajukan jika hasil pemeriksaan tidak sesuai.")

        reason = post.get("cancellation_reason", "Tidak ada alasan yang diberikan.")

        # Tambahkan pesan log ke chatter atas nama vendor
        package.message_post(
            body=(
                "<p><b>Konfirmasi Vendor: Mengajukan Pembatalan</b></p>"
                "<p>Vendor telah menerima pemberitahuan ketidaksesuaian barang/jasa, namun <b>tidak sanggup</b> "
                "untuk melakukan perbaikan/pengiriman ulang dan meminta pesanan ini dibatalkan.</p>"
                "<p><b>Alasan:</b> %s</p>"
                "<p>Menunggu persetujuan Tim Teknis/PP.</p>"
            ) % reason,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=request.env.user.partner_id.id,
        )
        
        package.write({'vendor_cancellation_requested': True, 'vendor_revision_requested': False})
        return request.redirect("/sadaya-rutin/paket/%s" % package_id)

    @http.route(
        ["/sadaya-rutin/kontrak", "/sadaya-rutin/contracts", "/purchase-portal/contracts"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_contracts(self, **params):
        contract_model = request.env["sadaya_rutin.contract"].sudo()
        domain = self._build_contract_domain(params)
        contracts = contract_model.search(domain, order="start_date desc", limit=100)
        return request.render(
            "sadaya_rutin.portal_contracts",
            {
                "contracts": contracts,
                "filters": params,
                "procurement_types": self._get_selection(
                    "sadaya_rutin.procurement_package", "procurement_type"
                ),
                "statuses": self._get_selection("sadaya_rutin.contract", "status"),
            },
        )
