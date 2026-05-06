{
    'name': 'SI-Plang',
    'version': '1.0',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard.xml',
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'si_plang/static/src/dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
}