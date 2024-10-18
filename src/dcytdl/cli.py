"""
Download the Discogs page and extract YouTube video links
along with metadata about the artist and tracks.
"""

import argparse
import enum
import json
import logging
import sys

import tabulate
import yaml
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from dcytdl import __version__, discogs


def create_argparser():
    """Create the command line argument parser"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "url",
        help="url to a release at Discogs",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )

    parser.add_argument(
        "--config",
        help="optional path to config file. The default path is config.yml "
        "in the current directory",
    )

    parser.add_argument(
        "--no-download",
        action="store_true",
        help="don't download the actual file. just print the list of videos",
    )

    return parser


def get_rendered_html(url, config):
    """
    Get rendered HTML from Discogs.

    The page content is rendered via JavaScript, requiring a headless
    Chrome browser to execute the scripts and return the fully rendered HTML.
    """
    chrome_options = Options()
    # Use headless mode for Chrome >= 109
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("user-agent=" + config["user_agent"])
    driver = webdriver.Chrome(options=chrome_options)

    # Load the Discogs URL and retrieve the fully rendered HTML
    driver.get(url)
    result = driver.page_source
    driver.quit()
    return result


def load_config(args):
    """
    Load the config file and merge it with default config.
    Return the config as dict
    """
    if args.config:
        filename = args.config
    else:
        filename = "config.yml"

    with open(filename, "r", encoding="utf8") as open_file:
        return yaml.safe_load(open_file)


def init_logging(args):
    """
    Initialize logging. When --debug has been provided, the log level
    will be set to DEBUG, otherwise logging with be disabled.
    """
    log = logging.getLogger()
    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.NOTSET)
    return log


def print_videos(videos):
    """Print YouTube videos from dsdata in a tabular format"""
    headers = ["video_id", "name"]
    data = []
    for item in videos:
        data.append(
            [
                item["youtubeId"],
                item["title"],
            ],
        )

    print(tabulate.tabulate(data, headers))


def youtube_download(video_id, config):
    """Download video from YouTube using the yt-dlp library"""

    ytdl = yt_dlp.YoutubeDL(config["yt_dlp"])
    url = config["youtube"]["video_base_url"] + video_id
    ytdl.download(url)


class CliExitStatus(enum.IntEnum):
    """Command exit codes"""

    SUCCESS = 0  # Successful execution
    ERROR = 1  # Error encountered


def main():
    """Entry point"""
    try:
        print("--- scraping video ids ...\n")
        args = create_argparser().parse_args()
        config = load_config(args)
        init_logging(args)
        html = get_rendered_html(args.url, config)
        videos = discogs.extract_videos(html)
        print_videos(videos)

        if args.no_download:
            return CliExitStatus.SUCCESS

        print("\n--- downloading files ...\n")

        for item in videos:
            try:
                youtube_download(item["youtubeId"], config)
            # pylint: disable=broad-exception-caught
            except Exception as e:
                print(e)

        return CliExitStatus.SUCCESS

    except discogs.DiscogsException as e:
        if e.dsdata:
            json.dump(e.dsdata, sys.stderr, indent=2)
        sys.stderr.write("\n")
        raise


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
