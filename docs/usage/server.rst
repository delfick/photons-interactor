.. _server:

Server
======

Photons Interactor is a server that sits on your network constantly looking for
lights and finding information about them.

This allows you to make changes to your lights without the startup cost of
Photons or of discovering your devices.

To start the server, install photons-interactor and then run::

    $ photons-interactor serve

If you don't have a configuration file present it will prompt you to make the
minimal configuration required.
