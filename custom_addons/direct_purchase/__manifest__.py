# -*- coding: utf-8 -*-
{
    "name": "Sadaya Rutin",
    "summary": "E-Purchasing untuk belanja operasional rutin via e-katalog",
    "version": "0.1.0",
    "category": "Operations/Procurement",
    "license": "LGPL-3",
    "author": "Sadaya Polban - Team(Farras_006, Fredy_010, Ichsan_015)",
    "website": "",
    "depends": [
        "base",
        "mail",
        "website",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/procurement_package_views.xml",
        "views/contract_views.xml",
        "views/menu.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "direct_purchase/static/src/css/portal.css",
        ],
    },
    "application": True,
    "installable": True,
}
