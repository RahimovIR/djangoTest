from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tables.models import my_models

my_resource = []
for model in my_models:
    class Meta:
        queryset = model.objects.all()
        resource_name = model.model_name
        authorization = Authorization()
        always_return_data = True

    def build_schema(self):
        base_schema = super(ModelResource, self).build_schema()
        base_schema['fields']['field_order'] = self.order_fields
        base_schema['fields']['fields_verbos_name'] = self.fields_verbos_name
        return base_schema

    my_attributes = {'Meta': Meta, 'build_schema': build_schema,
                     'order_fields': model.order_fields, 'fields_verbos_name': model.fields_verbos_name}
    my_resource.append(type(model.model_name + 'Resource', (ModelResource,), my_attributes))