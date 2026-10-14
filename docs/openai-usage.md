# OpenAI usage summary

`openai_run_usage` is one log line at the end of `run_pipeline`, including when a stage fails or scoring stops for billing or the request cap. `estimated_usd` is an application estimate. It is not an invoice and it is not a spending cap.

`openai_usage_summary` is only the scoring client's chat totals. The run line is the process total for fit scoring, embeddings, and role classification.

## What the line contains

- `operations.fit`, `operations.embedding`, `operations.role`, and `operations.other` each have attempt, success, empty-follow-up, retry, exception, and missing-usage counts.
- Token fields stay empty until a response reports them. A missing field is not stored as zero. Cached tokens are not added into prompt tokens. Embedding totals use `usage.prompt_tokens` from the embeddings response. `usage.total_tokens` is not added again. The installed SDK's embedding response has no request id.
- `models` repeats those counts per model id returned by the API, or the id that was requested when the response has none.
- `response_ids` lists chat completion ids. Embedding calls increment `responses_without_id`.
- `reserved_attempts` is the number of HTTP attempts the process reserved. A refusal before the call is not an attempt.
- `estimated_usd` is set only when every recorded attempt has a known model rate and the token fields that rate needs. Otherwise it is null and `cost_complete` is false. With no attempts, the token and cost fields stay empty and `reserved_attempts` is 0.
- `cost_basis` is `estimate`. Rates are USD per 1,000,000 tokens, read on 2026-10-14 from the OpenAI pages for `gpt-5-mini` (input $0.25, cached input $0.025, output $2) and `text-embedding-3-small` ($0.02). The snapshot `gpt-5-mini-2025-08-07` uses the gpt-5-mini price. Reasoning tokens are not priced a second time.

## Comparing with the OpenAI dashboard

Match chat `response_ids` to request logs only when the account is retaining those logs. A day whose API logs are empty cannot be matched request by request.

Embedding calls from this SDK have no response id. Compare them as model-level `prompt_tokens` sums, not as individual requests.

The dashboard total for a day includes every program using the same API key. This line does not. Use it against the dashboard only for a window where this process was the only caller, and still treat the dashboard figure as the aggregate.

`missing_usage` counts responses that did not include a usage object. Those attempts are in `request_attempts` and are absent from the token sums, so the sums can be lower than the bill.

This line cannot prove an exact match to the dashboard.

## Bounded trial

`.github/workflows/trial.yml` is a separate manual workflow. It uses a runner-local SQLite file and does not receive the production database or Telegram credentials. One `run-once` process shares the OpenAI request ledger, so fit scoring, embeddings, and any other chat call in that process draw from `OPENAI_MAX_REQUESTS`.

One planned discovery query can still contact every configured job site. A request that has already been sent can still be billed. `estimated_usd` does not stop that.

OpenAI spend alerts only send a notification. A hard spend limit is different: the platform docs say it stops affected API traffic when tracked spend reaches the limit. Set a hard spend limit on the project before any trial dispatch. The prepaid balance is not that control, and this workflow does not check whether the limit is present.
