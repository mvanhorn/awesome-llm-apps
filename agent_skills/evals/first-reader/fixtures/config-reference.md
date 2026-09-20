# retrycfg configuration reference

All options live in `retry.toml` at the repo root. Values shown are
defaults.

## retry.max_attempts

Integer, default `5`. Total tries including the first. Set to `1` to
disable retries entirely.

## retry.backoff

String, default `"exponential"`. One of `fixed`, `linear`,
`exponential`. Exponential doubles the delay each attempt starting
from `retry.base_delay_ms`.

## retry.base_delay_ms

Integer, default `250`. First delay in milliseconds. With exponential
backoff and 5 attempts the worst case wait is 3750 ms.

## retry.jitter

Boolean, default `true`. Adds up to 20% random jitter to every delay.
Disable only in tests that assert exact timing.

## retry.retry_on

List of strings, default `["timeout", "connection_reset"]`. HTTP status
codes may be given as strings: `"503"` retries on service unavailable.
Codes in the `4xx` range other than `408` and `429` are refused with a
config error at load time.

## Environment overrides

Every key can be overridden with `RETRYCFG_` variables:
`RETRYCFG_MAX_ATTEMPTS=3` beats the file. Overrides are read once at
startup; changing them at runtime has no effect.
