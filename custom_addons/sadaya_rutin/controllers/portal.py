# -*- coding: utf-8 -*-

from datetime import datetime

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
            domain.append(("name", "ilike", params["query"]))
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

    @http.route(["/purchase-portal", "/purchase-portal/dashboard"], type="http", auth="user", website=True)
    def portal_dashboard(self, **params):
        package_model = request.env["sadaya_rutin.procurement_package"].sudo()
        packages = package_model.search([], order="start_date desc", limit=20)
        return request.render(
            "sadaya_rutin.portal_dashboard",
            {
                "packages": packages,
            },
        )

    @http.route(["/purchase-portal/packages"], type="http", auth="user", website=True)
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

    @http.route(["/purchase-portal/contracts"], type="http", auth="user", website=True)
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
