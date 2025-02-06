# Plexutil

CLI tool with helpful functions to manage a Plex server.


> [!NOTE]
> Installation is supported only for the following: 
> - Windows
> - Linux

> [!NOTE]
> Development requires a fully configured [Dotfiles](https://github.com/florez-carlos/dotfiles) dev environment <br>

## Table of Contents

* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Development](#development)


## Installation

```bash
pip install plexutil
```

## Configuration
### Required
Set the host, port, token of your plex server
```bash
plexutil config -host <PLEX_SERVER_HOST> -port <PLEX_SERVER_PORT> -token <PLEX_SERVER_TOKEN>
```
### Optional
#### TV Series Language Override
To override the language of tv series, modify the tv_language_manifest.json file found in:
- Windows
```bash
C:\Users\<YOUR_USER>\Documents\plexutil\config\tv_language_manifest.json
```
- Linux
```bash
$HOME/plexutil/config/tv_language_manifest.json
```
The file can be modified like such:
```bash
{
  "es-ES": [327417,396583,388477,292262,282670,274522],
  "en-US": []
}
```
Where the key is the language and the list contains the [TVDB](https://www.thetvdb.com/) ids of the desired series to be overriden <br >
For a list of supported languages: TODO


## Usage
test


## Development
```bash
source init.sh
```

## License
[MIT](https://choosealicense.com/licenses/mit/)

