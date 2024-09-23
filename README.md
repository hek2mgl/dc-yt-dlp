# dc-yt-dlp

Scrape video links from a Discogs release page and download them with yt-dlp

## Installation

- Clone the repository
- Create a virtualenv (See: [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/))
- Run pip install .
- Copy `config.dist.yml` to `config.yml`

```console
$ git clone https://github.com/hek2mgl/dc-yt-dlp
$ cd dc-yt-dlp
$ mkvirtualenv -a . dc-yt-dlp
$ pip install .
$ cp config.dist.yml config.yml
```

## Usage

Navigate to [Discogs](https://www.discogs.com) and find a release you like.

Download all videos from the release page:

```console
$ dc-yt-dlp https://www.discogs.com/de/master/96581-Rick-Astley-Hold-Me-In-Your-Arms
```
