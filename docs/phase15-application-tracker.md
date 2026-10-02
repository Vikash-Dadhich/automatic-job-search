# Phase 15 application tracker

The job row answers where a posting sits in the agent workflow. The application row answers what happened to an actual application. Discovery, scoring, shortlist, and portfolio allocation do not create an application.

## When a row is created

A row is created only when one of these happens:

- Workday pre-fill reaches the review screen. The state is `in_progress`. `submitted_at` stays empty.
- A person approves and the submitter reports that the application was submitted. The state is `submitted`.
- A person chooses manual takeover, or submit is blocked, or pre-fill hits a blocker. The state is `manual_review`. That is not a submission.
- A submitted job is already in the database with no application row. Startup backfill creates one from `decided_at`. It does not invent a separate start event. It copies `outcome` only when the job already has one.

Discarding a review card creates nothing. If a pre-fill row already exists, discard marks it `withdrawn`.

There is one application per job. Repeating the same action does not add another row or another event of the same type.

## States and outcomes

The application state is `in_progress`, `submitted`, `manual_review`, or `withdrawn`.

The outcome stays the existing vocabulary: `ghosted`, `screening`, `interview`, `rejected`, `offer`. It is stored on the application only after the job is `submitted`. The current outcome and its time are on the row. Each distinct outcome is also an event, and a later outcome does not erase the earlier event or its time.

`Job.status` is still the workflow. The tracker does not change it. `Job.outcome` is still what the Telegram outcome button writes. The tracker copies that fact and keeps the history the job row does not keep.

## Method and time

`workday` means the posting is a Workday application. Anything else is `manual`. Times are UTC. The first `submitted_at` is not replaced when the pipeline runs again.

Version `phase15-v1` is stored on the application row.

## What this is not

It does not score, rank, or learn. Outcomes do not change fit, priority, eligibility, the shortlist, or portfolio allocation. That is Phase 16, and it is not implemented.
