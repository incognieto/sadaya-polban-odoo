# -*- coding: utf-8 -*-
{
    'name': 'Sadaya Auth - Register Login Logout',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Custom authentication module for Sadaya application with Badan Usaha & Perorangan registration',
    'description': """
        Module autentikasi kustom untuk aplikasi Sadaya.
        Fitur:
        - Registrasi Badan Usaha
        - Registrasi Perorangan
        - Login dengan email & password
        - Logout
        - Page layout aplikasi Sadaya
    """,
    'author': 'Sadaya Development Team',
    'website': 'https://sadaya.id',
    'depends': [
        'base',
        'web',
        'website',
        'portal',
        'mail',
    ],
    'data': [
        'security/sadaya_security.xml',
        'views/sadaya_layout_templates.xml',
        'views/sadaya_register_templates.xml',
        'views/sadaya_login_templates.xml',
        'views/sadaya_dashboard_templates.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
