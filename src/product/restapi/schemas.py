"""

    This file is auto generated by the case auto generator
    Swagger File: product.yaml
    Description: The Object Report for the API Definition
    API Doc Version: 1.0.0
    Date: 2021-02-03 20:00:10,

"""
from product.restapi.common.schemabase import SchemaBase, response_schema
class ProductAddInfo(SchemaBase):
    """
    the new added product info
    """
    _all_fields = ["name", "price", "catagory"]
    required_fields = ["name", "price", "catagory"]

    def __init__(self, raw_json=None):
        self._object_fields = {}
        self._name = None
        self._price = None
        self._catagory = None
        super().__init__(raw_json)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def catagory(self):
        return self._catagory

    @catagory.setter
    def catagory(self, value):
        self._catagory = value


class ProductInfo(SchemaBase):
    """
    the product information
    """
    _all_fields = ["id", "name", "price", "catagory"]
    required_fields = ["id", "name", "price", "catagory"]

    def __init__(self, raw_json=None):
        self._object_fields = {}
        self._id = None
        self._name = None
        self._price = None
        self._catagory = None
        super().__init__(raw_json)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def catagory(self):
        return self._catagory

    @catagory.setter
    def catagory(self, value):
        self._catagory = value


class ProductInfoList(SchemaBase):
    """
    The product list
    """
    _all_fields = ["products"]
    required_fields = ["products"]

    def __init__(self, raw_json=None):
        self._object_fields = {}
        self._products = []
        super().__init__(raw_json)

    @property
    def products(self):
        return self._products

    @products.setter
    def products(self, value):
        self._products = value


class ErrorResponse(SchemaBase):
    """
    The error response
    """
    _all_fields = ["message"]
    required_fields = ["message"]

    def __init__(self, raw_json=None):
        self._object_fields = {}
        self._message = None
        super().__init__(raw_json)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value


class ProductProductPostResponse201(SchemaBase):
    """
    the added product id
    """
    _all_fields = ["id"]
    required_fields = ["id"]

    def __init__(self, raw_json=None):
        self._object_fields = {}
        self._id = None
        super().__init__(raw_json)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value


