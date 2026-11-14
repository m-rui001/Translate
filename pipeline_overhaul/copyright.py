"""A single copyright page shared by every assembler.

Only attribution is claimed, and nothing else. Boilerplate about the original work's
rights, about the original prevailing, and any restriction on commercial use adds
nothing a reader needs: the author's rights are not ours to state or qualify, and the
translator does not want to restrict reuse.
"""
from __future__ import annotations

import html

CSS = """div.copyright{margin-top:14%;margin-bottom:10%}
div.copyright h1{font-size:1.3em;letter-spacing:.2em;margin:0 0 1.6em;text-align:center}
div.copyright p{text-indent:0;text-align:center;margin:0 0 .6em}
div.copyright p.src{font-size:.95em;color:#555}
div.copyright p.tr{font-size:1em;color:#333;margin-bottom:3em}
div.copyright div.cn{font-size:.82em;line-height:1.85;color:#555;text-align:left;
  border-top:1px solid #ddd;padding-top:1.2em;margin:0 1em}
"""

TEXT = ("本译本由坟头草翻译，保留署名权；除此之外不主张任何权利，"
        "亦不作任何担保。")

# Works whose author died less than fifty years ago are still in copyright in China, so
# the translation cannot be published or attributed. The page therefore carries no
# translator name and no licence claim at all -- only what the reader needs in order to
# know that this is a private reading copy and not a released edition. Putting a name on
# it would turn a private aid into an unlicensed publication.
TEXT_PRIVATE = ("本译本仅供私人阅读使用，不对外发布、不用于任何商业用途；"
                "原作品著作权归原作者及其继承人所有。")


def page(title: str, src_title: str, author: str, style: str = "",
         private: bool = False) -> str:
    """Build the copyright page.

    `private` drops the translator credit and swaps in the private-use notice. It is used
    for in-copyright works, where naming a translator would amount to publishing.
    """
    return ("<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n"
            "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='zh-CN'>"
            "<head><meta charset='utf-8'/><title>版权</title>"
            "<style>" + style + CSS + "</style></head><body>"
            "<div class='copyright'>"
            f"<h1>{html.escape(title)}</h1>"
            f"<p class='src'>{html.escape(src_title)}</p>"
            f"<p class='src'>{html.escape(author)}　著</p>"
            + ("" if private else "<p class='tr'>坟头草　译</p>")
            + f"<div class='cn'>{TEXT_PRIVATE if private else TEXT}</div>"
            "</div></body></html>")
