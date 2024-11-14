from importlib import import_module
from typing import Any


def resolve_import_string(import_string: str) -> Any:
    try:
        if ":" not in import_string:
            return import_module(import_string)

        module_path, func_name = import_string.rsplit(":", 1)
        module = import_module(module_path)

        if not hasattr(module, func_name):
            raise AttributeError(
                f"Module '{module_path}' has no attribute '{func_name}'"
            )

        return getattr(module, func_name)
    except ImportError as e:
        raise ImportError(f"Could not import '{import_string}'. Error: {str(e)}")
    except ValueError:
        raise ValueError(f"Invalid import string format: '{import_string}'")
