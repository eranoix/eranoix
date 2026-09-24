### Backend and systems engineer — Go, TypeScript, Kotlin

I build the unglamorous half: the part that has to keep working when a
dependency is down, a process dies mid-write, or two people click the same
button at once.

Most of what I work on runs in production and cannot be published. These are
sanitised or rebuilt versions, each one runnable in a single command.

---

**[linux-control-plane](https://github.com/eranoix/linux-control-plane)** · Go, Kotlin, ~45k LOC

A single static binary that replaces SSH, a terminal multiplexer, `docker`,
`crontab` and `journalctl` with one page — plus a native Android client with
its own VT terminal engine. Terminal sessions survive the server process
restarting, and render per client, so a phone looking in does not shrink the
desktop. The public demo runs the real binary behind a deny-by-default gate at
the single point every request passes through.

```
docker compose up   →   localhost:8765
```

**[llm-protocol-gateway](https://github.com/eranoix/llm-protocol-gateway)** · TypeScript

One endpoint, two protocols: OpenAI and Anthropic shapes translated in both
directions, streaming included. The part worth reading is the token refresh —
in-process single-flight, a cross-process file lock, and a re-read *inside* the
lock, which is the layer people skip and the reason a shared credential file
survives concurrency. Runs with no provider account at all.

**[durable-op-queue](https://github.com/eranoix/durable-op-queue)** · TypeScript

Exactly-once effects against systems you do not control. The hard case is the
window between *the provider applied the change* and *our row says so*: crash
there and a retry either charges twice or loses the work. So handlers must
answer whether **they** made the change or found it already done, and the queue
records the difference.

**[scheduling-engine](https://github.com/eranoix/scheduling-engine)** · TypeScript

Availability rules, recurrence and conflict-free booking. Days are not always
24 hours long, the 31st of a 30-day month is skipped rather than clamped, and
availability is advice while the write is the authority — the conflict check
lives inside the transaction, not in the code that ran a moment earlier.

**[offshore-competency-forms](https://github.com/eranoix/offshore-competency-forms)** · React, Vite

Competency paperwork with retrieval-augmented drafting under a strict contract:
one mode takes your writing voice and *no* facts from the retrieved passages,
the other may state nothing that is not in them. The failure worth preventing
is a confident sentence about a job that never happened.

---

**Working on:** Go · TypeScript · Kotlin + Compose · SQLite / Postgres · Docker ·
Linux · WebRTC · protocol translation · anything with a hard concurrency edge

**Open to:** remote backend and systems roles.
