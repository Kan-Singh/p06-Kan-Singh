# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_context():
    cfg = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
        PILLOW_PRESERVE_INDEXED_MODE=True,
    )
    cfg.STORAGE = "thumbor.storages.no_storage"
    return Context(config=cfg)


def make_transparent_gif():
    # Palette GIF: left half is palette index 0 (transparent),
    # right half is index 1 (red, opaque).
    img = Image.new("P", (20, 20), 1)
    img.putpalette([0, 0, 0, 255, 0, 0] + [0, 0, 0] * 254)
    img.paste(0, (0, 0, 10, 20))
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


def make_opaque_gif():
    # Palette GIF with no transparency at all.
    img = Image.new("P", (20, 20), 1)
    img.putpalette([0, 0, 0, 255, 0, 0] + [0, 0, 0] * 254)
    buffer = BytesIO()
    img.save(buffer, "GIF")
    return buffer.getvalue()


def make_multi_transparent_gif():
    # Truecolour source with two distinct fully transparent colours
    # (top-left and bottom-left) and an opaque red right half.
    img = Image.new("RGBA", (20, 20), (255, 0, 0, 255))
    img.paste((0, 0, 0, 0), (0, 0, 10, 10))
    img.paste((255, 255, 255, 0), (0, 10, 10, 20))
    buffer = BytesIO()
    img.save(buffer, "GIF")
    return buffer.getvalue()


def test_resized_gif_keeps_transparency_index():
    engine = Engine(make_context())
    engine.load(make_transparent_gif(), ".gif")

    engine.resize(10, 10)
    img = Image.open(BytesIO(engine.read(".gif")))

    assert img.info.get("transparency") is not None
    assert img.convert("RGBA").getpixel((0, 0))[3] == 0


def test_opaque_gif_stays_opaque_after_resize():
    engine = Engine(make_context())
    engine.load(make_opaque_gif(), ".gif")

    engine.resize(10, 10)
    img = Image.open(BytesIO(engine.read(".gif")))

    assert img.info.get("transparency") is None
    alpha = img.convert("RGBA").getchannel("A")
    assert alpha.getextrema() == (255, 255)


def test_multiple_transparent_colors_stay_transparent():
    engine = Engine(make_context())
    engine.load(make_multi_transparent_gif(), ".gif")

    engine.resize(10, 10)
    img = Image.open(BytesIO(engine.read(".gif")))
    rgba = img.convert("RGBA")

    assert img.info.get("transparency") is not None
    assert rgba.getpixel((0, 0))[3] == 0
    assert rgba.getpixel((0, 9))[3] == 0
    assert rgba.getpixel((9, 5))[3] == 255
