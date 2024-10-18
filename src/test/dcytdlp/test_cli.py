"""
tests for dcytdl.cli
"""

import io

import pytest

from dcytdl.cli import (
    create_argparser,
    discogs,
    get_rendered_html,
    init_logging,
    load_config,
    main,
    print_videos,
    youtube_download,
)


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


@pytest.mark.parametrize("debug", [False, True])
def test_init_logging(debug, mocker):
    """basic invocation test"""
    args = mocker.Mock(spec=["debug"])
    args.debug = debug
    mocker.patch("logging.getLogger")
    init_logging(args)


@pytest.mark.parametrize("arg_config", ["custom-config.yml", None])
def test_load_config(arg_config, mocker):
    """basic invocation test"""
    args = mocker.Mock(spec=["config"])
    args.config = arg_config
    mocker.patch("builtins.open", return_value=io.StringIO("---"))
    load_config(args)


def test_print_videos():
    """basic invocation test"""
    videos = [
        {
            "youtubeId": "1",
            "title": "Hack at the zoo",
        }
    ]
    print_videos(videos)


def test_download_videos(mocker):
    """basic invocation test"""
    mocker.patch("yt_dlp.YoutubeDL")
    video_id = "1"
    config = {
        "yt_dlp": {
            "not accessed directly": "by the function",
        },
        "youtube": {"video_base_url": "test/"},
    }
    youtube_download(video_id, config)


@pytest.mark.parametrize("no_download", [True, False])
@pytest.mark.parametrize("unknown_exception", [True, False])
@pytest.mark.parametrize(
    "discogs_exception",
    [
        None,
        discogs.DiscogsException("", {"some": "dsdata"}),
        discogs.DiscogsException("", None),
    ],
)
def test_main(no_download, unknown_exception, discogs_exception, mocker):
    """basic test"""
    args = mocker.Mock(spec=["no_download", "url"])
    args.no_download = no_download
    args.url = "test://url"
    argparser = mocker.Mock(spec=["parse_args"])
    argparser.parse_args.return_value = args
    mocker.patch("dcytdl.cli.create_argparser", return_value=argparser)
    mocker.patch("dcytdl.cli.load_config")
    mocker.patch("dcytdl.cli.init_logging")
    mocker.patch("dcytdl.cli.get_rendered_html")
    videos = [
        {
            "youtubeId": "1",
        }
    ]
    xtr_videos_mock = mocker.patch(
        "dcytdl.cli.discogs.extract_videos", return_value=videos
    )
    mocker.patch("dcytdl.cli.print_videos")
    ytdl_mock = mocker.patch("dcytdl.cli.youtube_download")
    if unknown_exception:
        ytdl_mock.side_effect = Exception("unknown error")

    if discogs_exception:
        xtr_videos_mock.side_effect = discogs_exception
        with pytest.raises(type(discogs_exception)):
            main()
    else:
        main()
