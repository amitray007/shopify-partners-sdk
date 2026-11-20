# Changelog

## Unreleased

This release moves the SDK to Partner API 2026-10 and contains breaking changes. See
"Migrating to API 2026-10" in the README for the full list.

### Added

- Support for Partner API versions 2026-01, 2026-04, 2026-07, 2026-10 (default), 2027-01,
  and `unstable`. The SDK bundles each version's schema.
- Schema validation: queries and mutations are checked before they are sent, with
  "Did you mean ...?" suggestions in `SchemaValidationError`.
- `client.paginate()` to iterate over every node of a connection.
- Credentials and settings from `SHOPIFY_PARTNERS_*` environment variables or a `.env` file.
- Enums for the 2026-10 `events` query and subscription types.

### Changed

- GraphQL variable types come from the schema. Enum and input-object arguments now work.
- Mutations are not retried after a timeout, connection error, or 5xx response.
- Connection edges parse into the model named by `__typename`.
- Money amounts keep every decimal digit when sent.
- Python 3.11 or later is required. Earlier releases did not import on Python 3.9.

### Removed

- Conversations, jobs, and messages (removed from the Partner API).
- API versions 2024-10 to 2025-07.
- The `shopify_partners_sdk.pagination` package, which raised `ImportError` on import.
- Enum values and model fields that the API does not have.

### Fixed

- The client raised `TypeError` when INFO logging was enabled.
- Settings validators crashed, and environment variables were ignored.
- App event models required an `id` the API never returns.
- The rate limiter's `try_acquire()` did not consume a token.
- `RetryHandler(max_attempts=0)` retried three times.
- Retry-After values are capped at the maximum backoff delay.
