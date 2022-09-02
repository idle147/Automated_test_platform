import os

import yaml


def change_to_camel(name):
    """
    Change from snake to camel
    :param name:
    :return:
    """
    name_list = name.split("_")
    rv = []
    for n in name_list:
        if n == "":
            continue
        item = n[1:].lower()
        item = n[0].upper() + item
        rv.append(item)

    return "".join(rv)


def format_url_to_snake(url):
    return url.strip('/').replace('/', '_').replace('-', '_').replace('{', '').replace('}', '')


def get_internal_response_schema_name(url, method, code):
    """
    生成假的 schema_name 用以解决内联schema_name没有相应的名称问题
    """
    schema_name = ""
    if url:
        schema_name += f"{format_url_to_snake(url)}_"
    if method:
        schema_name += schema_name + method + "_"
    schema_name += f"response_{code}"
    schema_name = change_to_camel(schema_name)
    return schema_name


def get_internal_request_schema_name(url, method):
    """
     生成假的 schema_name 用以解决内联schema_name没有相应的名称问题
     """
    schema_name = format_url_to_snake(url)
    schema_name += f"_{method}_request"
    schema_name = change_to_camel(schema_name)
    return schema_name


class OpenApiDefineError(Exception):
    pass


class SchemaDataType:
    """
        1. 定义了type_和description
        2. 并通过工厂方法create来生成相对应的具体子类型
    """

    @classmethod
    def type_mapping(cls):
        return {
            "string": StringSchemaDataType,
            "integer": IntSchemaDataType,
            "number": NumberSchemaDataType,
            "boolean": BooleanSchemaDataType,
            "object": ObjectSchemaDataType,
            "reference": ReferenceSchemaDataType,
            "array": ArraySchemaDataType,
            "uuid": StringSchemaDataType
        }

    def __init__(self, *args, **kwargs):
        self.item = None
        self.name = None
        self.data_type = kwargs.get("type_")
        self.type_object = kwargs.get("obj")
        self.description = self.type_object.get("description", "")

    @staticmethod
    def create(type_data):
        if type_data == "":
            return OtherSchemaDataType(type_="other", obj={})
        if ref := type_data.get("$ref", None):
            return ReferenceSchemaDataType(type_="ref", obj=type_data)
        type_str = type_data.get("type", "object")
        if type_str in SchemaDataType.type_mapping():
            return SchemaDataType.type_mapping()[type_str](type_=type_str, obj=type_data)
        else:
            raise OpenApiDefineError(f"{type_str} is not a open API data type")


class StringSchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = self.type_object.get("format")

    @property
    def is_enum(self):
        return self.type_object.get("enum", None) is not None

    @property
    def enum_list(self):
        return self.type_object.get("enum", [])


class IntSchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = self.type_object.get("format")


class NumberSchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = self.type_object.get("format")


class BooleanSchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectSchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required = self.type_object.get("required", [])
        self.properties = {}
        for pname, pdata in self.type_object.get("properties", {}).items():
            self.properties[pname] = SchemaDataType.create(pdata)


class ReferenceSchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref = self.type_object.get("$ref")


class ArraySchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = SchemaDataType.create(self.type_object.get("items"))


class OtherSchemaDataType(SchemaDataType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Schemas:
    """
    存放所有的Schema定义, 以及其具体在YAML文件里面的路径
    """

    def __init__(self, objects, parent):
        self.schema_mapping = {}
        self.parent = parent
        self.parse(objects)

    def parse(self, schema_objects):
        for schema_name, schema_value in schema_objects.items():
            self.schema_mapping[f"/components/schemas/{schema_name}"] = SchemaDataType.create(schema_value)
            self.schema_mapping[f"/components/schemas/{schema_name}"].name = schema_name


class Response:
    def __init__(self, code, response):
        self.ref = None
        self.description = response.get("description", "")
        self.status_code = code
        self.content = None  # 描述response的具体内容(具体格式)
        self.example = None
        if "content" in response:
            if "application/json" in response["content"]:
                self.content = SchemaDataType.create(response["content"]["application/json"]["schema"])
            else:
                self.content = SchemaDataType.create("")
            self.example = response["content"].get("example", None)
        elif "$ref" in response:
            self.ref = response["$ref"]


class Responses:
    def __init__(self, objects, parent):
        self.response_mapping = {}
        self.parent = parent
        for response_key, response_value in objects.items():
            self.response_mapping[f"/components/responses/{response_key}"] = Response(response_key, response_value)


class Parameter:
    def __init__(self, parameter_data):
        self.name = parameter_data.get("name")
        self.in_ = parameter_data.get("in")
        self.required = parameter_data.get("required", True)
        self.description = parameter_data.get("description", "")
        self.content = None
        self.example = None
        if "schema" in parameter_data:
            self.content = SchemaDataType.create(parameter_data.get("schema"))
        elif "content" in parameter_data:
            self.content = SchemaDataType.create(parameter_data["content"]["application/json"]["schema"])
            self.example = parameter_data["content"]["application/json"].get("example", None)
        else:
            raise OpenApiDefineError(f"No schema or content defined in parameter, param Name {self.name}")


class Parameters:
    def __init__(self, objects, parent):
        self.parameter_mapping = {}
        self.parent = parent
        for pkey, pvalue in objects.items():
            self.parameter_mapping[f"/components/parameters/{pkey}"] = Parameter(pvalue)


class RequestBody:
    def __init__(self, request_data):
        self.ref = None
        if "$ref" in request_data:
            self.ref = request_data["$ref"]
        else:
            self.description = request_data.get("description", "")
            self.content = SchemaDataType.create(request_data["content"]["application/json"]["schema"])


class RequestBodies:
    def __init__(self, objects, parent):
        self.body_mapping = {}
        self.parent = parent
        for key, value in objects.items():
            self.body_mapping[f"/components/requestBodies/{key}"] = RequestBody(value)


class ApiMethod:
    """
        代表API的一个方法, 包含paramters、requestBody及response属性
    """

    def __init__(self, method, method_data):
        self.method_data = method_data
        self.method = method
        self.summary = method_data.get("summary", "")
        self.description = method_data.get("description", "")
        self.tags = method_data.get("tags", [])
        self.request_body = None
        self.responses = {}
        self.parameters = [
            Parameter(param) for param in method_data.get("parameters", [])
        ]

        if "requestBody" in method_data:
            self.request_body = RequestBody(method_data["requestBody"])
        for code, response in method_data["responses"].items():
            self.responses[code] = Response(code, response)


class ApiObject:
    def __init__(self, url, api_data):
        self.url = url
        self.api_data = api_data
        self.methods = []
        self.parameters = [
            Parameter(param) for param in api_data.get("parameters", [])
        ]

        methods = ['get', 'post', 'put', 'patch', 'delete']
        for method in methods:
            if method in api_data:
                self.methods.append(ApiMethod(method, api_data[method]))


class SwaggerLoader:
    """
        通过添加load功能来读取YAML文件
    """

    def __init__(self, **kwargs):
        self.main_file = None
        self.yaml_file = {}
        self.api_list = {}
        self.schema_data = {}
        self.response_data = {}
        self.parameter_data = {}
        self.description_data = {}
        self.request_bodies = {}
        self.replace_mapping = kwargs.get("replace_mapping", {})

    def load(self, files, main_file=None):
        if main_file is None or main_file not in files:
            self.main_file = os.path.basename(files[0])
        else:
            self.main_file = os.path.basename(main_file)

        for file in files:
            with open(file) as f:
                file_name = os.path.basename(file)
                swagger_data = yaml.load(f)
                self.yaml_file[file_name] = swagger_data
                self.description_data[file_name] = {}
                self.description_data[file_name]['info'] = swagger_data['info']
                self.description_data[file_name]['servers'] = swagger_data.get("servers", None)

                if "schemas" in swagger_data["components"]:
                    self.schema_data[file_name] = \
                            Schemas(swagger_data["components"]["schemas"], self)
                if "responses" in swagger_data["components"]:
                    self.response_data[file_name] = \
                            Responses(swagger_data["components"]["responses"], self)
                if "parameters" in swagger_data["components"]:
                    self.parameter_data[file_name] = \
                            Parameters(swagger_data["components"]["parameters"], self)
                if "requestBodies" in swagger_data["components"]:
                    self.request_bodies[file_name] = \
                            RequestBodies(swagger_data["components"]["requestBodies"], self)
                if "paths" in swagger_data:
                    # 创建ApiObject对象
                    for url, api_data in swagger_data['paths'].items():
                        self.api_list[url] = ApiObject(url, api_data)
                    # 遍历所创建的API对象中，所有的Object类型的Schema
                    for url, apiobj in self.api_list.items():
                        for method in apiobj.methods:
                            for code, response in method.responses.items():
                                if response.content is not None and \
                                            isinstance(response.content, ObjectSchemaDataType):
                                    # 创建内联Schema
                                    schema_name = get_internal_response_schema_name(url, method.method, code)
                                    self.schema_data[file_name].schema_mapping[f"/components/schemas/{schema_name}"] = \
                                            response.content
                                    self.schema_data[file_name].schema_mapping[
                                        f"/components/schemas/{schema_name}"].name = \
                                            schema_name
                            if method.request_body is not None and \
                                        method.request_body.ref is None and \
                                        isinstance(method.request_body.content, ObjectSchemaDataType):
                                # 创建内联Schema
                                schema_name = get_internal_request_schema_name(url, method.method)
                                self.schema_data[file_name].schema_mapping[f"/components/schemas/{schema_name}"] = \
                                        method.request_body.content
                                self.schema_data[file_name].schema_mapping[f"/components/schemas/{schema_name}"].name = \
                                        schema_name
                # 遍历Responses中所有的内联Schema定义，创建内联Schema
                for yfile, responses in self.response_data.items():
                    for code, response in responses.response_mapping.items():
                        if response.content and isinstance(response.content, ObjectSchemaDataType):
                            schema_name = get_internal_response_schema_name(None, None, str(response.status_code))
                            self.schema_data[yfile].schema_mapping[f"/components/schemas/{schema_name}"] = \
                                    response.content
                            self.schema_data[yfile].schema_mapping[f"/components/schemas/{schema_name}"].name = \
                                    schema_name

        # yfile is the filename, t is the URL name
        # in outbound reference, the reference should be https://xxxx.xxx#/components/schema
        # so we need to put the file name as the HTTP url
        for yfile, target_url in self.replace_mapping.items():
            if yfile in self.schema_data:
                self.schema_data[target_url] = self.schema_data.get(yfile, {})
                self.response_data[target_url] = self.response_data.get(yfile, {})
                self.parameter_data[target_url] = self.parameter_data.get(yfile, {})
                self.request_bodies[target_url] = self.request_bodies.get(yfile, {})
                if yfile in self.schema_data:
                    self.schema_data.pop(yfile)
                if yfile in self.response_data:
                    self.response_data.pop(yfile)
                if yfile in self.parameter_data:
                    self.parameter_data.pop(yfile)
                if yfile in self.request_bodies:
                    self.request_bodies.pop(yfile)

    def get_final_schema(self, schema: SchemaDataType):
        if schema.data_type == "ref":
            ref_path = schema.ref.split("#")
            ref_file_name = ref_path[0] if ref_path[0] != "" else self.main_file
            ref_obj = self.schema_data[ref_file_name].schema_mapping[ref_path[1]]
            return self.get_final_schema(ref_obj)
        if schema.data_type == "array":
            return self.get_final_schema(schema.item)
        return schema

    def get_struct_from_schema(self, schema: SchemaDataType):
        if schema is None:
            return None
        if schema.data_type == "array":
            # if the type is array, generate 1 element
            return [self.get_struct_from_schema(schema.item)]
        if schema.data_type == "ref":
            # if the type is reference, get the reference
            ref_path = schema.ref.split("#")
            ref_file_name = ref_path[0] if ref_path[0] != "" else self.main_file
            ref_obj = self.schema_data[ref_file_name].schema_mapping[ref_path[1]]
            return self.get_struct_from_schema(ref_obj)
        if schema.data_type in ["string", "uuid"]:
            return "test_string"
        if schema.data_type == "boolean":
            return True
        if schema.data_type == "integer":
            return 1
        if schema.data_type == "number":
            return 0.1
        if schema.data_type == "object":
            return {
                name: self.get_struct_from_schema(field)
                for name, field in schema.properties.items()
            }


        return {}

    def get_response_schema(self, response, file=None):
        recent_file = file if file is not None else self.main_file
        if response.content is not None:
            if isinstance(response.content, ReferenceSchemaDataType):
                ref_str = response.content.ref.split("#")
                response_file = recent_file if ref_str[0] == "" else ref_str[0]
                if ref_str[1] in self.response_data[response_file].response_mapping:
                    return self.get_response_schema(
                        self.response_data[response_file].response_mapping[
                            ref_str[1]
                        ],
                        response_file,
                    )

                elif ref_str[1] in self.schema_data[response_file].schema_mapping:
                    return self.get_final_schema(self.schema_data[response_file].schema_mapping[ref_str[1]])
            elif isinstance(response.content, ObjectSchemaDataType):
                schema_name = get_internal_response_schema_name(None, None, str(response.status_code))
                return self.get_final_schema(
                    self.schema_data[recent_file].schema_mapping[f"/components/schemas/{schema_name}"])
        elif response.ref is not None:
            ref_str = response.ref.split("#")
            response_file = recent_file if ref_str[0] == "" else ref_str[0]
            response_data = self.response_data[response_file].response_mapping[ref_str[1]]
            return self.get_response_schema(response_data, response_file)

    def get_request_schema_obj(self, url, method):
        """
        Get the request Body related Schema
        This method walks thru the request body and get the
        corresponding schema object
        """
        if method.request_body is None:
            return None
        if hasattr(method.request_body, "ref") and method.request_body.ref:
            ref_str = method.request_body.ref.split("#")
            file = ref_str[0] if ref_str[0] != "" else self.main_file
            req_body = self.request_bodies[file][ref_str[1]]
        else:
            req_body = method.request_body
        if not isinstance(req_body.content, ObjectSchemaDataType):
            return self.get_final_schema(req_body.content)
        request_schema = get_internal_request_schema_name(url, method.method)
        return self.schema_data[self.main_file].schema_mapping[
            f"/components/schemas/{request_schema}"
        ]

    def get_response_schema_obj(self, url, method, response, code):
        """
        Get the Response Related Schema
        The method will walk thru the response object
        and get the corresponding Schema Object
        """
        if response.content is not None and isinstance(response.content, ObjectSchemaDataType):
            schema_name = get_internal_response_schema_name(url, method.method, code)
            return self.schema_data[self.main_file].schema_mapping[
                f"/components/schemas/{schema_name}"
            ]

        else:
            return self.get_response_schema(response)
