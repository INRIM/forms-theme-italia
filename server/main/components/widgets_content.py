
from .widgets_base import WidgetsBase



class PageWidget(WidgetsBase):

    def __init__(self, templates_engine, request, settings, schema={}, resource_ext=None, disabled=False):
        super(PageWidget, self).__init__(templates_engine, request)
        self.settings = settings
        self.schema = schema
        self.ext_resource = resource_ext
        self.beforerows = []
        self.disabled = disabled

    def get_login_act(self, session):
        return 'logout' if session.get('logged_in') else 'login'

    def render_page(self, template_name_or_list: str, session: dict, **context):

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
            "request": self.request
        }
        kwargs_def = {**context, **base_prj_data}
        return self.response_template(template_name_or_list, kwargs_def)
