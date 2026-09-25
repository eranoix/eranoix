### Backend and systems engineer — Go, Kotlin, TypeScript, Python

**Remote from Brazil. Open to backend and systems roles.** · [arthurrhuan39@gmail.com](mailto:arthurrhuan39@gmail.com)

I build the part that has to hold when something else has already failed.

---

### Things that broke, and what I built about them

**A minified bundle kept a production address alive after I had already fixed
the source.** The bundle was a second copy of that source, and the scanner was
only reading sources. → [publication-gate](https://github.com/eranoix/publication-gate)
reads the *output* tree, and the file path as well as the content — a directory
name once carried a ticket key while every file inside it was clean.

**Restarting the panel killed whatever was running in it.**
→ [linux-control-plane](https://github.com/eranoix/linux-control-plane) detaches
terminal sessions from the process that serves them, so a restart costs you
nothing and reattaching replays the live screen.

**Opening that panel on my phone shrank the session on my desktop.**
→ Rendering is per client now: two people watching one session each get output
composed for their own window.

**Two processes noticed a shared token had expired at the same moment, both
refreshed, and the last writer won.**
→ [llm-protocol-gateway](https://github.com/eranoix/llm-protocol-gateway):
single-flight inside the process, a lock between processes, and a re-read of the
file *inside* that lock. The re-read is the layer people skip.

**A process died between the charge going through and the record of it.**
Retry and you charge twice; skip it and the work is lost quietly.
→ [durable-op-queue](https://github.com/eranoix/durable-op-queue): the handler
has to report whether **it** made the change or found it already done, and the
database, not the application, refuses the duplicate.

**Two people booked the same slot four seconds apart**, because the check that
said it was free had run a moment earlier.
→ [scheduling-engine](https://github.com/eranoix/scheduling-engine) runs that
check inside the same transaction as the insert.

---

### The six

- **[linux-control-plane](https://github.com/eranoix/linux-control-plane)** — Linux server administration in one binary, plus a native Android client with its own VT terminal engine · Go, Kotlin · ~215k lines
- **[publication-gate](https://github.com/eranoix/publication-gate)** — derives a public repository from a private one, and refuses to publish when a check fails · Python
- **[llm-protocol-gateway](https://github.com/eranoix/llm-protocol-gateway)** — OpenAI and Anthropic shapes on one endpoint, both directions, streaming included · TypeScript, SQL
- **[offshore-competency-forms](https://github.com/eranoix/offshore-competency-forms)** — signed paperwork written at sea, where the connection drops and does not come back · JavaScript, Python
- **[durable-op-queue](https://github.com/eranoix/durable-op-queue)** — exactly-once effects against systems you do not control · TypeScript
- **[scheduling-engine](https://github.com/eranoix/scheduling-engine)** — availability, recurrence and booking that cannot collide · TypeScript

I run my own server, and a fair amount of what I know came from having to fix it
myself at a bad hour — the first project above started exactly there. Nearly
everything else I build runs in production and is not mine to publish, so these
are sanitised copies or smaller rebuilds. Each runs with a single command, and
each README starts with the problem before it gets to the feature list.

---

### Languages, and where they actually are

Sixteen, counted by GitHub across the six repositories above — not a list of
things I have read about. Every figure below is what `api.github.com/repos/…/languages`
returns for a public repo, so it can be checked without taking my word for it.
The link goes to the code.

| | Where | What it does there |
|---|---|---|
| **Go** | [control-plane](https://github.com/eranoix/linux-control-plane) | 65 packages, almost all of it bare `net/http`. 45% of that repo |
| **Kotlin** | [control-plane](https://github.com/eranoix/linux-control-plane/tree/main/android) | Android client: Compose UI and a VT terminal engine |
| **TypeScript** | [gateway](https://github.com/eranoix/llm-protocol-gateway) · [queue](https://github.com/eranoix/durable-op-queue) · [scheduling](https://github.com/eranoix/scheduling-engine) | Strict mode: one gateway service and two libraries |
| **JavaScript** | [control-plane](https://github.com/eranoix/linux-control-plane) · [forms](https://github.com/eranoix/offshore-competency-forms) | Alpine panel, React app, and browser tests driven over CDP |
| **SQL** | [gateway](https://github.com/eranoix/llm-protocol-gateway/tree/main/src/storage/migrations) · [queue](https://github.com/eranoix/durable-op-queue/blob/main/src/schema.ts) | Schema by hand — including the unique index the queue's guarantee rests on |
| **HTML / CSS** | [control-plane](https://github.com/eranoix/linux-control-plane) · [forms](https://github.com/eranoix/offshore-competency-forms) | One Alpine template *is* the whole panel; the hand-written CSS is the forms app's print-exact sheets — the panel's is generated Tailwind, and does not count |
| **Python** | [publication-gate](https://github.com/eranoix/publication-gate/tree/main/lib) · [control-plane](https://github.com/eranoix/linux-control-plane/tree/main/scripts) · [forms](https://github.com/eranoix/offshore-competency-forms/blob/main/worker/ocr.py) | The publication pipeline and its gates; document OCR; a VT session replayer |
| **C++** | [control-plane](https://github.com/eranoix/linux-control-plane/tree/main/android/terminal-engine/src/main/cpp) | JNI bridge from Kotlin into a native VT parser |
| **Shell** | [control-plane](https://github.com/eranoix/linux-control-plane/tree/main/scripts) · gateway · forms | 40 build, release and test harnesses; a credential backup under `flock` |

Plus the build and config layer, which is real work even when it does not look
like a language: Gradle Kotlin DSL (a 17-module composite build), Dockerfile,
Makefile, CMake, Android XML, Go templates.

The percentages are honest in both directions. The vendored copies of Monaco,
xterm.js, zstd and HDiffPatch that ship in-tree are marked as third-party and
excluded — that is 19 MB of JavaScript and 2.3 MB of C I do not claim.

---

**Day to day:** Go · Kotlin + Compose · TypeScript · Python · JavaScript · SQL ·
Bash · C++ at the JNI boundary · HTML and hand-written CSS · Gradle · Docker ·
Linux · SQLite and Postgres · WebRTC

**Drawn to:** protocol translation, idempotency, time zones and recurrence,
terminal internals — anything with a hard concurrency edge or a contract that
has to hold while something else is failing.

**Open to:** remote backend and systems roles. If you want to see how I think
before you talk to me, the comments in these repositories say which defect each
decision came from.
