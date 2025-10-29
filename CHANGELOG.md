# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release of the Microservices Framework
- Complete documentation structure with 200+ markdown files
- Framework-as-Submodule architecture pattern
- Improved Hybrid Approach implementation
- Support for FastAPI, Aiogram, AsyncIO workers
- PostgreSQL and MongoDB data services
- RabbitMQ event-driven architecture
- Redis caching and session management
- Docker Compose configurations for dev/prod
- AI agent workflow documentation
- 4 maturity levels (PoC, Development, Pre-Production, Production)
- Comprehensive atomic documentation modules
- GitHub templates for issues and pull requests
- Security policy and code of conduct
- MIT License for open source usage

### Security
- Added SECURITY.md with vulnerability reporting guidelines
- Configured .gitignore for sensitive data protection
- Implemented security best practices documentation

### Documentation
- 172 atomic documentation files covering all aspects
- AI navigation matrix for 7-stage workflow
- Complete architecture guide
- Service naming conventions
- Template usage guide
- Troubleshooting guide

## [1.0.0] - 2024-10-29

### Added
- First stable release
- Production-ready framework
- Complete test coverage requirements
- CI/CD pipeline templates
- Monitoring and observability stack
- Multi-environment support

### Changed
- Updated Python version requirement to 3.11+
- Improved documentation structure
- Enhanced error handling patterns

### Fixed
- Coverage command paths (--cov=src)
- Relative link resolution in documentation
- Template naming consistency

## [0.9.0] - 2024-10-15 (Pre-release)

### Added
- Beta version with core functionality
- Basic service templates
- Initial documentation

### Known Issues
- Some observability docs marked as TODO
- Testing documentation incomplete

---

## Version History

- **1.0.0** (2024-10-29): First stable public release
- **0.9.0** (2024-10-15): Beta pre-release
- **0.1.0** (2024-09-01): Initial development

## Upgrade Guide

### From 0.9.x to 1.0.0
1. Update Python to 3.11+ if needed
2. Review breaking changes in service naming
3. Update coverage commands from `--cov=services` to `--cov=src`
4. Regenerate service templates if customized

## Deprecations

### Deprecated in 1.0.0
- Old service naming convention (will be removed in 2.0.0)
- Direct database access patterns (use HTTP-only data services)

## Contributors

Thanks to all contributors who helped shape this framework!

[unreleased]: https://github.com/yourusername/doc4microservices/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/doc4microservices/releases/tag/v1.0.0
[0.9.0]: https://github.com/yourusername/doc4microservices/releases/tag/v0.9.0