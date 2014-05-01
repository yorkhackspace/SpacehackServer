SpaceHack
=========

"Decrease polarity knot to 7!  Set multitronic filter to magenta alert!  Plug in the centrifugal F-screen!"

SpaceHack is an exciting yet light-hearted starship emergency simulator, a hands-on visitor-participation game set aboard the perpetually disaster-prone USS Guppy on its voyage around the universe.  Newly recruited Star Corps cadets must operate their command consoles to flip switches, turn dials, push buttons and more according to a sequence of instructions relayed to them by their fellow crew memebers, or face destruction.  How long can you keep the ship safe?

Directory structure
===================

The 'ConsoleGame' repository contains all the software we wrote to run the game.  Other repositories in the YorkHackSpace area contain files detailing the physical laser-cut and 3D-printed parts we created in fabrication.

"Client" is the game client, which runs on Beaglebone Black and handles communications with physical hardware, and game communications with the server over MQTT.  It is essentially a configurable fairly dumb client which reads its configuration from file, and uses it to set up and poll controls, register its capabilities with the server, display text on its seven LCD displays when sent from the server, and report control state values to the server.  The client software understands the mapping between its hardware control implementations and the server's abstracted control types, but doesn't otherwise have and game logic at all or visibility of any other conencted clients.

"Server" runs on a Raspberry Pi and handles running the game, control text generation and sound effects as well as hosting the game's MQTT broker.  The server knows nothing about particular hardware implementations of controls, only abstracted control types whose implementation is managed by the clients.  For instance the server understands a 'toggle' control type, but doesn't know that the clients might implement that with an illuminated button, or a flip switch, or a pair of buttons marked 'On' and 'Off', or a potentiometer with an 'Off' end and an 'On' end.

"ProofOfConcept" originally tested proposed candidate infrastructure to prove the concept was workable on Beaglebone and Raspberry Pi, and thereafter remained as an experimental scratchpad area.
