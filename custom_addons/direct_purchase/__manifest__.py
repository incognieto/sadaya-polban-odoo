# -*- coding: utf-8 -*-
{
    "name": "Pembelian Langsung",
    "summary": "Modul pembelian langsung",
    "version": "0.1.0",
    "category": "Operations/Procurement",
    "license": "LGPL-3",
    "author": "Sadaya Polban - Team(Farras_006, Fredy_010, Ichsan_015)",
    "website": "",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/procurement_package_views.xml",
        "views/contract_views.xml",
        "views/menu.xml",
    ],
    "application": True,
    "installable": True,
}
