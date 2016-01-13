# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) LasLabs, Inc [https://laslabs.com]. All Rights Reserved
#
##############################################################################
#
#    Collaborators of this module:
#       Written By: James Foster <jfoster@laslabs.com>
#
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{

    'name': 'Password Security',
    'version': '8.0.0.0.1',
    'author': "LasLabs",
    'category': 'Base',
    'depends': [
        'auth_signup',
    ],
    "website": "https://laslabs.com",
    "licence": "AGPL-3",
    "data": [
        'views/res_company_view.xml'
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
