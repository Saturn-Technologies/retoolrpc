import inspect
import typing
from asyncio import to_thread

import pydantic
from pydantic import validate_arguments

from retoolrpc.types import (
    RetoolArgument,
    RetoolFunction,
    Function_T,
    RETOOL_LOG_LEVELS,
    RetoolArgumentTypes,
    InvalidModelAttributes,
)
from retoolrpc.util.serialization import safe_dict


class RetoolRPC:
    functions: list[RetoolFunction]

    def __init__(
        self,
        *,
        api_key: str,
        resource_id: str,
        environment: str,
        version: str,
        polling_interval_ms: int = 1000,
        log_level: RETOOL_LOG_LEVELS = "info",
    ) -> None:
        self.api_key = api_key
        self.resource_id = resource_id
        self.environment = environment
        self.version = version
        self.polling_interval_ms = polling_interval_ms
        self.log_level = log_level
        self.functions = []

    def pre_start(self):
        pass

    @classmethod
    def _resolve_type(cls, object: dict) -> RetoolArgumentTypes:
        # Item is an array, resolve the inner type of the array
        if object.get("type") == "array":
            return cls._resolve_type(object.get("items"))
        # Item has a type, resolve it
        if object_type := object.get("type"):
            if object_type == "integer":
                return "number"
            allowed_values = typing.get_args(RetoolArgumentTypes)
            if object_type in allowed_values:
                return object_type
        # Items is a reference to another type, assume it's a dict
        elif object.get("$ref"):
            return "dict"
        raise ValueError(f"Invalid type for {object}")

    @staticmethod
    def _resolve_description(item: dict, schema: dict) -> str:
        if description := item.get("description"):
            return description
        elif ref := item.get("$ref"):
            return (
                schema.get("definitions", {})
                .get(ref.split("/")[-1])
                .get("description", "")
            )
        return item.get("title", "")

    def _generate_retool_args(self, function: Function_T) -> dict[str, RetoolArgument]:
        model: pydantic.BaseModel | None = getattr(function, "model", None)
        assert model is not None, "Function must have a Typing Model embedded on it"
        json_schema = model.schema()
        required_items = json_schema.get("required", [])
        retool_args: dict[str, RetoolArgument] = {}

        for key, item in json_schema.get("properties").items():
            if key in InvalidModelAttributes:
                continue
            retool_args[key] = RetoolArgument(
                description=self._resolve_description(item, json_schema),
                required=key in required_items,
                type=self._resolve_type(item),
                array=item.get("type") == "array",
            )
        return retool_args

    def task(self, function: Function_T) -> Function_T:
        impl = validate_arguments(function)
        is_async = inspect.iscoroutinefunction(function)

        async def _wrapper(arguments: dict, context: dict) -> typing.Any:
            # TODO: Add context to the function
            if is_async:
                response = await impl(**arguments)
            else:
                response = await to_thread(impl, **arguments)
            return safe_dict({"data": response})

        function_def = RetoolFunction(
            name=function.__qualname__,
            arguments=self._generate_retool_args(impl),
            implementation=_wrapper,
            permissions=None,
        )
        self.functions.append(function_def)
        return impl
