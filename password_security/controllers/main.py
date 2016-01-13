# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging
import operator
import werkzeug

import openerp
from openerp import http
from openerp.http import request
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.web.controllers.main import ensure_db, Session
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class PasswordSecuritySession(Session):

    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        old_password, new_password, confirm_password = operator.itemgetter(
            'old_pwd', 'new_password', 'confirm_pwd')(
                dict(map(operator.itemgetter('name', 'value'), fields))
            )
        if not (old_password.strip() and new_password.strip() and
                confirm_password.strip()):
            return {
                'error': _('You cannot leave any password empty.'),
                'title': _('Change Password')}
        if new_password != confirm_password:
            return {
                'error': _(
                    'The new password and its confirmation must be identical.'
                ),
                'title': _('Change Password')}
        user = request.env.user
        user.check_password(new_password)
        try:
            if request.session.model('res.users').change_password(
                    old_password, new_password):
                return {'new_password': new_password}
        except Exception:
            return {
                'error': _('The old password you provided is incorrect, '
                           'your password was not changed.'),
                'title': _('Change Password')}
        return {'error': _('Error, password not changed !'),
                'title': _('Change Password')}


class PasswordSecurityHome(AuthSignupHome):

    def do_signup(self, qcontext):
        values = dict((key, qcontext.get(key))
                      for key in ('login', 'name', 'password'))
        assert any([k for k in values.values()]
                   ), "The form was not properly filled in."
        assert values.get('password') == qcontext.get(
            'confirm_password'), "Passwords do not match; please retype them."
        res_user = request.env['res.users'].browse(request.uid)
        password = values.get('password')
        res_user.check_password(password)
        values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(PasswordSecurityHome, self).web_login(*args, **kw)
        if request.httprequest.method == 'POST':
            uid = request.session.authenticate(
                request.session.db,
                request.params['login'],
                request.params['password'])
            if uid is not False:
                login = request.params['login']
                res_users = request.env['res.users']
                res_user = res_users.browse(request.uid)
                if res_user._password_has_expired():
                    res_users.sudo().expire_password(login)
                    redirect = res_user.partner_id.signup_url
                    return http.redirect_with_hash(redirect)
        return response

    @http.route(
        '/web/reset_password',
        type='http',
        auth='public',
        website=True)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get(
                'reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return super(
                        PasswordSecurityHome,
                        self).web_login(
                        *args,
                        **kw)
                else:
                    login = qcontext.get('login')
                    assert login, "No login provided."
                    res_users = request.registry.get('res.users')
                    res_users.reset_password(
                        request.cr, openerp.SUPERUSER_ID, login)
                    qcontext['message'] = _(
                        "An email has been sent with credentials "
                        "to reset your password")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = _(e.message)

        if 'error' not in qcontext and qcontext.get('token'):
            qcontext['error'] = _("Your password has expired")

        return request.render('auth_signup.reset_password', qcontext)
