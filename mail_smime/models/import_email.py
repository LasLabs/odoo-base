# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs, Inc.
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

from openerp.tools.import_email import ReceiverEmail2Event
from tempfile import TemporaryFile
from M2Crypto import BIO, SMIME


class ReceiverEmail2Event(ReceiverEmail2Event):
    
    SMIME_CONTENT_TYPES = [
        'application/pkcs7-signature'
    ]
    CERTSTORE = '/etc/ssl/certs/ca-certificates.crt'
    
    def __setup_smime(self):
        """
        Set up the SMIME.SMIME instance
        and loads the CA certificates store
        """
        smime = SMIME.SMIME()
        st = X509.X509_Store()
        if not os.access(self.CERTSTORE, os.R_OK):
            raise VerifierError, "cannot access %s" % self.CERTSTORE
        st.load_info(self.CERTSTORE)
        smime.set_x509_store(st)
        self._smime = smime
    
    def validate_smime(self, msg_part, ):
        '''
        Validates SMIME certs
        :param  msg_part: email.message
        :return signer_certs: valid signer certs
        '''
        _dashes = '-----'
        if self._smime is None:
            self.__setup_smimesetup()
        if msg_part.get_content_type() in self.SMIME_CONTENT_TYPES:
            with TemporaryFile('r+b') as fh:
                fh.write('%sBEGIN PKCS7%s\n%s\n%sEND PKCS7%s' % (
                            _dashes, _dashes,
                            msg_part.get_payload(),
                            _dashes, _dashes
                        ))
                fh.seek(0)
                pfh = BIO.File(fh)
                p7 = SMIME.load_pkcs7_bio(pf)
                sk3 = p7.get0_signers(X509.X509_Stack())
                if len(sk3) == 0:
                    raise []
                signer_certs = []
                for cert in sk3:
                    signer_certs.append(
                        "%sBEGIN CERTIFICATE%s\n%s\n%sEND CERTIFICATE%s" % (
                            _dashes, _dashes,
                            base64.encodestring(cert.as_der()),
                            _dashes, _dashes
                        ))
                self._smime.set_x509_stack(sk3)
                try:
                    v = self._smime.verify(p7)
                except SMIME.SMIME_Error, e:
                    return []
                if data_bio is not None and data != v:
                    raise []
                return signer_certs
        return []
    
    def save_mail(self, msg, subject, partners):
        counter, description = 1, u''
        signer_certs = []
        if msg.is_multipart():
            for part in msg.get_payload():
                stockdir = os.path.join('emails', msg['Message-Id'][1:-1])
                newdir = os.path.join('/tmp', stockdir)
                filename = part.get_filename()
                if not filename:
                    ext = mimetypes.guess_extension(part.get_type())
                    if not ext:
                        ext = '.bin'
                    filename = 'part-%03d%s' % (counter, ext)

                if part.get_content_maintype() == 'multipart':
                    continue
                elif part.get_content_type() in self.SMIME_CONTENT_TYPES:
                    signer_certs.extend(self.validate_smime(part))
                elif part.get_content_maintype() == 'text':
                    if part.get_content_subtype() == 'plain':
                        description += part.get_payload(decode=1).decode(part.get_charsets()[0])
                        description += u'\n\nVous trouverez les éventuels fichiers dans le répertoire: %s' % stockdir
                        continue
                    else:
                        description += u'\n\nCe message est en "%s", vous trouverez ce texte dans le répertoire: %s' % (part.get_content_type(), stockdir)
                elif part.get_content_type() == 'message/rfc822':
                    continue
                if not os.path.isdir(newdir):
                    os.mkdir(newdir)

                counter += 1
                fd = file(os.path.join(newdir, filename), 'w')
                fd.write(part.get_payload(decode=1))
                fd.close()
        else:
            description = msg.get_payload(decode=1).decode(msg.get_charsets()[0])

        project = self.project_re.search(subject)
        if project:
            project = project.groups()[0]
        else:
            project = ''

        for partner in partners:
            self.rpc(('res.partner.event', 'create', {
                'name' : subject,
                'partner_id' : partner,
                'description' : description,
                'project' : project,
                'valid_signed': len(signer_certs) > 0,
            }))
