"""
Module for extracting and formatting data from the Discogs API
"""

import json
import logging

import bs4


class DiscogsException(Exception):
    """
    Custom exception to capture error messages and associated Discogs data
    for debugging purposes.

    This exception is used to provide detailed information about errors
    encountered while interacting with the Discogs API, including the
    original error message and any relevant data extracted from the
    Discogs response.

    Attributes:
        msg (str): The error message associated with the exception.
        dsdata (dict or None): The Discogs data related to the error, if
                               available.
    """

    def __init__(self, msg, dsdata):
        super().__init__(msg)
        self.msg = msg
        self.dsdata = dsdata


def _extract_dsdata(html):
    """
    Extract the dsdata JSON blob from the rendered Discogs page.

    This function searches for a <script> tag with the id 'dsdata' in the
    provided HTML content. If found, it logs the contents of the tag and
    parses the JSON data. If the <script> tag is not found, a
    DiscogsException is raised.

    Args:
        html (str): The HTML content of the rendered Discogs page.

    Returns:
        dict: The parsed JSON data extracted from the dsdata blob.

    Raises:
        DiscogsException: If the <script> element with id 'dsdata' cannot
                          be found in the HTML.
    """
    soup = bs4.BeautifulSoup(html, features="html.parser")
    result = soup.find(id="dsdata")
    if result:
        log = logging.getLogger("discogs_scraper")
        log.debug("found dsdata: %s", str(result.contents[0]))
        return json.loads(result.contents[0])
    raise DiscogsException(
        "Can't find <script> element with id=dsdata",
        None,
    )


def _fmt_release_key(string):
    """
    Helper function to format key strings to match Discogs' expected key
    format.

    This function takes a key string and transforms it to conform to the
    Discogs API's expected format. Specifically, it capitalizes the first
    letter, replaces "discogsid" with "discogsId", and removes parentheses.
    Additionally, it ensures that the opening brace is followed by a colon
    with no space.

    Example:
        Input:  release({"discogsId":624390})
        Output: Release:{"discogsId":624390}

    Args:
        string (str): The key string to be formatted.

    Returns:
        str: The formatted key string.
    """
    return (
        string.capitalize()
        .replace("discogsid", "discogsId")
        .replace("(", "")
        .replace(")", "")
        .replace("{", ":{")
    )


def extract_videos(html):
    """
    Extracts video information from the provided HTML content.

    This function parses the HTML to extract the 'dsdata' object, which
    contains information about releases. It attempts to find a release
    that contains video data, first by looking for keys that start with
    "release" and then by checking for keys that start with "Master" if
    no videos are found in the initial search.

    If a release with videos is found, the function returns the list of
    videos. If no release is found or if there is a KeyError during the
    extraction process, a DiscogsException is raised.

    Args:
        html (str): The HTML content from which to extract video
                    information.

    Returns:
        list: A list of videos associated with the release.

    Raises:
        DiscogsException: If no release is found in the dsdata or if a
                          KeyError occurs during the extraction process.
    """
    dsdata = _extract_dsdata(html)
    release = None
    root_query = dsdata["data"]["ROOT_QUERY"]
    for key in root_query.keys():
        if key.startswith("release"):
            # fmt_key = _fmt_release_key(key)
            # release = dsdata["data"][fmt_key]
            ref = root_query[key]["__ref"]
            release = dsdata["data"][ref]
            # Sometimes, the videos are only populated via the the master
            # release record
            if release.get("videos"):
                break
    else:
        for key in dsdata["data"].keys():
            if key.startswith("Master"):
                release = dsdata["data"][key]
                break
        else:
            raise DiscogsException("Release not found in dsdata", dsdata)
    return release["videos"]
