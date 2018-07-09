# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.7.1] - 2018-07-09
### Fixed
- `__version__` corrected
## [0.7] - 2018-07-09
### Added
- time_order helper function for API wrappers

## [0.6.1] - 2018-04-26
### Added
- Logger for JHHAlchemy migration

## [0.6] - 2018-02-01
### Removed
- Use `enum.Enum` instead of `jhhalchemy.model.BaseTypes`

## [0.5] - 2018-01-31
### Added
- `jhhalchemy.migrate` module with functions to create database locks and to safely run [Alembic](http://alembic.zzzcomputing.com/) upgrades

### Changed
- Moved tests to root directory so they won't be included in the package.

## [0.4] - 2018-01-11
### Changed
- Updated column definitions in Base and TimeOrder to correctly autogenerate alembic migrations

## [0.3] - 2017-11-21
### Added
- TimeOrderMixin for models that have time_order columns
- Integration tests refer to `MYSQL_CONNECTION_URI` environment variable to connect to the DB
- This changelog

### Changed
- Moved common fixtures to conftest.py
- Renamed test_model to test_base
