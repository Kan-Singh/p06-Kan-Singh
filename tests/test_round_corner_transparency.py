# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# Regression test for issue #2: transparent rounded corners carry a dark ring.
# Edge pixels on the arc must keep their original RGB and become partly
# transparent. Opaque pixels on the arc must not be darkened.

from tornado.testing import gen_test

from tests.base import FilterTestCase

RADIUS = 50


class RoundCornerTransparencyTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_arc_pixels_are_partially_transparent(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            f"round_corner({RADIUS},255,0,0,1)",
            mode="RGBA",
        )

        partial = 0
        for y in range(RADIUS):
            for x in range(RADIUS):
                _, _, _, alpha = image.getpixel((x, y))
                if 0 < alpha < 255:
                    partial += 1

        assert partial > 0, "no partially transparent edge pixels found"

    @gen_test
    async def test_transparent_arc_pixels_keep_original_rgb(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            f"round_corner({RADIUS},255,0,0,1)",
            mode="RGBA",
        )
        source = self.get_fixture("source.jpg", mode="RGB")

        darkened = []
        for y in range(RADIUS):
            for x in range(RADIUS):
                r, g, b, alpha = image.getpixel((x, y))
                if alpha != 255:
                    continue
                src_r, src_g, src_b = source.getpixel((x, y))
                if (r, g, b) != (src_r, src_g, src_b):
                    darkened.append((x, y, (r, g, b), (src_r, src_g, src_b)))

        assert not darkened, (
            f"{len(darkened)} opaque corner pixels differ from the source "
            f"RGB, first: {darkened[:3]}"
        )
