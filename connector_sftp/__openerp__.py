# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "SCP Connector",
    "summary": "Framework for interacting with SCP hosts",
    "version": "9.0.1.0.0",
    "category": "Base",
    "website": "https://laslabs.com/",
    "author": "LasLabs",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [
            'paramiko',
        ],
    },
    'data': [
        'views/connector_sftp_view.xml',
        'views/res_company_view.xml',
        'security/ir.model.access.csv',
    ]
}
