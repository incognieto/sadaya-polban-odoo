{
    'name': "sadaya-rancang",
    'summary': "Modul untuk menginput usulan kebutuhan barang/jasa (RAB dan KAK) secara internal.",
    'description': """
Modul ini bertindak sebagai Hulu pengadaan:
1. Unit Kerja/Pemohon menginput usulan kebutuhan (RAB, KAK).
2. Publikasi ke RUP di Quotation (sadaya-tawar) setelah disetujui.
    """,
    'author': "Politeknik Negeri Bandung",
    'website': "https://www.polban.ac.id",
    'category': 'Procurement',
    'version': '1.0',
    'depends': ['base', 'sadaya_tawar'],
    'data': [
        'security/ir.model.access.csv',
        'views/usulan_views.xml',
    ],
    'application': True,
    'installable': True,
}
