.. _configuration:

Configuration
=============

You can alter photons-interactor settings from your configuration file.

By default this is ``interactor.yml`` in the current directory you start the
server from.

You can change where this configuration is by setting the ``LIFX_CONFIG``
environment variable to the location of your configuration file.

It will also load ``~/.photons_apprc.yml``.

You can load extra files from either of these locations with something like:

.. code-block:: yaml

    ---

    photons_app:
      extra_files:
        after:
          - filename: "{config_root}/secrets.yml"
            optional: true
        before:
          - filename: "/path/to/file/you/want/loaded/before/this/one.yml

All the files that get loaded will be merged together and treated as if they
were one python dictionary using
`Option Merge <https://delfick-project.readthedocs.io/en/latest/api/option_merge/index.html>`_

Interactor options
------------------

You have available to you ``interactor`` options at the root of your
configuration:

.. code-block:: yaml

    interactor:
      host: localhost

      port: 6100

      cookie_secret: secret_for_secure_cookies

      database:
        uri: "sqlite:///{config_root}/interactor.db"

      animation_presets:
        # These appear as options when you choose to animate tiles
        scrolling:
          - animation: tile_nyan
            options:
              num_iterations: 1
          - animation: tile_pacman
            options:
              num_iterations: 2
          - animation: tile_marquee
            options:
              num_iterations: 1
              text: THE FUTURE IS INTIMATE
              text_color:
                hue: 240
                saturation: 1

Photons options
---------------

You also have available options to your from photons.

For example, if your devices are on a particular subnet:

.. code-block:: yaml

    ---

    targets:
      lan:
        type: lan
        options:
          default_broadcast: 192.168.1.255

Or if you have many devices and discovery doesn't work so well, you have
`discovery options <https://delfick.github.io/photons-core/discovery.html>`_


Finally, there also
`options <https://delfick.github.io/photons-core/tile_animations.html#running-a-tile-animation-on-a-noisy-network>`_
for the tile animations.
