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
* [Usage](#usage)
* [Development](#development)
  * [Clone the repo in workspace with recurse submodules](#clone-the-repo-in-workspace-with-recurse-submodules)
  * [Install Git Hooks](#install-git-hooks) 


## Installation

```bash
python3 -m pip install plexutil
```

### Create the plexutil/config directory

This directory is necessary to store our custom configuration of server settings and library preferences


#### Windows

```bash
mkdir C:\Users\%USERNAME%\Documents\plexutil\config
```

#### Linux

```bash
mkdir -p $HOME/plexutil/config
```

### Add the sample Configuration files to the plexutil/config directory
- Download the sample Preferences files located in ./samples/preferences and place in the plexutil config directory
- Download the sample Manifests files located in ./samples/mainfests and place in the plexutil config directory
- Download the sample Playlists files located in ./samples/playlists and place in the plexutil config directory

The plexutil config directory should hold the folllowing

```bash
plexutil/config/music_playlist.json
plexutil/config/tv_language_manifest.json
plexutil/config/movie_library_preferences.json
plexutil/config/tv_library_preferences.json
plexutil/config/music_library_preferences.json
plexutil/config/plex_server_setting_preferences.json
```



## Usage
test




## License
[MIT](https://choosealicense.com/licenses/mit/)

