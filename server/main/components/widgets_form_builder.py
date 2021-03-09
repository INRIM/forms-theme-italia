from copy import deepcopy

from formiodata.builder import Builder
from formiodata.form import Form

from .default_config_components import *
from . import custom_components
import logging

from .widgets_content import PageWidget

logger = logging.getLogger(__name__)


class FormIoBuilderWidget(PageWidget):

    def __init__(self, templates_engine, request, settings, components, form_id, resource_ext=None, disabled=False,
                 **kwargs):
        super(FormIoBuilderWidget, self).__init__(
            templates_engine, request, settings, schema={}, resource_ext=resource_ext,
            disabled=disabled, **kwargs
        )
        self.cls_title = " text-center "
        self.api_action = "/"
        self.title = kwargs.get('title', "")
        self.name = kwargs.get('name', "")
        self.action_buttons = kwargs.get('action_buttons', "/")
        self.base_form_url = kwargs.get('base_form_url', "/")
        self.preview_link = kwargs.get('preview_link', "/")
        self.curr_row = []
        self.submission_id = ""
        self.form_name = ""
        self.components = components
        self.form_id = form_id

    def get_config(self, session: dict, **context):
        cfg = super(FormIoBuilderWidget, self).get_config(
            session, **context
        )
        cfg['components'] = json.dumps(self.components)
        cfg['base_form_url'] = self.base_form_url
        cfg['action_buttons'] = self.action_buttons
        cfg['name'] = self.name
        cfg['title'] = self.title
        cfg['preview_link'] = self.preview_link
        return cfg
