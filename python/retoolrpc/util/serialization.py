from typing import Any, Generator, Iterable, Union

import orjson
from pydantic import BaseModel


def safe_dict(
    data: Union[dict, BaseModel, Iterable[BaseModel]],
    *args: Any,
    as_bytes: bool = False,
    **kwargs: Any,
) -> dict | bytes:
    """Convert a dictionary to json-safe values.

    Any extra-args or kwargs passed to this function will be passed
    to the dict() function from pydantic.

    :param data: the data to be converted. A pydantic model can also be used.
    :type data: Union[dict, BaseModel, Iterable[BaseModel]]
    :param args: args to be passed to the pydantic dict() if `data` is pydantic
    :type args: Any
    :param as_bytes: if should return the serialized as bytes.
    :param kwargs: kwargs to be passed to the pydantic dict() if `data` is pydantic
    :type kwargs: Any
    :return: a json-safe dictionary
    :rtype: dict
    """

    if isinstance(data, Generator):
        data = list(data)
    if isinstance(data, BaseModel):
        data = data.dict(*args, **kwargs)

    data = orjson.dumps(
        data,
        default=BaseModel.__json_encoder__,
        option=orjson.OPT_NON_STR_KEYS
        | orjson.OPT_PASSTHROUGH_DATETIME
        | orjson.OPT_NAIVE_UTC,
    )
    if as_bytes:
        return data
    return orjson.loads(data)  # noqa
