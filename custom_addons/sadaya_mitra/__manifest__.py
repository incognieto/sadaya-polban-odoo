{
    'name': 'Sadaya Mitra',
    'version': '1.0',
    'summary': 'Modul Pendaftaran Penyedia/Vendor',
    'author': 'Tim Pengadaan POLBAN',
    'depends': ['base', 'mail', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/penyedia_views.xml',
        'views/pengurus_views.xml',
        'views/website_penyedia_templates.xml',
        'views/website_lanjutan_templates.xml',
    ],
    'installable': True,
    'application': True,
}