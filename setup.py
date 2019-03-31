from photons_interactor import VERSION

from setuptools import setup, find_packages

setup(
      name = "photons-interactor"
    , version = VERSION
    , packages = ['photons_interactor'] + ['photons_interactor.%s' % pkg for pkg in find_packages('photons_interactor')]
    , include_package_data = True

    , install_requires =
      [ "lifx-photons-core==0.12.1"
      , "tornado==5.1.1"
      , "SQLAlchemy==1.2.10"
      , "alembic==1.0.0"
      , "whirlwind-web==0.5.3"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.7"
        , "asynctest==0.10.0"
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
