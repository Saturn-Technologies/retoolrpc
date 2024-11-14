import asyncio

import typer

from retoolrpc.legacy.rpc import RetoolRPC as LegacyRPC
from retoolrpc.server import RetoolRPC
from retoolrpc.legacy.utils.types import RetoolRPCConfig
from retoolrpc.util.imports import resolve_import_string

app = typer.Typer()


@app.command()
def run(application_path: str, host: str) -> None:
    application: RetoolRPC = resolve_import_string(application_path)
    assert isinstance(
        application, RetoolRPC
    ), "Application must be a RetoolRPC instance"

    # Build host:port string add http:// if not present
    host = f"https://{host}" if not host.startswith("http") else host

    rpc_config = RetoolRPCConfig(
        api_token=application.api_key,
        host=host,
        resource_id=application.resource_id,
        environment_name=application.environment,
        polling_interval_ms=application.polling_interval_ms,
        version=application.version,
        log_level=application.log_level,
    )
    rpc = LegacyRPC(rpc_config)

    for function in application.functions:
        rpc.register(function)
    asyncio.run(rpc.listen())
