code-format:
	isort --line-length 79 --profile black src
	black src

code-check:
	isort --line-length 79 --profile black --check src
	black --check src
	pylint src
	flake8 src

install:
	cp scripts/wrapper.sh /usr/local/bin/dc-yt-dlp
	chmod +x /usr/local/bin/dc-yt-dlp
