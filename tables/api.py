from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from tastypie.http import HttpBadRequest
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse, BadRequest, ApiFieldError
from tastypie import http
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

    def deserialize(self, request, data, format='application/json'):
        print("start deserialize")
        # try:
        return super(ModelResource, self).deserialize(request, data, format=format)
        # except Exception as e:
            # if an exception occurred here it must be due to deserialization
            # raise ImmediateHttpResponse(response=http.HttpBadRequest(e.message))

    def post_list(self, request, **kwargs):
        print("start post_list")
        # try:
        return super(ModelResource, self).post_list(request, **kwargs)
        # except Exception as e:
        #     # if an exception occurred here it must be due to deserialization
        #     return HttpBadRequest({'code': 400, 'message':', '.join(e.messages)})


    def wrap_view(self, view):
        """
        Wraps views to return custom error codes instead of generic 500's
        """
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                print("start wrap_view")
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                # if request.is_ajax():
                #     patch_cache_control(response, no_cache=True)

                # response is a HttpResponse object, so follow Django's instructions
                # to change it to your needs before you return it.
                # https://docs.djangoproject.com/en/dev/ref/request-response/
                return response
            except (BadRequest, ApiFieldError) as e:
                return HttpBadRequest(e.args[0])
            except ValidationError as e:
                # Or do some JSON wrapping around the standard 500
                return HttpBadRequest(', '.join(e.messages))
            except ValueError as e:
                return HttpBadRequest(e)
            except Exception as e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                # raise
                return self._handle_500(request, e)

        return wrapper

    my_attributes = {'Meta': Meta, 'build_schema': build_schema, 'deserialize': deserialize,
        'wrap_view': wrap_view,  'post_list': post_list,
        'order_fields': model.order_fields, 'fields_verbos_name': model.fields_verbos_name}
    my_resource.append(type(model.model_name + 'Resource', (ModelResource,), my_attributes))