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

### Configuration

Configuration is store in a config file. The application loads the configuration from `config.yml` in the current directory. A default config.file called `config.dist.yml` is included in the the repository.

For the the initial configuration, copy the default config to `config.yml`:

```console
$ cp config.dist.yml config.yml
```

## Usage

Navigate to [Discogs](https://www.discogs.com) and find a release you like.

Download all videos from the release page:

```console
$ dc-yt-dlp https://www.discogs.com/de/master/96581-Rick-Astley-Hold-Me-In-Your-Arms
```


## yt-dlp

`yt-dlp` seems to support Discogs natively. However, when trying it I'm a getting a 403 respnse:

```console
$ yt-dlp https://www.discogs.com/de/release/624390-Rick-Astley-Hold-Me-In-Your-Arms 
[generic] Extracting URL: https://www.discogs.com/de/release/624390-Rick-Astley-Hold-Me-In-Your-Arms
[generic] 624390-Rick-Astley-Hold-Me-In-Your-Arms: Downloading webpage
ERROR: [generic] Unable to download webpage: HTTP Error 403: Forbidden (caused by <HTTPError 403: Forbidden>)
```

Even with a forged user-agent, still a 403 is received:

```console
$ yt-dlp --user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"  https://www.discogs.com/de/release/624390-Rick-Astley-Hold-Me-In-Your-Arms 
[generic] Extracting URL: https://www.discogs.com/de/release/624390-Rick-Astley-Hold-Me-In-Your-Arms
[generic] 624390-Rick-Astley-Hold-Me-In-Your-Arms: Downloading webpage
ERROR: [generic] Unable to download webpage: HTTP Error 403: Forbidden (caused by <HTTPError 403: Forbidden>)
```

TODO: debug this ^^^. Native support by yt-dlp would make this whole project obsolete (lesson learned)
