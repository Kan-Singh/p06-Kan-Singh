# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import TestCase
from tests.fixtures.transformer_test_data import TestData
from thumbor.transformer import Transformer


def assert_no_empty_crop(calls):
    for call in calls:
        width = call["right"] - call["left"]
        height = call["bottom"] - call["top"]
        assert (
            width >= 1 and height >= 1
        ), f"engine crop produced an empty box: {call}"


class ExtremeAspectCropTestCase(TestCase):
    @gen_test
    async def test_auto_crop_wide_short_target_is_not_empty(self):
        data = TestData(
            source_width=16,
            source_height=16,
            target_width=800,
            target_height=20,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
        )
        ctx = data.to_context()
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        await trans.transform()

        assert engine.calls["crop"], "auto_crop should have cropped"
        assert_no_empty_crop(engine.calls["crop"])
        assert engine.calls["resize"] == [{"width": 800, "height": 20}]

    @gen_test
    async def test_fit_in_1x1_for_very_wide_source(self):
        data = TestData(
            source_width=940,
            source_height=2,
            target_width=1,
            target_height=1,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
            fit_in=True,
        )
        ctx = data.to_context()
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        await trans.transform()

        assert not engine.calls["crop"]
        assert engine.calls["resize"] == [{"width": 1, "height": 1}]

    @gen_test
    async def test_fit_in_width_only_for_very_wide_source(self):
        data = TestData(
            source_width=940,
            source_height=2,
            target_width=100,
            target_height=0,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
            fit_in=True,
        )
        ctx = data.to_context()
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        await trans.transform()

        assert not engine.calls["crop"]
        assert engine.calls["resize"] == [{"width": 100, "height": 1}]
