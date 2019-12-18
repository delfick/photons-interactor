from photons_interactor import VERSION

from setuptools import setup, find_packages

# fmt: off

setup(
      name = "photons-interactor"
    , version = VERSION
    , packages = ['photons_interactor'] + ['photons_interactor.%s' % pkg for pkg in find_packages('photons_interactor')]
    , include_package_data = True

    , python_requires = ">= 3.6"

    , install_requires =
      [ "delfick_project==0.7.0"
      , "lifx-photons-core==0.24.3"
      , "tornado==5.1.1"
      , "SQLAlchemy==1.3.3"
      , "alembic==1.0.0"
      , "whirlwind-web==0.6"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.7"
        , "asynctest==0.12.2"
        , "nose"
        , "mock"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'photons-interactor = photons_interactor.executor:main'
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
    )

# fmt: on
