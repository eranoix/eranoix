### Backend and systems engineer — Go, Kotlin, TypeScript, Python

I build the unglamorous half: the part that has to keep working when a
dependency is down, a process dies mid-write, or two people click the same
button at once. Nobody notices that work until it fails, which is most of why
I like it — done properly, it stays invisible.

I work remotely from Brazil, and have for years. Most of what I build runs in
production and cannot be published; what follows is sanitised or rebuilt, and
every one of them runs with a single command.

---

**[linux-control-plane](https://github.com/eranoix/linux-control-plane)** · Go, Kotlin · ~215k lines, ~300k with tests

This is the one I use every day. It administers my own server, and I built it
because administering a machine meant keeping a dozen tools in my head and an
SSH session open on each of them — `docker` here, `crontab` there, `journalctl`
somewhere else, and a folder of shell scripts I had to remember the arguments
to. Now it is one page, and one file to deploy: the whole front end is compiled
into the binary.

The part I am most attached to is the terminal. Sessions outlive the process
that serves them, so restarting the control plane does not kill a running job,
and reattaching replays the live screen instead of a blank one. Rendering is
per client — I kept opening the panel on my phone while a build ran on the
desktop, and the session kept collapsing to the phone's width. Two viewers of
the same session now each get output composed for their own screen.

The Android client is native, not a web view, with its own VT parser driving a
Compose renderer. That was the hardest single thing here, and the most fun.

```
docker compose up   →   localhost:8765
```

**[llm-protocol-gateway](https://github.com/eranoix/llm-protocol-gateway)** · TypeScript · SQL

One endpoint, two protocols: OpenAI and Anthropic request shapes translated in
both directions, streaming and tool calls included. I wrote it because I had
tools that spoke one dialect and a provider that spoke the other, and I did not
want to modify every tool.

It runs on my own machine and has for months. The part worth reading is the
token refresh: in-process single-flight, a cross-process file lock, and a
re-read of the file *inside* that lock. The re-read is the layer people skip,
and it is the reason a credential file shared between processes survives
concurrency instead of being clobbered by whichever refresh finished last.

Runs with no provider account at all — `MOCK_UPSTREAM=1` and the whole path,
locking included, exercises against a canned reply.

**[publication-gate](https://github.com/eranoix/publication-gate)** · Python

Every repository on this profile was produced by this one. I wrote it because I
had eleven private repositories full of work I wanted to show and could not:
production addresses, e-mail, client names, a phone number. Copying and running
`sed` works once; the second time, the private repo has moved on and you
re-sanitise from memory, and that is where things leak.

So it derives the public copy instead — and **refuses to publish** when a check
fails. Each gate exists because something got through: it reads the output tree
rather than the sources, because a minified bundle is a second copy that kept a
production address alive after the source was fixed; and it reads the file
*path*, because a directory name carried a tracker key while every file inside
it was clean.

The example ships leaking on purpose. The first run refuses, the README says
which line fixes it, and CI asserts that the refusal still happens — a tool
whose value is saying no has one interesting failure mode, which is going quiet.

**[offshore-competency-forms](https://github.com/eranoix/offshore-competency-forms)** · JavaScript, CSS, Python

Competency paperwork, filled and signed offshore. The constraint that shaped
everything is that it is used at sea, where the connection drops and does not
come back for a while: it installs as a PWA and runs from a single file with no
network at all.

The drafting is retrieval-augmented under a contract I care about. One mode
borrows your writing voice and **no** facts from the retrieved passages; the
other may state nothing that is not in them. The failure worth preventing is a
fluent, confident sentence about a job that never happened — in paperwork that
someone signs.

Print fidelity is arithmetic rather than eyeballing, and the checks read the
`.docx` that comes out instead of the screen that drew it.

**[durable-op-queue](https://github.com/eranoix/durable-op-queue)** · TypeScript

Exactly-once effects against systems you do not control — charge a card, create
a remote folder, send a statement.

The system this comes from runs in production and is not mine to publish, so
this is a smaller rebuild of the same problem, written from scratch. That is
also why it is small: it is the argument, not the product.

The hard case is the window between *the provider applied the change* and *our
row says so*. A process that dies in there leaves a completed effect our records
believe is still owed; retry and you charge twice, skip and you lose the work
silently. No amount of care in the calling code fixes it, because the calling
code is what died. So handlers have to answer a question the queue cannot answer
for them — did **I** make this change, or was it already there — and the queue
records the difference.

**[scheduling-engine](https://github.com/eranoix/scheduling-engine)** · TypeScript

Availability rules, recurrence, and booking that cannot double-book. Same
origin as the queue above: rebuilt small, from a system I cannot publish.

Most of the work is in the places where calendars lie. Days are not always 24
hours long, so a weekly appointment at 09:00 has to stay at 09:00 across a
daylight-saving change rather than drifting an hour. The 31st of a 30-day month
is skipped, not clamped to the 30th — clamping invents an appointment nobody
asked for, and it shows up as a stranger in someone's calendar.

And availability is advice while the write is the authority: the conflict check
runs inside the same transaction as the insert, not in the code that ran a
moment earlier and believed the slot was free.


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
