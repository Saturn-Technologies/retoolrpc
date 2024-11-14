import typing

Function_T = typing.TypeVar("Function_T", bound=typing.Callable)
RETOOL_LOG_LEVELS = typing.Literal["debug", "info"]
RetoolArgumentTypes = typing.Literal["string", "number", "boolean", "dict", "json"]
InvalidModelAttributes = ("v__duplicate_kwargs", "args", "kwargs")


class RetoolArgument(typing.TypedDict):
    type: RetoolArgumentTypes
    description: str | None
    required: bool
    array: bool


class RetoolFunction(typing.TypedDict):
    name: str
    arguments: dict[str, RetoolArgument]
    implementation: typing.Callable[
        [dict, dict], typing.Coroutine[typing.Any, typing.Any, typing.Any]
    ]
    permissions: list | None
