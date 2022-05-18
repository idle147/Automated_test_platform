"""
    实现代码文档元素
"""
from abc import abstractmethod, ABCMeta


class CodeDomError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ExpressionBase(metaclass=ABCMeta):
    """
        表达式基类
    """

    def __init__(self):
        pass

    @abstractmethod
    def to_code(self):
        """
        输出表达式所代表的代码
        """
        pass


class VariableInvokeExpression(ExpressionBase):
    """
        变量引用表达式
    """

    def __init__(self, var_name):
        super().__init__()
        self.var_name = var_name  # 变量名

    def to_code(self):
        """
            直接返回变量名的字符串
        """
        return self.var_name


class ConstInvokeExpression(ExpressionBase):
    """
        常量引用表达式
    """

    def __init__(self, const_value):
        super().__init__()
        self.const_value = const_value  # 常量名

    def to_code(self):
        if isinstance(self.const_value, int) or isinstance(self.const_value, float):
            return str(self.const_value)
        elif self.const_value is None:
            return "None"
        else:
            return f"\"{self.const_value}\""  # 如果是字符串常量,则需要添加引号


class NoneExpression(ConstInvokeExpression):
    """
    None Expression
    """

    def __init__(self):
        super().__init__(None)


class TrueExpression(ConstInvokeExpression):
    """
    True Expression
    """

    def __init__(self):
        super().__init__(True)


class FalseExpression(ConstInvokeExpression):
    """
    False Expression
    """

    def __init__(self):
        super().__init__(False)


class AssignExpression(ExpressionBase):
    """
    赋值表达式
    """

    def __init__(self, left_expression, right_expression):
        """
            赋值前,对输入参数进行检查
        """
        super().__init__()
        if not isinstance(left_expression, ExpressionBase):
            raise CodeDomError("left expression should be an expression instance")
        if not isinstance(right_expression, ExpressionBase):
            raise CodeDomError("right expression should be an expression instance")
        self.left_expression = left_expression
        self.right_expression = right_expression

    def to_code(self):
        return f"{self.left_expression.to_code()} = {self.right_expression.to_code()}"


class FieldInvokeExpression(ExpressionBase):
    """
    Object/Instance Field Invoke Expression
    封装了对象/实例的字段/属性的引用,
    """

    def __init__(self, instance_expression, field_expression):
        super().__init__()
        if not isinstance(instance_expression, ExpressionBase):
            raise CodeDomError("Instance name should be an expression")
        if not isinstance(field_expression, ExpressionBase):
            raise CodeDomError("Field should be an expression")
        self.instance_expression = instance_expression
        self.field_expression = field_expression

    def to_code(self):
        return f"{self.instance_expression.to_code()}.{self.field_expression.to_code()}"


class MethodInvokeExpression(ExpressionBase):
    """
    Method invoke Expression
    表示方法的调用,每个参数均为表达式类型
    """

    def __init__(self, method_name, *args, **kwargs):
        super().__init__()
        for arg in args:
            if not isinstance(arg, ExpressionBase):
                raise CodeDomError("Argument should be expression")
        self.method_name = method_name
        self.arg_list = list()
        for arg in args:
            self.arg_list.append(arg)
        self.obj = kwargs.get("instance", None)

    def to_code(self):
        if self.obj:
            return f"{self.obj.to_code()}.{self.method_name}({', '.join([x.to_code() for x in self.arg_list])})"
        else:
            return f"{self.method_name}({', '.join([x.to_code() for x in self.arg_list])})"


class InstanceCreationExpression(ExpressionBase):
    """
    创建实例表达式
    """

    def __init__(self, class_name, *args):
        super().__init__()
        for arg in args:
            if not isinstance(arg, ExpressionBase):
                raise CodeDomError("Argument should be expression")
        self.class_name = class_name
        self.arg_list = args

    def to_code(self):
        return f"{self.class_name}({', '.join([x.to_code() for x in self.arg_list])})"


class DictInvokeExpression(ExpressionBase):
    """
    获取字典信息表达式
    """

    def __init__(self, dict_name, key_expression):
        super().__init__()
        self.dict_name = dict_name
        self.key_name = key_expression

    def to_code(self):
        if not isinstance(self.key_name, ExpressionBase):
            raise CodeDomError("key should be an expression")
        return f"{self.dict_name}[{self.key_name.to_code()}]"


class ParameterDefineExpression(ExpressionBase):
    """
        参数定义表达式
    """

    def __init__(self, name, default_value=None):
        super().__init__()
        self.name = name
        self.default_value = default_value
        if default_value is not None and not isinstance(default_value, ExpressionBase):
            raise CodeDomError("Parameter default value should be an expression")

    def to_code(self):
        ret = self.name
        if self.default_value is not None:
            return f"{ret}={self.default_value.to_code()}"
        else:
            return ret


class BinaryOperatorExpression(ExpressionBase):
    """
        二进制操作表达式
    """

    def __init__(self, op_expression1, op_expression2, operator):
        super().__init__()
        if not isinstance(op_expression1, ExpressionBase):
            raise CodeDomError("expression1 should be an expression")
        if not isinstance(op_expression2, ExpressionBase):
            raise CodeDomError("expression2 should be an expression")
        self.expression1 = op_expression1
        self.expression2 = op_expression2
        self.operator = operator

    def to_code(self):
        return f"{self.expression1.to_code()} {self.operator} {self.expression2.to_code()}"


class ListExpression(ExpressionBase):
    """
        list表达式
    """

    def __init__(self, expression_list):
        super().__init__()
        self.expression_list = expression_list

    def to_code(self):
        rv_list = ", ".join([exp.to_code() for exp in self.expression_list])
        return f"[{rv_list}]"


class SelfExpression(ExpressionBase):
    """
    self表达
    """

    def to_code(self):
        return "self"


def _get_indent(indent):
    """
        python中需要通过控制缩进,以输出正确的代码格式
    """
    return "    " * indent


class StatementBase(metaclass=ABCMeta):
    """
    语句基类
        语句 == 一组表达式 or 子语句
    """

    def to_code(self, indent=0):
        """
            将_to_code的返回值加上换行符后返回
            indent: 表示所需要的缩进级数
        """
        return self._to_code(indent) + "\n"

    @abstractmethod
    def _to_code(self, indent=0):
        pass


class ExpressionStatement(StatementBase):
    """
        表达式语句
    """

    def __init__(self, expression):
        if not isinstance(expression, ExpressionBase):
            raise CodeDomError("expression should be an expression")
        self.expression = expression

    def _to_code(self, indent=0):
        return f"{_get_indent(indent)}{self.expression.to_code()}"


class BlankStatement(StatementBase):

    def _to_code(self, indent=0):
        return ""


class ImportStatement(StatementBase):
    """
        包引用语句
    """

    def __init__(self, packages: list, from_package=None, _as=None):
        self.packages = packages
        self.from_package = from_package
        self.as_ = _as

    def _to_code(self, indent=0):
        ret = f"import {', '.join(self.packages)}"
        if self.from_package:
            ret = f"from {self.from_package} {ret}"
        if self.as_ is not None:
            ret += f" as {self.as_}"
        return f"{_get_indent(indent)}{ret}"


class ReturnStatement(StatementBase):
    """
        返回语句
    """

    def __init__(self, expression):
        if not isinstance(expression, ExpressionBase):
            raise CodeDomError("Return expression should be an expression")
        self.expression = expression

    def _to_code(self, indent=0):
        return f"{_get_indent(indent)}return {self.expression.to_code()}"


class MethodDefineStatement(StatementBase):
    """
        方法定义语句
    """

    def __init__(self, method_name, *args):
        self.method_name = method_name
        self.decorators = list()
        self.args = list()
        self.doc = None
        for arg in args:
            self.args.append(arg)
        self.body = list()

    def _to_code(self, indent=0):
        ret = ""
        for decorator in self.decorators:
            ret += f"{_get_indent(indent)}@{decorator.to_code()}\n"
        ret += f"{_get_indent(indent)}def {self.method_name}({', '.join([x.to_code() for x in self.args])}):\n"
        if self.doc is not None:
            ret += self.doc.to_code(indent + 1)
        for segment in self.body:
            ret += segment.to_code(indent + 1)
        return ret


class ClassDefineStatement(StatementBase):
    """
        类定义语句
    """

    def __init__(self, class_name, parent=None, doc=None):
        self.class_name = class_name
        self.parent = parent
        self.decorators = list()
        self.body = list()
        self.doc = doc

    def _to_code(self, indent=0):
        ret = ""
        for decorator in self.decorators:
            ret += f"{_get_indent(indent)}@{decorator.to_code()}\n"
        ret += f"{_get_indent(indent)}class {self.class_name}"
        if self.parent is not None:
            ret += f"({self.parent})"
        ret += f":\n"
        if self.doc is not None:
            ret += self.doc.to_code(indent + 1)
        for segment in self.body:
            ret += segment.to_code(indent + 1)
        return ret


class DocStatement(StatementBase):
    """
     doc语句
    """

    def __init__(self, lines):
        self.lines = lines

    def _to_code(self, indent=0):
        rv = f"{_get_indent(indent)}\"\"\"" + "\n"
        for line in self.lines:
            rv += f"{_get_indent(indent)}{line}\n"
        rv += f"{_get_indent(indent)}\"\"\""
        return rv


class IfStatement(StatementBase):

    def __init__(self, condition):
        self.condition = condition
        self.true_statements = list()
        self.false_statements = list()

    def _to_code(self, indent=0):
        rv = f"{_get_indent(indent)}if {self.condition.to_code()}:\n"
        for statement in self.true_statements:
            rv += statement.to_code(indent + 1)
        rv += f"{_get_indent(indent)}else:\n"
        for statement in self.false_statements:
            rv += statement.to_code(indent + 1)
        return rv


class PassStatement(StatementBase):

    def _to_code(self, indent=0):
        return f"{_get_indent(indent)}pass"


if __name__ == "__main__":
    mh = MethodDefineStatement("add")
    mh.decorators.append(VariableInvokeExpression("check"))
    mh.args.append(ParameterDefineExpression("a"))
    mh.args.append(ParameterDefineExpression("b"))
    mh.body.append(
        ExpressionStatement(
            AssignExpression(
                VariableInvokeExpression("ret"),
                BinaryOperatorExpression(
                    VariableInvokeExpression("a"),
                    VariableInvokeExpression("b"),
                    "+"))))
    mh.body.append(
        ReturnStatement(
            VariableInvokeExpression("ret")
        )
    )
    print(mh.to_code())
