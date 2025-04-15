import enum

from pydantic import validate_arguments
from pydantic.main import BaseModel

from retoolrpc import RetoolRPC


class User(BaseModel):
    user_id: str
    name: str
    email: str | None

class MyEnum(enum.StrEnum):
    A = "A"
    B = "B"

class NumberedEnum(enum.IntEnum):
    A = 1
    B = 2

class AnonymousEnum(enum.Enum):
    A = 1
    B = 2

class TestTypes:

    def test_pydantic_model_list(self):
        def my_method(calling_user: User, users: list[User]):
            pass
        resolved = RetoolRPC._generate_retool_args(validate_arguments(my_method))
        assert resolved['calling_user']['array'] is False
        assert resolved['users']['array'] is True

        assert resolved['calling_user']['type'] == 'dict'
        assert resolved['users']['type'] == 'dict'

    def test_dict_complex(self):
        def my_method(common: dict, complex_dict: dict[str, str]):
            pass
        resolved = RetoolRPC._generate_retool_args(validate_arguments(my_method))
        assert resolved['common']['type'] == 'dict'
        assert resolved['complex_dict']['type'] == 'dict'

    def test_dict_pydantic(self):
        def my_method(users: dict[str, User]):
            pass
        resolved = RetoolRPC._generate_retool_args(validate_arguments(my_method))
        assert resolved['users']['type'] == 'dict'

    def test_enum(self):
        def my_method(my_enum: MyEnum, my_enum_list: list[MyEnum], dict_enum: dict[str, MyEnum], dict_enum_key: dict[MyEnum, str]):
            pass
        resolved = RetoolRPC._generate_retool_args(validate_arguments(my_method))

        assert resolved['my_enum']['type'] == 'string'
        assert resolved['my_enum_list']['type'] == 'string'
        assert resolved['my_enum_list']['array'] is True
        assert resolved['dict_enum']['type'] == 'dict'
        assert resolved['dict_enum_key']['type'] == 'dict'

    def test_numbered_enum(self):
        def my_method(my_enum: NumberedEnum, my_enum_list: list[NumberedEnum]):
            pass
        resolved = RetoolRPC._generate_retool_args(validate_arguments(my_method))

        assert resolved['my_enum']['type'] == 'number'
        assert resolved['my_enum_list']['type'] == 'number'
        assert resolved['my_enum_list']['array'] is True

    def test_anonymous_enum(self):
        def my_method(my_enum: AnonymousEnum, my_enum_list: list[AnonymousEnum], my_enum_dict: dict[str, AnonymousEnum]):
            pass
        resolved = RetoolRPC._generate_retool_args(validate_arguments(my_method))
        # Anonymous enums are not supported, so we fall back to string
        assert resolved['my_enum']['type'] == 'string'
        assert resolved['my_enum_list']['type'] == 'string'
        assert resolved['my_enum_list']['array'] is True
        assert resolved['my_enum_dict']['type'] == 'dict'
