import collections
from copy import deepcopy

from formiodata.builder import Builder
from formiodata.form import Form

from .base_config_components import *
from . import custom_components
import logging

from .widgets_table import TableWidget

logger = logging.getLogger(__name__)


class TableFormWidget(TableWidget):

    def __init__(self, templates_engine, request, settings, schema={}, form_schema={}, resource_ext=None,
                 disabled=False, **kwargs):
        super(TableFormWidget, self).__init__(
            templates_engine, request, settings, schema=schema, resource_ext=resource_ext,
            disabled=disabled, **kwargs
        )
        self.form_schema = form_schema
        self.builder = Builder(
            self.form_schema, resources_ext=self.ext_resource,
            template_engine=templates_engine, components_base_path=self.components_base_path,
            disabled=self.disabled
        )

    def make_def_table(self, data, **kwargs):
        logger.info("make_def_table")
        self.form_c = Form({}, self.builder)
        self.title = self.form_schema['title']
        self.name = self.form_schema['id']
        return self.render_def_table(data, **kwargs)

    def get_columns(self, data):
        cols = {'id': 'id'}
        for key, component in self.builder.components.items():
            if component.raw.get('tableView') and component.raw.get('type') and not component.raw.get(
                    'tableView') == "dataGrid":
                cols[component.key] = component.label
        return collections.OrderedDict(cols.copy())
