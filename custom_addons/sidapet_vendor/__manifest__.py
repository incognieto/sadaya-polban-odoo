{
    'name': 'SIDAPET Penyedia',
    'version': '1.0',
    'summary': 'Pendaftaran Penyedia (SIDAPET)',
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