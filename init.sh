#!/usr/bin/zsh -i

color_red=$(tput setaf 1)
color_green=$(tput setaf 2)
color_yellow=$(tput setaf 3)
color_normal=$(tput sgr0)
setopt aliases

required_python_version_path_name="3.11"
required_python_version="3.11.6"

if [ $UID -eq 0 ]; then
    printf "%s\n" "${color_red}ERROR:${color_normal}Please DO NOT run this script with sudo"
    exit 1
fi

current_python_version=$(python -V | sed 's/Python //;s/+//')
if ! dpkg --compare-versions "$current_python_version" eq "$required_python_version";then
    printf "%s\n" ""
    printf "%s\n" "${color_red}ERROR${color_normal}: Current Python is $current_python_version but $required_python_version required"
    printf "%s\n" ""
    exit 1
fi

python -m venv "$HOME"/venv/plexutil
# shellcheck source=/dev/null
. "$HOME"/venv/plexutil/bin/activate
if [ "$VIRTUAL_ENV" != "$HOME"/venv/plexutil ]; then
    printf "%s\n" ""
    printf "%s\n" "${color_red}ERROR${color_normal}: Attempted to set venv to: $HOME/venv/plexutl but current venv is $VIRTUAL_ENV"
    printf "%s\n" ""
    exit 1
fi
pip install -r requirements.txt

export PYTHONPATH=$VIRTUAL_ENV/lib/python"$required_python_version_path_name"/site-packages/


printf "%s\n" ""
printf "%s\n" "${color_green}SUCCESS${color_normal}: Init complete!"
# printf "%s\n" "${color_yellow}TO ACTIVATE VENV, RUN${color_normal}:. $HOME/venv/plexutil/bin/activate"
printf "%s\n" ""
# exit 0
