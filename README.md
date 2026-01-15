# Plexutil

CLI for Plex Media Server.

![PyPI Version](https://img.shields.io/pypi/v/plexutil)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Platform](https://img.shields.io/badge/Platform-Cross--Platform-success)
![PyPI Status](https://img.shields.io/pypi/status/plexutil)
![CLI](https://img.shields.io/badge/Interface-CLI-important)


> [!NOTE]
> Installation is supported only for the following: 
> - Windows (amd64)
> - Linux (amd64)
>    - X11
>    - Wayland


## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
  * [Creating a media library](#creating-a-media-library-or-music-playlist)
  * [Deleting a media library](#deleting-a-media-library-or-music-playlist)
  * [Exporting/Importing Music Playlists](#exportingimporting-music-playlists)
* [Development](#development)
* [Log Location](#log-location)


## Installation
> [!NOTE]
> - Requires Python 3.11+<br >
> - Requires pip
```bash
pip install plexutil
```
---

## Usage
### Creating a media library or music playlist:
> [!NOTE]
> If language is not supplied, the default is en-US
```bash
plexutil create
```

### Deleting a media library or music playlist:
```bash
plexutil delete
```

### Exporting/Importing Music Playlists
Music Playlists can be exported to a playlists.db file, this file can later be imported to another Plex server with plexutil
```bash
plexutil download
```
This action will create a playlists.db file in your current directory <br >
This file can then be used to recreate the playlists in another Plex Server with plexutil by doing
```bash
plexutil upload
```
> [!NOTE]
> The songs in the Music Library of the importing server must match the songs in the exporting server

## Development
> [!NOTE]
> Development requires a fully configured [Dotfiles](https://github.com/florez-carlos/dotfiles) dev environment <br>
```bash
source init.sh
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

