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

config = json.load(open(package_dir / "config.json", "r"))

@cli.command(name="dev", help="Run the server in development mode")
def dev(workers: int = typer.Option(4, help="Number of workers")):
    """Run the server in development mode"""
    uvicorn.run("eudata_server.api:app", reload=True)

@cli.command(name="prod", help="Run the server in production mode withouth SSL")
def prod(workers: int = typer.Option(4, help="Number of workers")):
    """Run the server in production mode without SSL"""
    uvicorn.run(
        "eudata_server.api:app",
        workers=workers,
        host=config["server"]["host"],
        port=config["server"]["port"],
        log_level="info",
        reload=False,
        )

def ssl_core(
    keyfile: Optional[str],
    certfile: Optional[str],
    workers: Optional[int],
    ):
    """Core function for ssl commands"""
    if keyfile is None:
        keyfile = config["ssl"]["key"]
    if certfile is None:
        certfile = config["ssl"]["cert"]

    console.print(f"[dim magenta]Default keyfile: [/][yellow]{config['ssl']['key']}[/]")
    console.print(f"[dim magenta]Default keyfile: [/][yellow]{config['ssl']['cert']}[/]")
    
    ok = Confirm.ask(f"[bold magenta] Use default credentials ?[/]")

    if not ok:
        keyfile = Prompt.ask("[bold magenta] Enter [yellow]SSL key[/] file path[/]", default=config["ssl"]["key"])
        certfile = Prompt.ask("[bold magenta] Enter [yellow]SSL cert[/] file path[/]", default=config["ssl"]["cert"])
        save = Confirm.ask("[bold yellow] Save config?[/]")
    
        if save:
            config["ssl"]["key"] = keyfile
            config["ssl"]["cert"] = certfile
            json.dump(config, open(package_dir / "config.json", "w"), indent=4)

    console.print(f"🚀🚀 [bold red]Starting server[/] [magenta]with {workers} workers[/]")

    # run the main app
    uvicorn.run(
        "eudata_server.api:app",
        workers=workers,
        host=config["server"]["host"],
        port=config["server"]["port"],
        log_level="info",
        ssl_keyfile=keyfile,
        ssl_certfile=certfile,
        )

@cli.command(name="sslprod", help="Run the server in production mode with SSL")
def sslprod(
    keyfile: Optional[str] = typer.Option(None, help="SSL key file path"),
    certfile: Optional[str] = typer.Option(None, help="SSL cert file path"),
    workers: int = typer.Option(4, help="Number of workers")
    ) -> None:
    """Run the server in production mode with SSL.
    
    If no keyfile or certfile is provided, the default ones will be used.
    An interactive prompt will ask for confirmation.
    
    This also runs a redirect server http -> https in the background."""
    ssl_core(keyfile, certfile, workers)

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
    develop()