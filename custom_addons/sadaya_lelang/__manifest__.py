# -*- coding: utf-8 -*-
{
    'name': "Sadaya Lelang",

    'summary': """
        Sistem Pengadaan dan Tendering (SPSE Style)""",

    'description': """
        Modul kustom Odoo untuk mengelola proses pengadaan/tender, 
        termasuk pendaftaran vendor (Penyedia), paket pengadaan, jadwal, 
        dan evaluasi (Pokja/PPK).
    """,

    'author': "Politeknik Negeri Bandung",
    'website': "https://www.polban.ac.id",

    'category': 'Operations/Purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'website', 'portal'],

    # always loaded
    'data': [
        'security/sadaya_lelang_groups.xml',
        'security/ir.model.access.csv',
        'views/sadaya_lelang_paket_views.xml',
        'views/res_partner_views.xml',
        'views/sadaya_lelang_menus.xml',
        'views/portal_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
