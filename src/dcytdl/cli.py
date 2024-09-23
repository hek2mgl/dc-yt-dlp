"""
Download the Discogs page and extract YouTube video links
along with metadata about the artist and tracks.
"""

import argparse
import enum
import json
import sys

import bs4
import tabulate
import yaml
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from dcytdl import __version__


class DsDataException(Exception):
    """
    Custom exception to capture the error message and Discogs data for
    debugging
    """

    def __init__(self, msg, dsdata):
        super().__init__(msg)
        self.msg = msg
        self.dsdata = dsdata


def create_argparser():
    """Create the command line argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        help="Url to a release at Discogs",
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


def extract_dsdata(html):
    """
    Extract the dsdata JSON blob from the rendered Discogs page.
    The blob is located within a <script> tag with id='dsdata'.
    """
    soup = bs4.BeautifulSoup(html, features="html.parser")
    for item in soup.find(id="dsdata"):
        return json.loads(item)


def _fmt_release_key(string):
    """
    Helper function to format key strings to match Discogs' expected key format
    """
    return (
        string.capitalize()
        .replace("discogsid", "discogsId")
        .replace("(", "")
        .replace(")", "")
        .replace("{", ":{")
    )


def extract_videos(dsdata):
    """
    Extract YouTube video information from the provided Discogs data (dsdata).

    This function searches through the 'dsdata' JSON structure to locate a
    release or master release, and extracts the associated video information.
    It follows this process:

    1. Looks for a key that starts with 'release' in the 'ROOT_QUERY'
       section of dsdata. If found, it formats the key and retrieves the
       corresponding release data.

    2. If no 'release' key is found, it falls back to searching for a 'Master'
       release key within the main dsdata structure and retrieves that if
       available.

    3. If neither a release nor master release is found, the function raises
       a custom 'DsDataException' to indicate the error.

    4. Finally, if a valid release is found, the function returns the list
       of videos from the release's data.

    Parameters:
        dsdata (dict): The JSON data structure retrieved from Discogs
                       containing release information.

    Returns:
        list: A list of video information associated with the release
              (YouTube links and metadata).

    Raises:
        DsDataException: If no release or master release is found, or
                         if the expected key structure does not exist
                         (e.g., due to a missing or malformed dsdata blob).
    """
    try:
        release = None
        root_query = dsdata["data"]["ROOT_QUERY"]
        for key in root_query.keys():
            if key.startswith("release"):
                fmt_key = _fmt_release_key(key)
                release = dsdata["data"][fmt_key]
                break
        else:
            for key in dsdata["data"].keys():
                if key.startswith("Master"):
                    release = dsdata["data"][key]
                    break
            else:
                raise DsDataException("Release not found in dsdata", dsdata)

        return release["videos"]
    except KeyError as e:
        raise DsDataException(f"KeyError: {e}", dsdata) from e


def progress_hook(status):
    """
    Hook that handles the progress of the download. Called periodically
    by yt-dlp with the current progress status.
    """
    if status["status"] == "downloading":
        total_bytes = status.get("total_bytes", 0)
        downloaded_bytes = status.get("downloaded_bytes", 0)
        speed = status.get("speed", 0)
        eta = status.get("eta", 0)

        if total_bytes > 0:
            progress = downloaded_bytes / total_bytes
            progress_prefix = f"[{'=' * int(progress * 40):40s}]"
            progress_value = f"{progress * 100:.2f}%"
            progress_bar = f"{progress_prefix} {progress_value}"
        else:
            progress_bar = "[Unknown Progress]"

        speed_str = f"{speed / 1024:.2f} KB/s" if speed else "N/A"
        eta_str = f"{eta:.0f} seconds remaining" if eta else "N/A"

        # Output progress bar, speed, and ETA
        sys.stdout.write(
            f"\r{progress_bar} | Speed: {speed_str} | ETA: {eta_str}",
        )
        sys.stdout.flush()

    elif status["status"] == "finished":
        print("\nDownload complete!")


def youtube_download(video_id, config):
    """Download video from YouTube using the yt-dlp library"""
    ydl_opts = {
        # Specify the format and postprocessor for extracting audio
        "format": "m4a/bestaudio/best",
        # See help(yt_dlp.postprocessor) for a list of available
        # Postprocessors and their arguments
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
        "paths": {
            "home": config["output_directory"],
        },
        "logger": CliOutput(),
        "progress_hooks": [progress_hook],
    }
    ytdl = yt_dlp.YoutubeDL(ydl_opts)
    url = config["youtube"]["video_base_url"] + video_id
    ytdl.download(url)


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


class CliOutput:
    """Console output class"""

    def debug(self, msg):
        """Handle debug messages"""
        # For compatibility with youtube-dl, both debug and info are
        # passed into debug You can distinguish them by the prefix '[debug] '
        if msg.startswith("[debug] "):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        """Handle info messages"""

    def warning(self, msg):
        """Handle warning messages"""

    def error(self, msg):
        """Handle error messages"""
        print(msg)

    def print_videos(self, videos):
        """Print YouTube videos from dsdata in a tabular format"""
        headers = ["video_id", "name", "duration"]
        data = []
        for item in videos:
            data.append(
                [
                    item["youtubeId"],
                    item["title"],
                    item["duration"],
                ],
            )

        print(tabulate.tabulate(data, headers))


class CliExitStatus(enum.Enum):
    """Command exit codes"""

    SUCCESS = 0  # Successful execution
    ERROR = 1  # Error encountered


def main():
    """Entry point"""
    try:
        args = create_argparser().parse_args()
        config = load_config(args)
        output = CliOutput()
        html = get_rendered_html(args.url, config)
        dsdata = extract_dsdata(html)
        videos = extract_videos(dsdata)
        output.print_videos(videos)

        for item in videos:
            try:
                youtube_download(item["youtubeId"], config)
            # pylint: disable=broad-exception-caught
            except Exception as e:
                print(e)

        return CliExitStatus.SUCCESS
    except DsDataException as e:
        json.dump(e.dsdata, sys.stderr, indent=2)
        sys.stderr.write("\n")
        json.dump(e.msg, sys.stderr)
        sys.stderr.write("\n")
        return CliExitStatus.ERROR


if __name__ == "__main__":
    sys.exit(main())
