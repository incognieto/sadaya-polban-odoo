{
    "name": "Sadaya Rancang",
    "summary": "Modul untuk menginput usulan kebutuhan barang/jasa (RAB dan KAK) secara internal.",
    "description": """
Modul ini bertindak sebagai Hulu pengadaan:
1. Unit Kerja/Pemohon menginput usulan kebutuhan (RAB, KAK).
2. Publikasi ke RUP di Quotation (sadaya-tawar) setelah disetujui.
    """,
    "author": "Politeknik Negeri Bandung",
    "website": "https://www.polban.ac.id",
    "category": "Procurement",
    "version": "1.0",
    "depends": ["base", "sadaya_tawar", "mail", "website", "portal", "sadaya_auth"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_catatan_views.xml",
        "views/usulan_views.xml",
        "views/rup_views.xml",
        "views/hps_views.xml",
        "views/dashboard_views.xml",
        "views/templates.xml",
    ],
    "application": True,
    "installable": True,
}
