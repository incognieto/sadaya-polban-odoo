{
    'name': "Sadaya Tender",

    'summary': "Modul manajemen pengadaan tender",

    'description': """
    Modul manajemen pengadaan tender
    """,

    'author': "Rafif, Zaki",
    'website': "https://www.google.com",

    'category': 'Tools',
    'version': '0.1',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],

    'installable': True,     
    'application': True,     
}
