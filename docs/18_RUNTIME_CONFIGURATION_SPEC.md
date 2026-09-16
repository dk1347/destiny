# Destiny — Runtime Configuration Specification

> Status: design baseline for the future API/Web MVP. No runtime configuration
> loader is introduced until an executable service exists.

## 1. Purpose

Destiny separates reproducible calculation rules from deployment-specific
settings and from a user's per-request choices. A single catch-all `.config`
file must not mix those three concerns.

## 2. Configuration classes

| Class | Examples | Storage | Version control |
| --- | --- | --- | --- |
| Calculation rule data | stems, branches, solar-term instants, relations | package JSON datasets | yes, versioned |
| Product defaults | default calculation-profile ID, enabled beta features, supported birth-year range | reviewed public service config | yes, versioned |
| Deployment secrets | API keys, database credentials, signing secrets | environment variables or secret manager | never |
| Per-request choices | birth data, unknown-time state, chosen profile, consent | request/result record | never treated as a server default |

## 3. Requirements for a future service config

1. A missing required secret fails startup with a clear non-secret error.
2. A production deployment rejects a default profile or enabled feature that
   refers to a non-`production_verified` rule dataset.
3. The resolved public config version and calculation-profile ID are preserved
   with every result for reproduction.
4. Changes to supported year range, profile default, or feature flags require
   review and a config version change; they are never silently inferred from
   the host environment.
5. Development/test may explicitly opt into pending datasets, but production
   cannot enable that escape hatch.

## 4. Explicit non-goals

- No secrets in repository files, test fixtures, logs, or result provenance.
- No user birth information in `.env` or a global server configuration.
- No multiprocessing setting inside the deterministic calculation core.
  Concurrency belongs to the future API worker or batch-job layer.

## 5. Initial MVP shape

When the API is introduced, use a small, validated public config plus a local
`.env` file excluded from Git. Start with one worker process and ordinary
request handling. Add queueing or multiple workers only after measured load or
batch work justifies it.
