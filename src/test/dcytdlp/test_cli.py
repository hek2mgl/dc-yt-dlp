"""
tests for dcytdl.cli
"""

import textwrap

import pytest

from dcytdl.cli import (
    DsDataException,
    create_argparser,
    extract_dsdata,
    get_rendered_html,
)


class TestDsDataException:
    """DsData Exception tests"""

    def test__init__(self):
        """basic test - initialization of the exception"""
        exception = DsDataException("test msg", {"test": "data"})
        assert exception.dsdata["test"] == "data"


def test_create_argparser():
    """basic invocation test"""
    assert create_argparser()


def test_get_rendered_html(mocker):
    """basic invocation test"""
    driver = mocker.Mock(
        spec=[
            "get",
            "page_source",
            "quit",
        ]
    )
    mocker.patch("dcytdl.cli.webdriver.Chrome", return_value=driver)
    config = {
        "user_agent": "test user agent",
    }

    result = get_rendered_html("http://test.url", config)
    assert result == driver.page_source


@pytest.mark.parametrize("item_found", [True, False])
def test_extract_dsdata(item_found):
    """test that json can be extracted from the element with id "dsdata" """
    if item_found:
        html = textwrap.dedent(
            """
            <html>
                <body>
                    <script id="dsdata">{"abc":"test"}</script>
                </body>
            <html>
        """
        )
        assert extract_dsdata(html) == {"abc": "test"}
    else:
        html = textwrap.dedent(
            """
            <html>
                <body></body>
            <html>
        """
        )

        with pytest.raises(DsDataException):
            extract_dsdata(html)
