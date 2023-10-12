#!/bin/bash 

# https://github.com/Stunkymonkey/nautilus-open-any-terminal
sudo apt install python3-nautilus
git clone https://github.com/Stunkymonkey/nautilus-open-any-terminal.git # pip install nautilus-open-any-terminal
cd nautilus-open-any-terminal && sudo ./tools/update-extension-system.sh install 
nautilus -q

sudo cp $HOME/nautilus-open-any-terminal/nautilus_open_any_terminal/schemas/com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal tilix
