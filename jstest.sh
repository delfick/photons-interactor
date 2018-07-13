#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if ! which npm > /dev/null; then
  echo "Couldn't find npm"
  exit 1
fi

exec $DIR/interact npm test --silent
