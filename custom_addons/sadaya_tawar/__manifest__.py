# -*- coding: utf-8 -*-
{
    'name': "Sadaya Tawar",
    'summary': "Modul Publikasi & Penawaran Awal eProcurement Polban",
    'description': """
        Modul ini berfungsi sebagai etalase publik jembatan antara perencanaan dan eksekusi.
        Memungkinkan PPK memublikasikan RUP dan Vendor menyatakan minat/mendaftar.
    """,
    'author': "Politeknik Negeri Bandung",
    'category': 'Procurement',
    'version': '1.0',
    'depends': ['base', 'sadaya_rutin', 'sadaya_langsung', 'sadaya_lelang', 'sadaya_mitra', 'website'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'application': True,
    'installable': True,
}