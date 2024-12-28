# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import math

from werkzeug import urls

from odoo.http import content_disposition, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal

import logging
_logger = logging.getLogger(__name__)

# --------------------------------------------------
# Misc tools
# --------------------------------------------------

# def pager(url, total, page=1, step=30, scope=5, url_args=None):
#     """ Generate a dict with required value to render `website.pager` template.
#
#     This method computes url, page range to display, ... in the pager.
#
#     :param str url : base url of the page link
#     :param int total : number total of item to be splitted into pages
#     :param int page : current page
#     :param int step : item per page
#     :param int scope : number of page to display on pager
#     :param dict url_args : additionnal parameters to add as query params to page url
#     :returns dict
#     """
#     # Compute Pager
#     page_count = int(math.ceil(float(total) / step))
#
#     page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
#     scope -= 1
#
#     pmin = max(page - int(math.floor(scope/2)), 1)
#     pmax = min(pmin + scope, page_count)
#
#     if pmax - pmin < scope:
#         pmin = pmax - scope if pmax - scope > 0 else 1
#
#     def get_url(page):
#         _url = "%s/page/%s" % (url, page) if page > 1 else url
#         if url_args:
#             _url = "%s?%s" % (_url, urls.url_encode(url_args))
#         return _url
#
#     return {
#         "page_count": page_count,
#         "offset": (page - 1) * step,
#         "page": {
#             'url': get_url(page),
#             'num': page
#         },
#         "page_first": {
#             'url': get_url(1),
#             'num': 1
#         },
#         "page_start": {
#             'url': get_url(pmin),
#             'num': pmin
#         },
#         "page_previous": {
#             'url': get_url(max(pmin, page - 1)),
#             'num': max(pmin, page - 1)
#         },
#         "page_next": {
#             'url': get_url(min(pmax, page + 1)),
#             'num': min(pmax, page + 1)
#         },
#         "page_end": {
#             'url': get_url(pmax),
#             'num': pmax
#         },
#         "page_last": {
#             'url': get_url(page_count),
#             'num': page_count
#         },
#         "pages": [
#             {'url': get_url(page_num), 'num': page_num} for page_num in range(pmin, pmax+1)
#         ]
#     }
#
#
# def get_records_pager(ids, current):
#     if current.id in ids and (hasattr(current, 'website_url') or hasattr(current, 'access_url')):
#         attr_name = 'access_url' if hasattr(current, 'access_url') else 'website_url'
#         idx = ids.index(current.id)
#         prev_record = idx != 0 and current.browse(ids[idx - 1])
#         next_record = idx < len(ids) - 1 and current.browse(ids[idx + 1])
#
#         if prev_record and prev_record[attr_name] and attr_name == "access_url":
#             prev_url = '%s?access_token=%s' % (prev_record[attr_name], prev_record._portal_ensure_token())
#         elif prev_record and prev_record[attr_name]:
#             prev_url = prev_record[attr_name]
#         else:
#             prev_url = prev_record
#
#         if next_record and next_record[attr_name] and attr_name == "access_url":
#             next_url = '%s?access_token=%s' % (next_record[attr_name], next_record._portal_ensure_token())
#         elif next_record and next_record[attr_name]:
#             next_url = next_record[attr_name]
#         else:
#             next_url = next_record
#
#         return {
#             'prev_record': prev_url,
#             'next_record': next_url,
#         }
#     return {}
#
#
# def _build_url_w_params(url_string, query_params, remove_duplicates=True):
#     """ Rebuild a string url based on url_string and correctly compute query parameters
#     using those present in the url and those given by query_params. Having duplicates in
#     the final url is optional. For example:
#
#      * url_string = '/my?foo=bar&error=pay'
#      * query_params = {'foo': 'bar2', 'alice': 'bob'}
#      * if remove duplicates: result = '/my?foo=bar2&error=pay&alice=bob'
#      * else: result = '/my?foo=bar&foo=bar2&error=pay&alice=bob'
#     """
#     url = urls.url_parse(url_string)
#     url_params = url.decode_query()
#     if remove_duplicates:  # convert to standard dict instead of werkzeug multidict to remove duplicates automatically
#         url_params = url_params.to_dict()
#     url_params.update(query_params)
#     return url.replace(query=urls.url_encode(url_params)).to_url()


class UserPortal(CustomerPortal):
    """ Override of CustomerPortal to add portal-specific routes"""

    MANDATORY_BILLING_FIELDS = ["name", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "phone", "email", "street", "city",]

    _items_per_page = 80


    @route(['/web/portal', '/web/portal/home', '/my/home', '/web/portal/my/profile'], type='http', auth="user", website=True)
    def home(self, **kw):
        return request.redirect('/profile/view')

    @route(['/web/portal/my/profile/edit'], type='http', auth='user', website=True)
    def edit_profile(self, redirect=None, **post):
        return request.redirect('/profile/edit')

    @route(['/my/security'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def security(self, **post):
        return request.redirect('/profile/security')

    @route(['/my/deactivate_account'], type='http', auth='user', website=True, methods=['POST'])
    def deactivate_account(self, validation, password, **post):
        return request.redirect('/profile/deactivate_account')

