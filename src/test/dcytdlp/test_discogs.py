"""
tests for dcytdl.discogs
"""

import textwrap

import pytest

from dcytdl.discogs import (
    DiscogsException,
    _extract_dsdata,
    _fmt_release_key,
    extract_videos,
)


class TestDiscogsException:
    """Discogs Exception tests"""

    def test__init__(self):
        """basic test - initialization of the exception"""
        exception = DiscogsException("test msg", {"test": "data"})
        assert exception.dsdata["test"] == "data"


@pytest.mark.parametrize("item_found", [True, False])
def test_extract_dsdata(item_found):
    """test that json can be extracted from the element with id "dsdata" """
    if item_found:
        html = textwrap.dedent(
            """
            <html>
                <body>
                    <script id="dsdata">{"abc":"test"}</script>
                    <script id="dsdata">{"abc":"test"}</script>
                </body>
            <html>
        """
        )
        assert _extract_dsdata(html) == {"abc": "test"}
    else:
        html = textwrap.dedent(
            """
            <html>
                <body></body>
            <html>
        """
        )

        with pytest.raises(DiscogsException):
            _extract_dsdata(html)


def test__fmt__release_key():
    """
    input:  release({"discogsId":624390})
    output: Release:{"discogsId":624390}
    """
    assert (
        _fmt_release_key('release({"discogsId":624390})')
        == 'Release:{"discogsId":624390}'
    )


@pytest.mark.parametrize(
    "dsdata",
    [
        {
            "data": {
                "ROOT_QUERY": {
                    "__typename": "Query",
                    "cartCount": {
                        "__typename": "MarketplaceCartCountConnection",
                        "totalCount": 0,
                    },
                    'release({"discogsId":123})': {
                        "__ref": 'Release:{"discogsId":123}'
                    },
                    "unreadMessagesCount": {
                        "__typename": "ProfileUnreadMessagesCountConnection",
                        "totalCount": 0,
                    },
                    "viewer": None,
                },
                'Release:{"discogsId":123}': {
                    "videos": ["video_xyz"],
                },
            },
        },
        {
            "data": {
                "ROOT_QUERY": {
                    "__typename": "Query",
                    "cartCount": {
                        "__typename": "MarketplaceCartCountConnection",
                        "totalCount": 0,
                    },
                    'release({"discogsId":123})': {
                        "__ref": 'Release:{"discogsId":123}'
                    },
                    "unreadMessagesCount": {
                        "__typename": "ProfileUnreadMessagesCountConnection",
                        "totalCount": 0,
                    },
                    "viewer": None,
                },
                'Release:{"discogsId":123}': {
                    "videos": [],
                },
            },
        },
        {
            "data": {
                "ROOT_QUERY": {
                    "__typename": "Query",
                    "cartCount": {
                        "__typename": "MarketplaceCartCountConnection",
                        "totalCount": 0,
                    },
                    'release({"discogsId":123})': {
                        "__ref": 'Release:{"discogsId":123}'
                    },
                    "unreadMessagesCount": {
                        "__typename": "ProfileUnreadMessagesCountConnection",
                        "totalCount": 0,
                    },
                    "viewer": None,
                },
                'Release:{"discogsId":123}': {
                    "videos": [],
                },
                'MasterRelease:{"discogsId":123}': {
                    "videos": ["video_xyz"],
                },
            },
        },
        {
            "data": {
                "ROOT_QUERY": {
                    "__typename": "Query",
                    "cartCount": {
                        "__typename": "MarketplaceCartCountConnection",
                        "totalCount": 0,
                    },
                    'release({"discogsId":123})': {
                        "__ref": 'Release:{"discogsId":123}'
                    },
                    "unreadMessagesCount": {
                        "__typename": "ProfileUnreadMessagesCountConnection",
                        "totalCount": 0,
                    },
                    "viewer": None,
                },
                'Release:{"discogsId":123}': {
                    "videos": [],
                },
            },
        },
    ],
)
def test_extract_videos(dsdata, mocker):
    """
    Test that video ids get extracted correctly from the HTML document
    """
    mocker.patch(
        "dcytdl.discogs._extract_dsdata",
        return_value=dsdata,
    )

    if (
        'Release:{"discogsId":123}' in dsdata["data"]
        and not dsdata["data"]['Release:{"discogsId":123}']["videos"]
        and 'MasterRelease:{"discogsId":123}' not in dsdata["data"]
    ):
        with pytest.raises(DiscogsException):
            extract_videos(dsdata)
    else:
        assert extract_videos(dsdata) == ["video_xyz"]
