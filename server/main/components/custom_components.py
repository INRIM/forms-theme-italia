# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

import json
from collections import OrderedDict

from formiodata.components import Component
from formiodata.utils import base64_encode_url, decode_resource_template, fetch_dict_get_value

from .DateEngine import DateEngine
from .base_config_components import *
import copy

import uuid


class CustomComponent(Component):

    def __init__(self, raw, builder, **kwargs):
        # TODO or provide the Builder object?
        super(CustomComponent, self).__init__(raw, builder, **kwargs)
        self.raw = copy.deepcopy(raw)

        # i18n (language, translations)

        self.tmpe = builder.tmpe
        self.components_base_path = builder.components_base_path
        self.component_items = []
        self.default_data = {
            self.key: ""
        }
        self.survey = False
        self.multi_row = False
        self.grid_rows = []
        self.size = 12

    @property
    def value(self):
        return self.form.get('value')

    @value.setter
    def value(self, value):
        self.form['value'] = value

    def make_config_new(self, component, id_form, id_submission, disabled=False, cls_size=" col-lg-12 "):
        cfg_map = form_io_default_map.copy()
        cfg = {}
        cvalue = self.value
        for key, value in component.items():
            if key not in cfg_map:
                cfg[key] = value
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
            cfg['customClass'] = f" col-lg-{self.size} "
        cfg['disabled'] = disabled
        cfg['items'] = self.component_items
        cfg['id_form'] = id_form
        cfg["id_submission"] = id_submission or ""
        if cvalue:
            cfg["value"] = cvalue
        return cfg

    def render_template(self, name: str, context: dict):
        template = self.tmpe.get_template(name)
        return template.render(context)

    def log_render(self, cfg, size="12"):
        logger.info("-------------------------")
        logger.info(self.key)
        logger.info(self.value)
        logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~")
        logger.info(self.form)
        logger.info("-------------------------")

    def render(self, id_form, id_submission, size="12", log=False):
        cfg = self.make_config_new(
            self.raw, id_form, id_submission, disabled=self.builder.disabled,
            cls_size=f"col-lg-{size}")
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
class formComponent(CustomComponent):
    pass


class textfieldComponent(CustomComponent):
    pass


class textareaComponent(CustomComponent):
    pass


class numberComponent(CustomComponent):
    pass


class infoComponent(CustomComponent):
    def make_config_new(self, component, id_form, id_submission, disabled=False, cls_size=" col-lg-12 "):
        cfg = super(infoComponent, self).make_config_new(
            component, id_form, id_submission, disabled=disabled, cls_size=cls_size
        )
        cfg['customClass'] = f" col-lg-{self.size} "
        return cfg


class passwordComponent(CustomComponent):
    pass


class checkboxComponent(CustomComponent):
    pass


class selectboxesComponent(CustomComponent):

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


class selectComponent(CustomComponent):

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

    @CustomComponent.value.setter
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


class radioComponent(CustomComponent):

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


class buttonComponent(CustomComponent):
    pass


# Advanced

class emailComponent(CustomComponent):
    pass


class urlComponent(CustomComponent):
    pass


class phoneNumberComponent(CustomComponent):
    pass


# TODO: tags, address


class datetimeComponent(CustomComponent):

    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.headers = []
        self.is_date = self.raw.get('enableDate', True)
        self.is_time = self.raw.get('enableTime', True)
        self.min = self.raw['widget']['minDate']
        self.max = self.raw['widget']['maxDate']
        self.client_format = self.builder.settings.ui_date_mask
        self.value_date = ""
        self.value_time = "00:00"
        self.value_datetime = ""
        self.dte = DateEngine(
            UI_DATETIME_MASK=self.builder.settings.ui_datetime_mask,
            SERVER_DTTIME_MASK=self.builder.settings.server_datetime_mask
        )
        self.size = 12

    @property
    def value(self):
        return self.form.get('value')

    @value.setter
    def value(self, vals):
        self.form['value'] = vals
        if self.is_date and self.is_time and vals:
            date_v = vals.split(" ")[0]
            if len(vals.split(" ")) > 1:
                time_v = vals.split(" ")[1]
            else:
                time_v = "00:00"
            self.value_date = self.dte.server_date_to_ui_date_str(date_v)
            self.value_time = f"{time_v}"
        elif self.is_date and vals:
            self.value_date = self.dte.server_date_to_ui_date_str(vals)
        elif self.is_time and vals:
            self.value_time = f"{vals}"

    def make_config_new(self, component, id_form, id_submission, disabled=False, cls_size=" col-lg-12 "):
        cfg = super(datetimeComponent, self).make_config_new(
            component, id_form, id_submission, disabled=disabled, cls_size=cls_size
        )
        cfg['value_date'] = self.value_date
        cfg['value_time'] = self.value_time
        if ":" in self.value_time:
            cfg['value_time_H'] = self.value_time.split(":")[0]
            cfg['value_time_M'] = self.value_time.split(":")[1]
        cfg['is_time'] = self.is_time
        cfg['is_date'] = self.is_date
        cfg['min'] = self.min
        cfg['max'] = self.max
        cfg['client_format'] = self.client_format
        cfg['customClass'] = f" col-lg-{self.size} "
        return cfg

    def compute_data(self, data):
        data = super(datetimeComponent, self).compute_data(data)
        new_dict = self.default_data.copy()
        datek = f"{self.key}-date"
        timek = f"{self.key}-time"
        if self.is_date and self.is_time:
            new_dict[self.key] = self.dte.ui_datetime_to_server_datetime_str(
                f"{data[datek]} {data[timek]}")
            data.pop(datek)
            data.pop(timek)
        elif self.is_date:
            new_dict[self.key] = self.dte.ui_date_to_server_date_str(
                f"{data[datek]}")
            data.pop(datek)
        elif self.is_time:
            new_dict[self.key] = f"{data[timek]}"
            data.pop(timek)
        data = {**data, **new_dict}
        return data.copy()


class dateComponent(CustomComponent):
    pass


class timeComponent(CustomComponent):
    pass


class currencyComponent(CustomComponent):
    pass


class surveyRowComponent(CustomComponent):
    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.headers = []
        self.grid = None
        self.min_row = 1
        self.max_row = 1
        self.row_id = 0
        self.size = 12

    def make_config_new(self, component, id_form, id_submission, disabled=False, cls_size=" col-lg-12 "):
        cfg = super(surveyRowComponent, self).make_config_new(
            component, id_form, id_submission, disabled=disabled, cls_size=cls_size
        )
        cfg['row_id'] = self.row_id
        cfg['customClass'] = f" col-lg-{self.size} "
        return cfg


class surveyComponent(CustomComponent):

    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.headers = []
        self.survey = True
        self.row_id = 0
        self.default_data = {
            self.key: {}
        }
        self.eval_rows()

    def eval_rows(self):
        self.component_items = []
        for row_id in range(len(self.raw['questions'])):
            row = self.get_row(row_id)
            self.component_items.append(row)

    @property
    def rows(self):
        return self.component_items

    def get_row(self, row_id):
        value = ""

        raw_row = OrderedDict()
        raw_row["key"] = f"{self.key}_surveyRow_{row_id}"
        raw_row["type"] = "surveyRow"
        row = self.builder.get_component_object(raw_row)
        row.row_id = row_id
        row.size = 12
        group = self.raw['questions'][row_id]['value']

        raw_info = OrderedDict()
        raw_info['key'] = f"{group}_{row_id}-info"
        raw_info["type"] = "info"
        raw_info["label"] = self.raw['questions'][row_id]['label']
        # raw_info["value"] = self.raw['questions'][row_id]['value']
        info = self.builder.get_component_object(raw_info)
        info.size = 12 - len(self.raw['values'])
        row.component_items.append(info)

        if self.value:
            value = self.value.get(group, "")

        raw_radio = OrderedDict()
        raw_radio['key'] = f"{self.key}_{group}"
        raw_radio["type"] = "radio"
        raw_radio["label"] = ""
        raw_radio["values"] = self.raw['values']
        raw_radio["value"] = value
        raw_radio["inline"] = True
        radio = self.builder.get_component_object(raw_radio)
        radio.size = len(self.raw['values'])
        row.component_items.append(radio)

        return row

    def compute_data(self, data):
        data = super(surveyComponent, self).compute_data(data)
        key = self.key
        list_to_pop = []
        new_dict = self.default_data.copy()
        for k, v in data.items():
            if f"{key}_" in k:
                list_to_pop.append(k)
                groups = k.split("_")
                new_dict[key][groups[1]] = v
        for i in list_to_pop:
            data.pop(i)
        data = {**data, **new_dict}
        return data.copy()


class signatureComponent(CustomComponent):
    pass


# Layout components

class htmlelementComponent(CustomComponent):
    pass


class contentComponent(CustomComponent):
    pass


class columnsComponent(CustomComponent):
    pass


class columnComponent(CustomComponent):
    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.size = self.raw['width']


class fieldsetComponent(CustomComponent):
    pass


class panelComponent(CustomComponent):

    @property
    def title(self):
        CustomComponent = self.builder.components.get(self.key)
        title = CustomComponent.raw.get('title')
        if not title:
            title = CustomComponent.raw.get('label')

        if self.i18n.get(self.language):
            return self.i18n[self.language].get(title, title)
        else:
            return title


class tableComponent(CustomComponent):
    pass


class tabsComponent(CustomComponent):
    pass


# Data components

class datagridRowComponent(CustomComponent):
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


class datagridComponent(CustomComponent):

    def __init__(self, raw, builder, **kwargs):
        super().__init__(raw, builder, **kwargs)
        self.headers = []
        self.multi_row = True
        self.min_row = 1
        self.max_row = 1
        self.add_enabled = True
        self.row_id = 0
        self.default_data = {
            self.key: []
        }
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
            # Copy CustomComponent raw (dict), to ensure no binding and overwrite.
            component_raw = component.raw.copy()
            component_raw['key'] = f"{self.key}_dataGridRow_{row_id}-{component_raw.get('key')}"
            component_obj = self.builder.get_component_object(component_raw)
            if self.value:
                for key, val in self.value[row_id].items():
                    if key.split("-")[1] == component.key:
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
        new_dict = self.default_data.copy()
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

class fileComponent(CustomComponent):

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


class resourceComponent(CustomComponent):

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

    @CustomComponent.value.setter
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
