# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

import json
from collections import OrderedDict

from formiodata.utils import base64_encode_url, decode_resource_template, fetch_dict_get_value
from .default_config_components import *
import copy


class Component:

    def __init__(self, raw, builder, **kwargs):
        # TODO or provide the Builder object?
        self.raw = copy.deepcopy(raw)
        self.builder = builder
        self.form = {}

        # i18n (language, translations)
        self.language = kwargs.get('language', 'en')
        self.i18n = kwargs.get('i18n', {})
        self.resources = kwargs.get('resources', False)
        self.resources_ext = kwargs.get('resources_ext', False)
        if self.resources and isinstance(self.resources, str):
            self.resources = json.loads(self.resources)
        self.html_component = ""
        self.defaultValue = self.raw.get('defaultValue')
        self.tmpe = builder.tmpe
        self.components_base_path = builder.components_base_path
        self.component_items = []
        self.multi_row = False
        self.grid_rows = []

    @property
    def key(self):
        return self.raw.get('key')

    @key.setter
    def key(self, value):
        self.raw['key'] = value

    @property
    def type(self):
        return self.raw.get('type')

    @property
    def input(self):
        return self.raw.get('input')

    @property
    def properties(self):
        return self.raw.get('properties')

    @property
    def label(self):
        label = self.raw.get('label')
        if self.i18n.get(self.language):
            return self.i18n[self.language].get(label, label)
        else:
            return label

    @label.setter
    def label(self, value):
        if self.raw.get('label'):
            self.raw['label'] = value

    @property
    def value(self):
        return self.form.get('value')

    @value.setter
    def value(self, value):
        print("Set Value ", self.key, value)
        self.form['value'] = value

    @property
    def hidden(self):
        return self.raw.get('hidden')

    def make_config_new(self, component, id_form, id_submission, disabled=False, cls_size=" col-lg-12 "):
        cfg_map = form_io_default_map.copy()
        cfg = {}
        for key, value in component.items():
            if key not in cfg_map:
                cfg[key] = value
                if key == "width":
                    cls_size = f" col-lg-{value}"
            else:
                if isinstance(cfg_map[key], dict):
                    if component.get(key):
                        node_cfg = cfg_map.get(key)
                        node = value
                        for iitem in node_cfg:
                            k = node_cfg[iitem]
                            v = node.get(iitem, "")
                            if k:
                                if k == 'label':
                                    v = self.i18n.get(v, v)
                                if k == "customClass" and v == "":
                                    v = cls_size
                                cfg[k] = v
                else:
                    k = cfg_map[key]
                    v = value
                if k:
                    if k == 'label':
                        v = self.i18n.get(v, v)
                    if k == "customClass" and v == "":
                        v = cls_size
                    cfg[k] = v
        if "customClass" not in cfg:
            cfg['customClass'] = cls_size
        cfg['disabled'] = disabled
        cfg['items'] = self.component_items
        cfg['id_form'] = id_form
        cfg["id_submission"] = id_submission or ""
        if self.value:
            cfg["value"] = self.value
        return cfg

    def render_template(self, name: str, context: dict):
        template = self.tmpe.get_template(name)
        return template.render(context)

    def log_render(self, cfg, size="12"):
        print("-------------------------")
        print(self.key)
        print(size)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(self.raw)
        print(cfg)
        print("-------------------------")

    def render(self, id_form, id_submission, size="12", log=False):
        cfg = self.make_config_new(self.raw, id_form, id_submission, disabled=self.builder.disabled, cls_size=f"col-lg-{size}")
        if log:
            self.log_render(cfg, size)
        if self.key == "submit":
            return ""
        self.html_component = self.render_template(
            f"{self.components_base_path}{formio_map[self.raw.get('type')]}", cfg)
        return self.html_component

    def compute_data(self, data):
        return data.copy()


# global

class formComponent(Component):
    pass


# Basic

class textfieldComponent(Component):
    pass


class textareaComponent(Component):
    pass


class numberComponent(Component):
    pass


class passwordComponent(Component):
    pass


class checkboxComponent(Component):
    pass


class selectboxesComponent(Component):

    @property
    def values_labels(self):
        comp = self.builder.form_components.get(self.key)
        builder_values = comp.raw.get('values')
        values_labels = {}
        for b_val in builder_values:
            if self.value and b_val.get('value'):
                if self.i18n.get(self.language):
                    label = self.i18n[self.language].get(b_val['label'], b_val['label'])
                else:
                    label = b_val['label']
                val = {'key': b_val['value'], 'label': label, 'value': self.value.get(b_val['value'])}
                values_labels[b_val['value']] = val
        return values_labels


class selectComponent(Component):

    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.item_data = {}
        self.template_label_keys = []
        if self.raw.get('template'):
            self.template_label_keys = decode_resource_template(self.raw.get('template'))
        self.compute_resources()

    def compute_resources(self):
        resource_id = self.raw.get('resource')
        if resource_id and not resource_id == "":
            if not self.resources and self.resources_ext:
                resource_list = self.resources_ext(resource_id)
            else:
                resource_list = self.resources[resource_id]
            if resource_list:
                self.raw['data'] = {"values": []}
                for item in resource_list:
                    label = fetch_dict_get_value(item, self.template_label_keys[:])
                    self.raw['data']['values'].append({
                        "label": label,
                        "value": item['_id']
                    })

    @Component.value.setter
    def value(self, value):
        if self.template_label_keys and isinstance(value, dict):
            self.form['value'] = value.get('_id', value)
        else:
            self.form['value'] = value

    @property
    def value_label(self):
        comp = self.builder.form_components.get(self.key)
        values = comp.raw.get('data') and comp.raw['data'].get('values')
        for val in values:
            if val['value'] == self.value:
                label = val['label']
                if self.i18n.get(self.language):
                    return self.i18n[self.language].get(label, label)
                else:
                    return label
        else:
            return False

    @property
    def value_labels(self):
        comp = self.builder.form_components.get(self.key)
        values = comp.raw.get('data') and comp.raw['data'].get('values')
        value_labels = []
        for val in values:
            if val['value'] in self.value:
                if self.i18n.get(self.language):
                    value_labels.append(self.i18n[self.language].get(val['label'], val['label']))
                else:
                    value_labels.append(val['label'])
        return value_labels

    @property
    def data(self):
        return self.raw.get('data')

    @property
    def values(self):
        return self.raw.get('data').get('values')


class radioComponent(Component):

    @property
    def values_labels(self):
        comp = self.builder.form_components.get(self.key)
        builder_values = comp.raw.get('values')
        values_labels = {}

        for b_val in builder_values:
            if self.i18n.get(self.language):
                label = self.i18n[self.language].get(b_val['label'], b_val['label'])
            else:
                label = b_val['label']
            val = {'key': b_val['value'], 'label': label, 'value': b_val['value'] == self.value}
            values_labels[b_val['value']] = val
        return values_labels

    @property
    def value_label(self):
        comp = self.builder.form_components.get(self.key)
        builder_values = comp.raw.get('values')
        value_label = {}

        for b_val in builder_values:
            if b_val['value'] == self.value:
                if self.i18n.get(self.language):
                    return self.i18n[self.language].get(b_val['label'], b_val['label'])
                else:
                    return b_val['label']
        else:
            return False


class buttonComponent(Component):
    pass


# Advanced

class emailComponent(Component):
    pass


class urlComponent(Component):
    pass


class phoneNumberComponent(Component):
    pass


# TODO: tags, address


class datetimeComponent(Component):
    pass


class dateComponent(Component):
    pass


class timeComponent(Component):
    pass


class currencyComponent(Component):
    pass


class surveyComponent(Component):
    pass


class signatureComponent(Component):
    pass


# Layout components

class htmlelementComponent(Component):
    pass


class contentComponent(Component):
    pass


class columnsComponent(Component):
    pass


class columnComponent(Component):
    pass


class fieldsetComponent(Component):
    pass


class panelComponent(Component):

    @property
    def title(self):
        component = self.builder.components.get(self.key)
        title = component.raw.get('title')
        if not title:
            title = component.raw.get('label')

        if self.i18n.get(self.language):
            return self.i18n[self.language].get(title, title)
        else:
            return title


class tableComponent(Component):
    pass


class tabsComponent(Component):
    pass


# Data components

class datagridRowComponent(Component):
    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.headers = []
        self.grid = None
        self.min_row = 1
        self.max_row = 1
        self.row_id = 0

    def make_config_new(self, component, id_form, id_submission, disabled=False, cls_size=" col-lg-12 "):
        cfg = super(datagridRowComponent, self).make_config_new(
            component, id_form, id_submission, disabled=disabled, cls_size=cls_size
        )
        cfg['row_id'] = self.row_id
        return cfg


class datagridComponent(Component):

    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.headers = []
        self.multi_row = True
        self.min_row = 1
        self.max_row = 1
        self.add_enabled = True
        self.row_id = 0
        self.aval_validate_row()

    def aval_validate_row(self):
        if self.raw.get("validate"):
            if self.raw.get("validate").get("minLength"):
                self.min_row = int(self.raw.get("validate").get("minLength"))
            if self.raw.get("validate").get("maxLength"):
                self.max_row = int(self.raw.get("validate").get("maxLength"))

    def make_config_new(self, component, id_form, id_submission, disabled=False, cls_size=" col-lg-12 "):
        cfg = super(datagridComponent, self).make_config_new(
            component, id_form, id_submission, disabled=disabled, cls_size=cls_size
        )
        cfg['min_rows'] = self.min_row
        cfg['max_rows'] = self.max_row
        return cfg

    @property
    def labels(self):
        labels = OrderedDict()
        for comp in self.raw['components']:
            if self.i18n.get(self.language):
                label = self.i18n[self.language].get(comp['label'], comp['label'])
            else:
                label = comp['label']
            labels[comp['key']] = label
            self.columns.append(label)
        return labels

    @property
    def rows(self):
        rows = []
        # Sanity check is really needed.
        # TODO add test for empty datagrid value.
        numrow = self.min_row
        if self.value:
            numrow = len(self.value)
        for row_id in range(numrow):
            row = self.get_row(row_id)
            rows.append(row)
        return rows

    def get_row(self, row_id):
        raw_row = OrderedDict()
        raw_row["key"] = f"{self.key}_dataGridRow_{row_id}"
        raw_row["type"] = "datagridRow"
        row = self.builder.get_component_object(raw_row)
        row.row_id = row_id
        for component in self.component_items:
            # Copy component raw (dict), to ensure no binding and overwrite.
            component_raw = component.raw.copy()
            component_raw['key'] = f"{self.key}_dataGridRow_{row_id}-{component_raw.get('key')}"
            component_obj = self.builder.get_component_object(component_raw)
            if self.value:
                for row_dict in self.value:
                    for key, val in row_dict.items():
                        if key == component_obj.key:
                            component_obj.value = val
            row.component_items.append(component_obj)
        return row

    def add_row(self, num_rows):
        return self.get_row(num_rows)

    def compute_data(self, data):
        data = super(datagridComponent, self).compute_data(data)
        c_keys = []
        for component in self.component_items:
            c_keys.append(component.key)
        key = self.key
        list_to_pop = []
        new_dict = {
            key: []
        }
        last_group = False
        data_row = {}
        for k, v in data.items():
            if f"{key}_" in k:
                list_to_pop.append(k)
                list_keys = k.split("-")
                if list_keys:
                    groups = list_keys[0].split("_")
                    if groups[2] != last_group:
                        if last_group:
                            new_dict[key].append(data_row.copy())
                            data_row = {}
                        last_group = groups[2]
                    if list_keys[1] in c_keys:
                        data_row[k] = data[k]
        new_dict[key].append(data_row.copy())
        for i in list_to_pop:
            data.pop(i)
        data = {**data, **new_dict}
        return data.copy()


# Premium components

class fileComponent(Component):

    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)

    @property
    def storage(self):
        return self.raw.get('storage')

    @property
    def url(self):
        return self.raw.get('url')

    @property
    def base64(self):
        if self.storage == 'url':
            res = ''
            for val in self.form.get('value'):
                name = val.get('name')
                url = val.get('url')
                res += base64_encode_url(url)
            return res
        elif self.storage == 'base64':
            return super().value


class resourceComponent(Component):

    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.item_data = {}
        self.template_label_keys = decode_resource_template(self.raw.get('template'))
        self.value_raw = ""
        self.compute_resources()

    def compute_resources(self):
        resource_id = self.raw.get('resource')
        if resource_id and not resource_id == "":
            if not self.resources and self.resources_ext:
                resource_list = self.resources_ext(resource_id)
            else:
                resource_list = self.resources[resource_id]
            if resource_list:
                self.raw['data'] = {"values": []}
                for item in resource_list:
                    label = fetch_dict_get_value(item, self.template_label_keys[:])
                    self.raw['data']['values'].append({
                        "label": label,
                        "value": item['_id']
                    })

    @Component.value.setter
    def value(self, value):
        if self.template_label_keys and isinstance(value, dict):
            self.form['value'] = value.get('_id', value)
        else:
            self.form['value'] = value

    @property
    def value_label(self):
        comp = self.builder.form_components.get(self.key)
        values = comp.raw.get('data') and comp.raw['data'].get('values')
        for val in values:
            if val['value'] == self.value:
                label = val['label']
                if self.i18n.get(self.language):
                    return self.i18n[self.language].get(label, label)
                else:
                    return label
        else:
            return False

    @property
    def value_labels(self):
        comp = self.builder.form_components.get(self.key)
        values = comp.raw.get('data') and comp.raw['data'].get('values')
        value_labels = []
        for val in values:
            if val['value'] in self.value:
                if self.i18n.get(self.language):
                    value_labels.append(self.i18n[self.language].get(val['label'], val['label']))
                else:
                    value_labels.append(val['label'])
        return value_labels

    @property
    def data(self):
        return self.raw.get('data')

    @property
    def values(self):
        return self.raw.get('data').get('values')
