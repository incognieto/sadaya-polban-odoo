{
    'name': "sadaya-tawar",
    'summary': "Modul Sadaya Tawar untuk Pengadaan Barang dan Jasa Polban",
    'description': """
Modul ini menangani:
- Pembuatan Rencana Umum Pengadaan (RUP)
- Pendaftaran Penawaran Harga dari Vendor
    """,
    'author': "Ichsan & Zaenal",
    'website': "https://www.polban.ac.id",
    'category': 'Procurement',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
}