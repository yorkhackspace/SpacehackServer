# Starting the consles from boot.

Copy the file consolegame.service to /etc/systemd/system and then run

    systemctl --system daemon-reload

To start the game

    systemctl start console 

To stop the game

    systemctl stop console

To look at the output

    journalctl -u consolegame


