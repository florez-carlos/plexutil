#!/usr/bin/zsh -i

color_red=$(tput setaf 1)
color_green=$(tput setaf 2)
color_yellow=$(tput setaf 3)
color_normal=$(tput sgr0)
setopt aliases

errors=false

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
printf "%s\n" "Attempting Azure login"
printf "%s\n" ""
sleep 1
az login --service-principal --username $AZ_LOGIN_APP_ID --tenant $AZ_LOGIN_TENANT_ID --password $AZ_LOGIN_CERT_PATH

if [ $? -ne 0 ]; then
    printf "%s\n" ""
    printf "%s\n" "${color_red}FAIL${color_normal}: Could not login to AZ"
    printf "%s\n" ""
    errors=true

fi

file_names=(
"music_playlists.json"
"tv_language_manifest.json"
"tv_library_preferences.json"
"movie_library_preferences.json"
"music_library_preferences.json"
"plex_server_setting_preferences.json"
)

printf "%s\n" ""
printf "%s\n" "Checking config files exist in $HOME/plexutil/config"
printf "%s\n" ""
mkdir -p $HOME/plexutil/config
mkdir -p $HOME/plexutil/log
for file_name in "${file_names[@]}"; do
    if [ -e "$HOME/plexutil/config/$file_name" ]; then
        printf "%s\n" ""
        printf "%s\n" "${color_green}EXISTS${color_normal}: $file_name"
        printf "%s\n" ""
        sleep 1
    else
        printf "%s\n" ""
        printf "%s\n" "${color_yellow}MISSING${color_normal}: $file_name"
        printf "%s\n" ""
        sleep 1
        printf "%s\n" ""
        printf "%s\n" "Fetching missing file: $file_name"
        printf "%s\n" ""
        sleep 1
        az storage blob download \
        --account-name plexutilblobs \
        --container-name files \
        --name $file_name \
        --file $HOME/plexutil/config/$file_name \
        --auth-mode login

        if [ $? -ne 0 ]; then
            printf "%s\n" ""
            printf "%s\n" "${color_red}FAIL${color_normal}: Could not fetch missing file $file_name"
            printf "%s\n" ""
            errors=true

        fi

    fi
done

if [ "$errors" = true ]; then

    printf "%s\n" ""
    printf "%s\n" "${color_red}FAIL${color_normal}: Init failed, 1 or more errros detected, check output"
    printf "%s\n" ""

else

    printf "%s\n" ""
    printf "%s\n" "${color_green}SUCCESS${color_normal}: Init complete!"
    printf "%s\n" ""
    
fi


