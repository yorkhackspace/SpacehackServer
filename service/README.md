# Starting the consles from boot.

Copy the file consolegame.service to /etc/systemd/system and then run

    systemctl --system daemon-reload

Enable the service

    systemctl enable consolegame

To restart the service

    systemctl restart consolegame

To start the game

    systemctl start console 

To stop the game

    systemctl stop console

To check the service status

    systemctl status consolegame

To look at the output

    journalctl -u consolegame


