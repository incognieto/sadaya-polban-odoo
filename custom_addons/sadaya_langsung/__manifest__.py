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
        "website",
        "sadaya_mitra",
        "sadaya_auth",
    ],
    "data": [
        "security/security.xml",
        "security/sadaya_langsung_groups.xml",
        "security/ir.model.access.csv",
        "views/frontend_templates.xml",
        "views/paket_views.xml",
        "views/kontrak_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "sadaya_langsung/static/src/scss/frontend.scss",
        ],
    },
    "demo": [],
    "application": True,
    "installable": True,
}
