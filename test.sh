#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec run_interactor_pytest -q --ignore=$DIR/photons_interactor --ignore=$DIR/.photons-interactor "$@"
