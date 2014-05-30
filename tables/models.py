from django.db import models
from django.conf import settings
import sys
import yaml
import datetime


def choice_field(field_type, title):
    if field_type == 'char':
        return models.CharField(max_length=50, verbose_name=title, default='')
    if field_type == 'int':
        return models.IntegerField(verbose_name=title, default=0)
    if field_type == 'date':
        return models.DateField(verbose_name=title, default=datetime.date.today())


def generate_models(ya):
    if ya is None:
        return
    for table_name, table in ya.items():
        class Meta:
            verbose_name = table['title']
            verbose_name_plural = table['title']

        my_attributes = {}
        my_attributes['verbose_name'] = table['title']
        my_attributes['model_name'] = table_name
        my_attributes['Meta'] = Meta
        my_attributes['__module__'] = __name__
        order_fields = {}
        fields_verbos_name = {}
        i = 0
        for field in table['fields']:
            field_id, field_type, title = field['id'], field['type'], field['title']
            my_attributes[field_id] = choice_field(field_type, title)
            fields_verbos_name[field_id] = title
            order_fields[i] = field_id
            i += 1
        my_attributes['order_fields'] = order_fields
        my_attributes['fields_verbos_name'] = fields_verbos_name
        my_models.append(type(table_name, (models.Model,), my_attributes))

my_models = []
ya = None

if not('test' in sys.argv):
    try:
        with open(settings.MODEL_FILENAME, 'r', encoding='utf-8') as yaml_file:
            ya = yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print('Yaml file not found')
else:
    # for test
    ya = yaml.safe_load('''
        users:
            title: Пользователи
            fields:
                - {id: name, title: Имя, type: char}
                - {id: paycheck, title: Зарплата, type: int}
                - {id: date_joined, title: Дата поступления на работу, type: date}

        rooms:
            title: Комнаты
            fields:
                - {id: spots, title: Вместимость, type: int}
                - {id: department, title: Отдел, type: char}

    ''')

generate_models(ya)
