{
    'name': 'Sadaya Mitra',
    'version': '1.0',
    'summary': 'Pendaftaran Penyedia (SADAYA_MITRA)',
    'author': 'Tim Pengadaan POLBAN',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/penyedia_views.xml',
        'views/pengurus_views.xml',
    ],
    'installable': True,
    'application': True,
}