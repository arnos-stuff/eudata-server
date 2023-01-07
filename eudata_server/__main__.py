import os
import sys
import json
import rich
import typer
import uvicorn

from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
 
from eudata_server.tools.paths import package_dir

cli = typer.Typer(help="Run the server", add_completion=True, no_args_is_help=True)

console = Console()

cfg_fname = package_dir / "config.json"

if cfg_fname.exists():
    config = json.load(open(cfg_fname, "r"))
else:
    config = {}

@cli.command(name="dev", help="Run the server in development mode")
def dev(workers: int = typer.Option(4, help="Number of workers")):
    """Run the server in development mode"""
    uvicorn.run("eudata_server.api:app", reload=True)

@cli.command(name="prod", help="Run the server in production mode withouth SSL")
def prod(
    port: Optional[int] = typer.Option(8080, help="Port number"),
    host: Optional[str] = typer.Option("0.0.0.0", help="Host address"),
    workers: int = typer.Option(4, help="Number of workers"),
    ):
    """Run the server in production mode without SSL"""
    if len(config):
        port = config["server"]["port"]
        host = config["server"]["host"]

    uvicorn.run(
        "eudata_server.api:app",
        workers=workers,
        host=host,
        port=port,
        log_level="debug",
        reload=False,
        )

def ssl_core(
    host: Optional[str],
    port: Optional[int],
    keyfile: Optional[str],
    certfile: Optional[str],
    workers: Optional[int],
    ):
    """Core function for ssl commands"""
    if len(config):
        port = config["server"]["port"]
        host = config["server"]["host"]
        keyfile = config["ssl"]["key"]
        certfile = config["ssl"]["cert"]

        console.print(f"[dim magenta]Default keyfile: [/][yellow]{config['ssl']['key']}[/]")
        console.print(f"[dim magenta]Default keyfile: [/][yellow]{config['ssl']['cert']}[/]")
        
    else:
        ok = Confirm.ask(f"[bold magenta] Use default credentials ?[/]")
        if not ok:
            keyfile = Prompt.ask("[bold magenta] Enter [yellow]SSL key[/] file path[/]", default=config["ssl"]["key"])
            certfile = Prompt.ask("[bold magenta] Enter [yellow]SSL cert[/] file path[/]", default=config["ssl"]["cert"])
            save = Confirm.ask("[bold yellow] Save config?[/]")
        
            if save:
                config["server"] = {"port": port}
                config["server"]["host"] = host
                config["ssl"] = {"key": keyfile}
                config["ssl"]["cert"] = certfile
                json.dump(config, open(package_dir / "config.json", "w"), indent=4)

    console.print(f"🚀🚀 [bold red]Starting server[/] [magenta]with {workers} workers[/]")

    # run the main app
    uvicorn.run(
        "eudata_server.api:app",
        workers=workers,
        host=host,
        port=port,
        log_level="info",
        ssl_keyfile=keyfile,
        ssl_certfile=certfile,
        )

@cli.command(name="sslprod", help="Run the server in production mode with SSL")
def sslprod(
    port: Optional[int] = typer.Option(8080, help="Port number"),
    host: Optional[str] = typer.Option("0.0.0.0", help="Host address"),
    keyfile: Optional[str] = typer.Option(None, help="SSL key file path"),
    certfile: Optional[str] = typer.Option(None, help="SSL cert file path"),
    workers: int = typer.Option(4, help="Number of workers")
    ) -> None:
    """Run the server in production mode with SSL.
    
    If no keyfile or certfile is provided, the default ones will be used.
    An interactive prompt will ask for confirmation.
    
    This also runs a redirect server http -> https in the background."""
    ssl_core(host, port, keyfile, certfile, workers)

@cli.command(name="ssl", help="Alias for `sslprod`")
def ssl(
    keyfile: Optional[str] = typer.Option(None, help="SSL key file path"),
    certfile: Optional[str] = typer.Option(None, help="SSL cert file path"),
    workers: int = typer.Option(4, help="Number of workers")
    ) -> None:
    """Run the server in production mode with SSL. 
    
    If no keyfile or certfile is provided, the default ones will be used.
    An interactive prompt will ask for confirmation.
    
    This also runs a redirect server http -> https in the background."""
    ssl_core(keyfile, certfile, workers)


if __name__ == "__main__":
    cli()