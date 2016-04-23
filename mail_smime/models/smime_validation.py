# -*- coding: utf-8 -*-
# © 2015 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields
import os, base64
from M2Crypto import BIO, SMIME, m2, X509
from difflib import unified_diff


class EncryptedText(fields._String):
    """
    Identical to fields.Text, except encrypted in the database

    :param translate: whether the value of this field can be translated
    """
    type = 'text'

    BS = 16
    KEY = '@TODO: SuperSecretKeyThatShouldBeReplacedWithAnEnvVarOrSomething'

    def __decrypt(self, value):
        """
        Decrypt a value
        :param value: String to decrypt
        """
        unpad = lambda s: s[:-ord(s[len(s)-1:])]
        value = base64.b64decode(value)
        iv = value[:16]
        cipher = AES.new(self.KEY, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(value[16:]))

    def __encrypt(self, value):
        """
        Encrypt a value
        :param value: String to encrypt
        """
        BS = self.BS
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        value = pad(value)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.KEY, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(value))

    def convert_to_cache(self, value, record, validate=True):
        """
        convert ``value`` to the cache level in ``env``; ``value`` may come
        from an assignment, or have the format of methods
        :meth:`BaseModel.read` or :meth:`BaseModel.write`

        :param record: the target record for the assignment,
            or an empty recordset

        :param bool validate: when True, field-specific validation of
            ``value`` will be performed
        """
        return self.__encrypt(value)

    def convert_to_read(self, value, use_name_get=True):
        """ convert ``value`` from the cache to a value as returned by method
            :meth:`BaseModel.read`

            :param bool use_name_get: when True, value's diplay name will
                be computed using :meth:`BaseModel.name_get`, if relevant
                for the field
        """
        return False if value is None else self.__decrypt(value)

    def convert_to_write(self, value, target=None, fnames=None):
        """ convert ``value`` from the cache to a valid value for method
            :meth:`BaseModel.write`.

            :param target: optional, the record to be modified with this value
            :param fnames: for relational fields only, an optional collection
                of field names to convert
        """
        return value

    def convert_to_onchange(self, value):
        """ convert ``value`` from the cache to a valid value for an onchange
            method v7.
        """
        return self.__decrypt(value)

    def convert_to_export(self, value, env):
        """ convert ``value`` from the cache to a valid value for export. The
            parameter ``env`` is given for managing translations.
        """
        if not value:
            return ''
        if env.context.get('export_raw_data'):
            return value
        return self.__decrypt(value)
