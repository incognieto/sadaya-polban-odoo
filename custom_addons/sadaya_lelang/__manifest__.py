# -*- coding: utf-8 -*-
{
    'name': "sadaya-lelang",

    'summary': """
        Sistem Pengadaan dan Tendering (SPSE Style)""",

    'description': """
        Modul kustom Odoo untuk mengelola proses pengadaan/sadaya_lelang, 
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
        'security/tender_groups.xml',
        'security/ir.model.access.csv',
        'views/tender_paket_views.xml',
        'views/res_partner_views.xml',
        'views/tender_menus.xml',
        'views/portal_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
