"""Airdrop invocation entrypoint."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from airdrop import __app_name__, cli

def main():
    cli.init_cli(prog_name=__app_name__)

if __name__ == "__main__":
    main()
