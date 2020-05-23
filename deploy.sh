#!/usr/bin/env bash
python setup.py sdist
twine upload --repository-url https://pypi.fury.io/jawbonehealth/ -u $FURY_TOKEN -p '' dist/*
