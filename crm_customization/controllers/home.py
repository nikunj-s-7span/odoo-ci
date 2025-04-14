from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from werkzeug.utils import redirect


class CustomLoginRedirect(Home):

    @http.route("/web/login", type="http", auth="public")
    def web_login(self, *args, **kw):
        # Call the original login method
        response = super(CustomLoginRedirect, self).web_login(*args, **kw)
        return response
        # Check if the user is successfully logged in
        if request.params.get("login_success"):
            # Get the CRM menu's ID and action ID
            crm_menu = request.env.ref("crm.crm_menu_root").id
            crm_action = request.env.ref("crm.crm_lead_action_pipeline").id

            # Construct the URL with menu and action
            crm_url = f"/web?#menu_id={crm_menu}&action={crm_action}"
            # Redirect to CRM
            return redirect(crm_url)

        # Return the original response for unsuccessful logins
        return response
