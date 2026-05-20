# -*- coding: utf-8 -*-
{
    "name": "Sadaya Langsung",
    "summary": "Sistem Informasi Sadaya Langsung",
    "description": """
        Modul pengadaan langsung untuk menangani paket pengadaan
        barang dan jasa dengan nilai di bawah Rp200 juta melalui
        prosedur non-sadaya_lelang yang lebih sederhana.
    """,
    "version": "19.0.1.0.0",
    "category": "Operations/Procurement",
    "license": "LGPL-3",
    "author": "Sadaya Polban",
    "website": "",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/paket_views.xml",
        "views/kontrak_views.xml",
        "views/dashboard_action.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sadaya_langsung/static/src/css/dashboard.css",
            "sadaya_langsung/static/src/js/dashboard.js",
            "sadaya_langsung/static/src/xml/dashboard.xml",
        ],
    },
    "demo": [],
    "application": True,
    "installable": True,
}
