from copy import deepcopy

from formiodata.builder import Builder
from formiodata.form import Form

from .base_config_components import *
from . import custom_components
import logging
import uuid
from .widgets_content import PageWidget

logger = logging.getLogger(__name__)


class CustomBuilder(Builder):

    def __init__(self, schema_json, **kwargs):
        self.tmpe = kwargs.get('template_engine', False)
        self.disabled = kwargs.get('disabled', False)
        self.components_base_path = kwargs.get('components_base_path', False)
        self.settings = kwargs.get('settings', False)
        super(CustomBuilder, self).__init__(schema_json, **kwargs)
        self.table_colums = []
        self.table_colums_types = []

    def load_components(self):
        self._raw_components = self.schema.get('components')
        self.raw_components = deepcopy(self.schema.get('components'))
        self.main = self.get_component_object({'type': 'form'})
        if self.raw_components:
            self._load_components(self.raw_components, self.main)

    def _load_components(self, components, parent, is_columns=False):
        """
        @param components
        """
        for component in components:
            if not parent.type == "components":
                if is_columns:
                    component['type'] = 'column'
                component_obj = self.get_component_object(component)
                if parent:
                    component_obj.parent = parent

                component_obj.id = component.get('id', str(uuid.uuid4()))
                self.component_ids[component_obj.id] = component_obj

                component['_object'] = component_obj
                if component.get('key') and component.get('input'):
                    self.form_components[component.get('key')] = component_obj
                    self.components[component.get('key')] = component_obj
                else:
                    if component.get('key'):
                        key = component.get('key')
                    elif self.components.get(component.get('type')):
                        key = component.get('type') + '_x'
                    else:
                        key = component.get('type')
                    if not component.get('type') == "components":
                        self.components[key] = component_obj
                parent.component_items.append(component_obj)
                if component.get('components'):
                    self._load_components(component.get('components'), component_obj)
                if component.get('columns'):
                    self._load_components(component.get('columns'), component_obj, is_columns=True)

    def get_component_object(self, component):
        """
        @param component
        """
        component_type = component.get('type')
        if not component_type == "components":
            try:
                cls_name = '%sComponent' % component_type
                cls = getattr(custom_components, cls_name)
                return cls(
                    component, self, language=self.language,
                    i18n=self.i18n, resources=self.resources,
                    resources_ext=self.resources_ext
                )
            except AttributeError as e:
                # TODO try to find/load first from self._component_cls else
                # re-raise exception or silence (log error and return False)
                logging.error(e)
                return custom_components.Component(component, self)
        else:
            return False


class CustomForm(Form):

    def load_components(self):
        for component in self.builder.main.component_items:
            self._load_components(component)

    def _load_components(self, component):
        component.value = self.form.get(component.key, component.defaultValue)
        if not component.survey and not component.multi_row and component.component_items:
            for sub_component in component.component_items:
                self._load_components(sub_component)
        if component.survey:
            component.eval_rows()


class FormIoWidget(PageWidget):

    def __init__(self, templates_engine, request, settings, schema={}, resource_ext=None, disabled=False, **kwargs):
        super(FormIoWidget, self).__init__(
            templates_engine, request, settings, schema=schema, resource_ext=resource_ext,
            disabled=disabled, **kwargs
        )
        self.cls_title = " text-center "
        self.api_action = "/"
        self.curr_row = []
        self.schema = schema
        self.submission_id = ""
        self.form_name = ""
        self.builder = CustomBuilder(
            self.schema, resources_ext=self.ext_resource,
            template_engine=templates_engine, components_base_path=self.components_base_path,
            disabled=self.disabled, settings=settings
        )

    def print_structure(self):
        for node in self.builder.main.component_items:
            print(node, node.key, node.value, "---")
            if node.component_items:
                for sub_node in node.component_items:
                    print("--->", sub_node, sub_node.key, sub_node.value)
                    if sub_node.multi_row:
                        for row in sub_node.grid_rows:
                            for sub3_node in row:
                                print("------------->", sub3_node, sub3_node.key, sub3_node.value)
                    elif sub_node.component_items:
                        for sub2_node in sub_node.component_items:
                            print("-------->", sub2_node, sub2_node.key, sub2_node.value)
                            if sub2_node.component_items:
                                for sub3_node in sub2_node.component_items:
                                    print("------------->", sub3_node, sub3_node.key, sub3_node.value)

    def get_component_by_key(self, key):
        for node in self.builder.main.component_items:
            if node.key == key:
                return node
            if node.component_items:
                for sub_node in node.component_items:
                    if sub_node.key == key:
                        return sub_node
                    if sub_node.multi_row:
                        for row in sub_node.grid_rows:
                            for sub3_node in row:
                                if sub3_node.key == key:
                                    return sub3_node
                    elif sub_node.component_items:
                        for sub2_node in sub_node.component_items:
                            if sub2_node.key == key:
                                return sub2_node
                            if sub2_node.component_items:
                                for sub3_node in sub2_node.component_items:
                                    if sub3_node.key == key:
                                        return sub3_node

    def compute_component_data(self, form_data):
        data = form_data.copy()
        for node in self.builder.main.component_items:
            data = node.compute_data(data)
            if node.component_items:
                for sub_node in node.component_items:
                    data = sub_node.compute_data(data)
                    if sub_node.multi_row:
                        for row in sub_node.grid_rows:
                            for sub3_node in row:
                                data = sub3_node.compute_data(data)
                    elif sub_node.component_items:
                        for sub2_node in sub_node.component_items:
                            data = sub2_node.compute_data(data)
                            if sub2_node.component_items:
                                for sub3_node in sub2_node.component_items:
                                    data = sub3_node.compute_data(data)
        return data

    def load_data(self, data):
        self.form_c = CustomForm(data, self.builder)

    def make_form(self, data):
        self.load_data(data)
        # self.print_structure()
        self.title = self.schema['title']
        self.name = self.schema['name']
        self.form_id = self.schema['id']
        submit = self.builder.components.get("submit")
        if submit:
            self.label = submit.label
        return self.render_form()

    def render_form(self):
        template = f"{self.components_base_path}{formio_map[self.builder.main.type]}"
        values = {
            "items": self.builder.main.component_items,
            # "items": self.builder.form_components,
            # "component": self.builder.main,
            "title": self.title,
            "cls_title": self.cls_title,
            "api_action": self.api_action,
            "label": self.label,
            "name": self.name,
            "id_form": self.form_id,
            "id_submission": self.submission_id,
            "disabled": self.disabled
        }

        return self.render_template(
            template, values
        )

    def grid_rows(self, key, render=False, log=False):
        results = {
            "rows": [],
            "showAdd": False
        }
        component = self.get_component_by_key(key)
        rows = component.rows
        results['showAdd'] = component.add_enabled
        for row in rows:
            logger.info(row)
            if render:
                results['rows'].append(row.render(self.name, self.submission_id, log=log))
            else:
                results['rows'].append(row)
        return results

    def grid_add_row(self, key, num_rows, render=False, log=False):
        results = {
            "row": "",
            "showAdd": False
        }
        component = self.get_component_by_key(key)
        row = component.add_row(num_rows)
        results['showAdd'] = component.add_enabled
        if render:
            results['row'] = row.render(self.name, "", log=log)
            return results
        else:
            results['row'] = row
            return results
