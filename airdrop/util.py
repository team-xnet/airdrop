"""Small utility functions.                            """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.layout import Layout
from rich.align  import Align
from rich.panel  import Panel
from rich.text   import Text

from airdrop import i18n

def get_layout_with_renderable(renderable) -> Layout:

    rendered_banner = Text.assemble(
        ("__   ___   _ ______ _______            _         _                 \n", "#902EF4"),
        ("\ \ / / \ | |  ____|__   __|     /\   (_)       | |                \n", "#1B6AFF"),
        (" \ V /|  \| | |__     | |       /  \   _ _ __ __| |_ __ ___  _ __  \n", "#008EFF"),
        ("  > < | . ` |  __|    | |      / /\ \ | | '__/ _` | '__/ _ \| '_ \ \n", "#00AAFF"),
        (" / . \| |\  | |____   | |     / ____ \| | | | (_| | | | (_) | |_) |\n", "#00ACFF"),
        ("/_/ \_\_| \_|______|  |_|    /_/    \_\_|_|  \__,_|_|  \___/| .__/ \n", "#00D5FF"),
        ("                                                            | |    \n", "#00E7FD"),
        ("                                                            |_|    \n", "#57F6F0"),

        overflow="crop",
        no_wrap=True
    )

    layout = Layout()

    layout.split_column(
        Layout(Align(Panel(rendered_banner, expand=False, subtitle=i18n.preflight.banner_subtitle, subtitle_align="left", border_style="#1B6AFF", padding=(0, 5)), "center", vertical="middle"), name="top"),
        Layout(Align(renderable, vertical="bottom"), name="bottom")
    )

    return layout
