SpaceHack
=========

"Decrease polarity knot to 7!  Set multitronic filter to magenta alert!  Plug in the centrifugal F-screen!"

SpaceHack is an exciting yet light-hearted starship emergency simulator, a hands-on visitor-participation game set aboard the perpetually disaster-prone USS Guppy on its voyage around the universe.  Newly recruited Star Corps cadets must operate their command consoles to flip switches, turn dials, push buttons and more according to a sequence of instructions relayed to them by their fellow crew memebers, or face destruction.  How long can you keep the ship safe?

[![SpaceHack at Maker Faire UK](http://img.youtube.com/vi/oCWH3n4aLJI/0.jpg)](http://www.youtube.com/watch?v=oCWH3n4aLJI)

Server side code
================


"Server" runs on a Raspberry Pi and handles running the game, control text generation and sound effects as well as hosting the game's MQTT broker.  The server knows nothing about particular hardware implementations of controls, only abstracted control types whose implementation is managed by the clients.  For instance the server understands a 'toggle' control type, but doesn't know that the clients might implement that with an illuminated button, or a flip switch, or a pair of buttons marked 'On' and 'Off', or a potentiometer with an 'Off' end and an 'On' end.

Running locally (testing)
=========================

You'll need to install mosquitto, and have fairly up-to-date libraries (as of writing, Ubuntu trusty requires a PPA: https://launchpad.net/~mosquitto-dev/+archive/ubuntu/mosquitto-ppa

To run the server, you need to start mosquitto first.
