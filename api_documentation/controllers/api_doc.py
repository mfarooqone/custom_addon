from odoo import http
from odoo.http import request


class ApiDocumentation(http.Controller):

    @http.route('/api/docs', type='http', auth='user', methods=['GET'])
    def api_docs(self, **kwargs):
        """Common API documentation page. Other modules extend the QWeb template."""
        return request.render('api_documentation.api_doc_page', {
            'base_url': request.httprequest.host_url.rstrip('/'),
        })
