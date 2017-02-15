## [1.3.0] - 2017-02-15
### Added
- Added Excel template report creation

### Changed
- Interface commands: now option for processing or just reporting

## [1.2.1] - 2016-08-09
### Added
- Added functionallity to add discriptions and tags to Security events

## [1.2.0] - 2016-08-08
### Added
- Methods to add elastic options
  - use elastic config file for complex configurations including using ssl certs
  - supply username and password (or just username and be prompted for password)
-  Functionality to ingest records from EVTXtract's extracted json

### Changed
- Now uses evtx.mapping.json file as the elastic mapping

## [1.0.1] - 2016-06-22
### Added
- pyinstaller spec for creating exe

### Fixed
- Mulitprocess issue that prevented creating exe with pyinstaller

### Changed
- Moved mapping to etc folder
