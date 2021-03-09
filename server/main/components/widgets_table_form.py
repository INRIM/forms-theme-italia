import collections
from copy import deepcopy

from formiodata.builder import Builder
from formiodata.form import Form

from .base_config_components import *
from . import custom_components
import logging

from .widgets_form import CustomBuilder
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
        self.builder = CustomBuilder(
            self.form_schema, resources_ext=self.ext_resource,
            template_engine=templates_engine, components_base_path=self.components_base_path,
            disabled=self.disabled, settings=settings
        )
    def print_structure(self):
        for node in self.builder.main.component_items:
            print(node, node.key, node.raw.get("tableView"))
            if node.component_items:
                for sub_node in node.component_items:
                    print("--->", sub_node, sub_node.key)
                    if sub_node.multi_row:
                        for row in sub_node.grid_rows:
                            for sub3_node in row:
                                print("------------->", sub3_node, sub3_node.key)
                    elif sub_node.component_items:
                        for sub2_node in sub_node.component_items:
                            print("-------->", sub2_node, sub2_node.key)
                            if sub2_node.component_items:
                                for sub3_node in sub2_node.component_items:
                                    print("------------->", sub3_node, sub3_node.key)

    def make_def_table(self, data, **kwargs):
        logger.info("make_def_table")
        self.form_c = Form({}, self.builder)
        self.print_structure()
        self.title = self.form_schema['title']
        self.name = self.form_schema['id']
        return self.render_def_table(data, **kwargs)

    def get_columns(self, data):
        cols = {'id': 'id'}
        for component in self.builder.main.component_items:
            if component.raw.get('tableView'):
                cols[component.key] = component.label
        return collections.OrderedDict(cols.copy())
