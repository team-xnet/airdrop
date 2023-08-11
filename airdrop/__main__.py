"""Airdrop invocation entrypoint.                      """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from typer import run

from airdrop.cli import cli
from airdrop     import __app_name__

if __name__ == "__main__":
    cli(prog_name=__app_name__)
