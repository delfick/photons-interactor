from photons_interactor import VERSION

from setuptools import setup, find_packages

# fmt: off

setup(
      name = "photons-interactor"
    , version = VERSION
    , packages = find_packages(include="photons_interactor.*", exclude=["tests*"])
    , include_package_data = True

    , python_requires = ">= 3.6"

    , install_requires =
      [ "delfick_project==0.7.3"
      , "lifx-photons-core==0.25.0"
      , "tornado==5.1.1"
      , "SQLAlchemy==1.3.3"
      , "alembic==1.3.2"
      , "whirlwind-web==0.6"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti==2.0.0"
        , "asynctest==0.12.2"
        , "pytest==5.3.1"
        , "alt-pytest-asyncio==0.5.1"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'photons-interactor = photons_interactor.executor:main'
        , 'run_interactor_pytest = photons_interactor:run_pytest'
        ]
      , "lifx.photons": ["interactor = photons_interactor.addon"]
      }

    # metadata for upload to PyPI
    , url = "http://github.com/delfick/photons-interactor"
    , author = "Stephen Moore"
    , author_email = "delfick755@gmail.com"
    , description = "A server for interacting with LIFX lights over the LAN"
    , license = "cc-by-nc-sa-4.0"
    , keywords = "lifx photons"
    , long_description = open("README.rst").read()
    )

# fmt: on
