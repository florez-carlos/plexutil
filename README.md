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
To override the language of tv series, modify the tv_language_manifest.json file found in: [Config Location](#config-location) <br >
The file can be modified like such:
```bash
{
  "es-ES": [327417,396583,388477,292262,282670,274522],
  "en-US": []
}
```
Where the key is the language and the list contains the [TVDB](https://www.thetvdb.com/) ids of the desired series to be overriden <br >
For a list of supported languages: [Language](./src/plexutil/enums/language.py)

---

#### Library Preferences
Libraries of type:
- Movie
- Music
- TV

Can have their preferences set in the following files:

- movie_library_preferences.json
- music_library_preferences.json
- tv_library_preferences.json

These files can be found here: [Config Location](#config-location)




## Usage
test


## Development
```bash
source init.sh
```
## Config Location
The config directory of Plexutil is located:
> [!NOTE]
> Replace <YOUR_USER> with your Windows UserName
- Windows
```bash
C:\Users\<YOUR_USER>\Documents\plexutil\config\
```
- Linux
```bash
$HOME/plexutil/config/tv_language_manifest.json
```

## Log Location
The log directory of Plexutil is located:
> [!NOTE]
> Replace <YOUR_USER> with your Windows UserName
- Windows
```bash
C:\Users\<YOUR_USER>\Documents\plexutil\log
```
- Linux
```bash
$HOME/plexutil/log
```
> [!NOTE]
> Log files are archived based on date, such as yyyy-mm-dd.log

## License
[MIT](https://choosealicense.com/licenses/mit/)

