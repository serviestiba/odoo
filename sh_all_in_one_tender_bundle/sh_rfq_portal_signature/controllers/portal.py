# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import http, fields
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import CustomerPortal
import binascii


class CustomerSignaturePortal(CustomerPortal):

    @http.route(['/my/purchase/<int:quote_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, quote_id, access_token=None, name=None, signature=None):
        """This controller is made for digital signature in rfq"""
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get(
            'access_token')
        try:
            quote_sudo = self._document_check_access(
                'purchase.order', quote_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid quotation.')}

        if not quote_sudo.has_to_be_signed():
            return {'error': _('The quotation is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            quote_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}
        return {
            'force_refresh': True,
        }
