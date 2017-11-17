# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.3] - Unreleased
### Added
- TimeOrderMixin for models that have time_order columns
- Integration tests refer to `MYSQL_CONNECTION_URI` environment variable to connect to the DB
- This changelog

### Changed
- Moved common fixtures to conftest.py
- Renamed test_model to test_base
