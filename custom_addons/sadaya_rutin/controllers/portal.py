# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from odoo import http
from odoo.http import request


class DirectPurchasePortal(http.Controller):
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
        domain = []
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
        packages = package_model.search([], order="start_date desc", limit=20)
        today = date.today()
        first_day, last_day = self._get_month_range(today)
        active_domain = [("status", "not in", ["done", "cancelled"])]
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
                    "direct_purchase.action_direct_purchase_packages"
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
                "statuses": self._get_selection(
                    "sadaya_rutin.procurement_package", "status"
                ),
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
        package = request.env["direct_purchase.procurement_package"].sudo().browse(package_id)
        if not package.exists():
            return request.not_found()
        return request.render(
            "direct_purchase.portal_package_detail",
            {
                "package": package,
            },
        )

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
