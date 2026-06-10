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
    'assets': {
        'web.assets_frontend': [
            'sadaya_mitra/static/src/scss/sadaya_mitra_frontend.scss',
        ],
    },
    'installable': True,
    'application': True,
}