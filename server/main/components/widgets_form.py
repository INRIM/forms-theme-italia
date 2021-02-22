from copy import deepcopy

from formiodata.builder import Builder
from formiodata.form import Form

from .default_config_components import *
from . import custom_components
import logging

from .widgets_content import PageWidget

logger = logging.getLogger(__name__)


class CustomBuilder(Builder):

    def __init__(self, schema_json, **kwargs):
        self.tmpe = kwargs.get('template_engine', False)
        self.disabled = kwargs.get('disabled', False)
        self.components_base_path = kwargs.get('components_base_path', False)

        super(CustomBuilder, self).__init__(schema_json, **kwargs)

    def load_components(self):
        self._raw_components = self.schema.get('components')
        self.raw_components = deepcopy(self.schema.get('components'))
        self.main = self.get_component_object({'type': 'form'})
        if self.raw_components:
            self._load_components(self.raw_components, self.main)

    def _load_components(self, components, parent):
        """
        @param components
        """
        for component in components:
            if not parent.type == "components":
                component_obj = self.get_component_object(component)
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
                for k, vals in component.copy().items():
                    if isinstance(vals, list):
                        for v in vals:
                            if 'components' in v:
                                if not k == "components":
                                    next_o = self.get_component_object({'type': k})
                                    if not next_o.type == "components":
                                        component_obj.component_items.append(next_o)
                                        self._load_components(v.get('components'), next_o)

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


class FormIoWidget(PageWidget):

    def __init__(self, templates_engine, request, settings, schema={}, resource_ext=None, disabled=False):
        super(FormIoWidget, self).__init__(
            templates_engine, request, settings, schema=schema, resource_ext=resource_ext,
            disabled=disabled
        )
        self.cls_title = " text-center "
        self.api_action = "/"
        self.curr_row = []
        self.schema = schema
        self.form_name = ""
        self.builder = CustomBuilder(
            self.schema, resources_ext=self.ext_resource,
            template_engine=templates_engine, components_base_path=self.components_base_path,
            disabled=self.disabled
        )

    def print_structure(self):
        for node in self.builder.main.component_items:
            print(node, node.key)
            if node.component_items:
                for sub_node in node.component_items:
                    print("--->", sub_node, sub_node.key)
                    if sub_node.component_items:
                        for sub2_node in sub_node.component_items:
                            print("-------->", sub2_node, sub2_node.key)
                            if sub2_node.component_items:
                                for sub3_node in sub2_node.component_items:
                                    print("------------->", sub3_node, sub3_node.key)

    def make_form(self, data):
        # self.print_structure()
        self.form_c = Form(data, self.builder)
        self.title = self.schema['title']
        self.name = self.schema['_id']
        submit = self.form_c.components.get("submit")
        if submit:
            self.label = submit.label
        # self.fetch_components(schema)
        return self.render_form()

    def render_form(self):
        template = f"{self.components_base_path}{formio_map[self.builder.main.type]}"
        values = {
            "items": self.builder.main.component_items,
            # "component": self.builder.main,
            "title": self.title,
            "cls_title": self.cls_title,
            "api_action": self.api_action,
            "label": self.label,
            "id_form": self.name,
            "disabled": self.disabled
        }

        return self.render_template(
            template, values
        )

    def render_component(self, component, cfg):
        return self.render_template(f"{self.components_base_path}{component}", cfg)


