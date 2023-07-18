"""Airdrop invocation entrypoint."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from typer import run

from airdrop.cli import main

if __name__ == "__main__":
    run(main)
