from .widgets_base import WidgetsBase


class PageWidget(WidgetsBase):

    def __init__(self, templates_engine, request, settings, schema={}, resource_ext=None, disabled=False, **kwargs):
        super(PageWidget, self).__init__(templates_engine, request, **kwargs)
        self.base_path = kwargs.get('base_path', "/")
        self.page_api_action = kwargs.get('page_api_action', "/")
        self.settings = settings
        self.schema = schema
        self.ext_resource = resource_ext
        self.beforerows = []
        self.disabled = disabled

    def get_login_act(self, session):
        return 'logout' if session.get('logged_in') else 'login'

    def get_config(self, session: dict, **context):
        today_date = self.dte.get_tooday_ui()
        avatar = "/avatars/"
        if session.get('logged_in'):
            if session.get('name'):
                user = session.get('name', "test")
            else:
                user = session.get('username', "Test")
            avatar = session.get('avatar', "/avatars/")
        else:
            user = False
        base_prj_data = {
            "token": self.authtoken,
            'app_name': self.settings.app_name,
            'version': self.settings.app_version,
            'env': "test",
            'login_act': self.get_login_act(session),
            'login_user': user,
            'avatar': avatar,
            'today_date': today_date,
            "beforerows": self.beforerows,
            "backtop": self.backtop,
            "error": self.error,
            "export_button": self.export_btn,
            "rows": self.rows,
            "request": self.request,
            "base_path": self.base_path,
            "page_api_action": self.page_api_action,
            "logo_img_url": self.settings.logo_img_url

        }
        kwargs_def = {**context, **base_prj_data}
        return kwargs_def

    def render_page(self, template_name_or_list: str, session: dict, **context):
        kwargs_def = self.get_config(session, **context)
        return self.response_template(template_name_or_list, kwargs_def)

    def render_custom(self, tmpname, cfg):
        return self.render_template(f"{tmpname}", cfg)
