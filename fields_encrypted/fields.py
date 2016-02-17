# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields
import base64
from Crypto.Cipher import AES
from Crypto import Random


# @TODO: SuperSecretKeyThatShouldBeReplacedWithAnEnvVarOrSomething
KEY = '=\x1f\x94\x8fQ\xe4l\x18\xf7\xf5\x15\x14\x7fP\x13^\xd7O\xc0W@;\xde\xa2'


class EncryptedText(fields._String):
    """
    Identical to fields.Text, except encrypted in the database

    :param translate: whether the value of this field can be translated
    """
    type = 'text'

    BS = 16
    KEY = KEY

    def _decrypt(self, value):
        """
        Decrypt a value

        Params:
            value: String to decrypt
        """
        def unpad(s):
            return s[:-ord(s[len(s)-1:])]
        value = base64.b64decode(value)
        iv = value[:16]
        cipher = AES.new(self.KEY, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(value[16:]))

    def _encrypt(self, value):
        """
        Encrypt a value

        Params:
            value: String to encrypt
        """
        def pad(s, bs=self.BS):
            return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        value = pad(value)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.KEY, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(value))

    def convert_to_cache(self, value, record, validate=True):
        """
        Convert ``value`` to the cache level in ``env``; ``value`` may come
        from an assignment, or have the format of methods
        :meth:`BaseModel.read` or :meth:`BaseModel.write`

        Params:
            value: str
            record: the target record for the assignment,
                or an empty recordset
            validate: bool when True, field-specific validation of
                ``value`` will be performed
        """
        return self._encrypt(value)

    def convert_to_read(self, value, use_name_get=True):
        """
        Convert ``value`` from the cache to a value as returned by method
        :meth:`BaseModel.read`

        Params:
            value: str
            use_name_get: bool when True, value's diplay name will
                    be computed using :meth:`BaseModel.name_get`, if relevant
                    for the field
        """
        return False if value is None else self._decrypt(value)

    def convert_to_write(self, value, target=None, fnames=None):
        """
        Convert ``value`` from the cache to a valid value for method
        :meth:`BaseModel.write`.

        Params:
            value: str
            target: optional, the record to be modified with this value
            fnames: for relational fields only, an optional collection
                of field names to convert
        """
        return value

    def convert_to_onchange(self, value):
        """
        Convert ``value`` from the cache to a valid value for an onchange
        method v7.

        Params:
            value: str
        """
        return self._decrypt(value)

    def convert_to_export(self, value, env):
        """
        Convert ``value`` from the cache to a valid value for export. The
        parameter ``env`` is given for managing translations.

        Params:
            value: str
        """
        if not value:
            return ''
        if env.context.get('export_raw_data'):
            return value
        return self._decrypt(value)
