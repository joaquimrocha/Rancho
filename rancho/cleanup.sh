#!/bin/sh

find -name \*.pyc -print0 | xargs -0 rm -fv
find -name \*.pyo -print0 | xargs -0 rm -fv
find -name \*~ -print0 | xargs -0 rm -fv


