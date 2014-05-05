# Starting the consles from boot.

## Client Consoles

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

## Server

Note: This is a work in progress it may not work yet!

Copy consolegame.init to /etc/init.d/consolegame

Set the game to start at the start

    update-rc.d consolegame defaults

Start the game manually.

    invoke-rc.d consolegame start

Restart the game.

    invoke-rc.d consolegame restart

Logs could go anwhere? Some to stdout but they may go to syslog so end up in /var/log/syslog
If they do spit out to stdout then we will need to redirect them from the startup script.
