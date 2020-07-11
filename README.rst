Deprecated
==========

This project has been deprecated in favour of
https://photons.delfick.com/apps/interactor/index.html

Photons Interactor
==================

A `Photons <https://delfick.github.io/photons-core>`_ powered server for
interacting with LIFX lights over the lan.

The server allows us to do continuous discovery and information gathering so that
all commands are super fast.

You can find documentation at https://photons-interactor.readthedocs.io

Installation and use
--------------------

Make sure you have a version of python greater than python3.6 and do::

    $ python -m venv .interactor
    $ source .interactor/bin/activate
    $ pip install photons-interactor
    $ photons-interactor serve
    # go to http://localhost:6100

Running from a docker container
-------------------------------

If you're not on a mac and want to run via a docker container, you can say::

    $ docker run --name=photons \
        --detach \
        --restart=always \
        --net=host \
        -e TZ=Australia/Melbourne \
        delfick/photons-interactor:0.6.2

Replace `Australia/Melbourne` with the correct `TZ database name <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_ for your timezone.

If you want custom options then I suggest having a folder that looks like::

    custominteractor/
        interactor.yml
        Dockerfile

Where the docker file says::

   FROM delfick/photons-interactor:0.6.2
   ADD interactor.yml /project/interactor.yml

Then run::

    $ cd custominteractor
    $ docker build . -t custominteractor

    # Run the docker command mentioned above but say "custominteractor"
    # instead of "delfick/photons-interactor:0.6.2"

Also, with many thanks to @Djelibeybi this docker image will work on many
architectures, including a Raspberry Pi!

Running from the code
---------------------

You can find the code at https://github.com/delfick/photons-interactor

Once you've checked it out you can start the server by installing python3.6 or
above and running::
    
    $ pip3 install venvstarter
    $ ./interact server

You can also find a handy script for running commands against the server in
this repository called ``command``.

For example::
    
    $ ./command query '{"pkt_type": "GetColor"}'
    {
        "results": {
            "d073d5001337": {
                "payload": {
                    "brightness": 1.0,
                    "hue": 0.0,
                    "kelvin": 3500,
                    "label": "",
                    "power": 65535,
                    "saturation": 0.0
                },
                "pkt_name": "LightState",
                "pkt_type": 107
            }
        }
    }

The License
-----------

This work is licensed under NonCommercial-ShareAlike 4.0 International
(CC BY-NC-SA 4.0). The 'LIFX Colour Wheel' patented design as intellectual
property is used in this repository.

LIFX has granted permission to use the 'LIFX Colour Wheel' design conditional
on use of the (CC BY-NC-SA 4.0) license.

Commercial use the 'LIFX Colour Wheel' requires written consent from LIFX.
Submit enquiries to business@lifx.com

References:

* https://creativecommons.org/licenses/by-nc-sa/4.0/
* https://www.lifx.com/pages/legals
* https://www.lifx.com/pages/developer-terms-of-use
