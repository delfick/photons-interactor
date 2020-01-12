.. _web_interface:

Web Interface
=============

When you start photons-interactor, it will start a server (by default on port
6100) that will present you with a simple interface.

You can use this interface for the following:

    * Selection of lights on your network to use a color wheel with for power
      and color changes

    * Start tile animations on individual tiles or on all tiles at the same
      time

    * Arrange the position of tiles relative to each other.

The server can also create and run scenes, however this is not exposed in the
web interface at this time.

Arranging the tile positions is necessary if you want to run animations on
multiple tiles at the same time. This allows the animation to understand where
tiles are relative to each other and treat multiple tiles as appearing on the
same canvas.
