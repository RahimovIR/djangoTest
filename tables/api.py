from django.core.exceptions import ValidationError
from django.utils.cache import patch_cache_control
from django.views.decorators.csrf import csrf_exempt
from tastypie.http import HttpBadRequest, HttpNotFound
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, ApiFieldError
from tastypie.serializers import Serializer
from tables.models import my_models
import json
import re


class MyJSONSerializer(Serializer):

    def __init__(self, fields_type):
        self.fields_type = fields_type
        super().__init__()

    def _validate(self, data):
        for fname in self.fields_type:
            ftype = self.fields_type[fname]
            if ftype == 'int':
                int(data[fname])
            if ftype == 'date':
                if not re.match(r'''^\d{4}-\d{2}-\d{2}$''', data[fname]):
                    raise ValueError('Error date format')
            if ftype == 'char':
                if len(data[fname]) == 0:
                    raise ValueError('field empty')

    def from_json(self, content):
        data = json.loads(content)
        self._validate(data)
        return data


my_resource = []
for model in my_models:
    class Meta:
        queryset = model.objects.all()
        resource_name = model.model_name
        authorization = Authorization()
        always_return_data = True
        serializer = MyJSONSerializer(model.fields_type)

    def build_schema(self):
        base_schema = super(ModelResource, self).build_schema()
        base_schema['fields']['field_order'] = self.order_fields
        base_schema['fields']['fields_verbos_name'] = self.fields_verbos_name
        return base_schema

    def post_detail(self, request, **kwargs):
        """
        Return 404 when url like /api/tables/users2//
        """
        return HttpNotFound()

    def wrap_view(self, view):
        """
        Wraps views to return custom error codes instead of generic 500's
        """
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                return response
            except (BadRequest, ApiFieldError) as e:
                return HttpBadRequest(e.args[0])
            except ValidationError as e:
                return HttpBadRequest(', '.join(e.messages))
            except ValueError as e:
                return HttpBadRequest(e)
            except Exception as e:
                return self._handle_500(request, e)

        return wrapper

    my_attributes = {'Meta': Meta, 'build_schema': build_schema, 'wrap_view': wrap_view, 'post_detail': post_detail,
        'order_fields': model.order_fields, 'fields_verbos_name': model.fields_verbos_name}
    my_resource.append(type(model.model_name + 'Resource', (ModelResource,), my_attributes))