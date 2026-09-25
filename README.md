### Backend and systems engineer — Go, Kotlin, TypeScript, Python

I like the problems that only appear after something else has already gone
wrong. The card charged twice because a process died at the wrong second. The
two people who booked the same slot four seconds apart. The terminal session
that vanishes because somebody restarted the server it was running on. Most of
what I have built is some version of making those not happen.

I run my own server, and a fair amount of what I know came from having to fix
it myself at a bad hour. The first project below started exactly there — I was
tired of holding four tools in my head to answer one question.

I work remotely from Brazil, and have for years. Nearly everything I build runs
in production and is not mine to publish, so these are sanitised copies or
smaller rebuilds of the same problems. Each one runs with a single command, and
each one starts by saying what it was built for before it says how it works.

---

**[linux-control-plane](https://github.com/eranoix/linux-control-plane)** · Go, Kotlin · ~215k lines, ~300k with tests

Something breaks on a server at eleven at night. You SSH in, and then you need
`docker ps` in one place, `journalctl -u` in another, `crontab -l` somewhere
else, and a deploy script whose arguments you never remember. Every answer is
in a different tool, and you are holding all of them in your head at once.

I got tired of that, so I built one page that does it: containers, logs,
scheduled jobs, files, disks, deploys, alerts. It ships as a single binary with
the entire front end compiled inside it, which means deploying is copying one
file, and there is no Node, no nginx config, nothing else to keep alive.

The terminal is the part I am most attached to, and it came from a specific
annoyance: I would start a long job on my laptop, open the panel on my phone to
check on it, and the session would shrink to the phone's width — ruining the
view on the desktop I had left it on. Sessions now outlive the server process,
so restarting the panel does not kill a running job, and each viewer gets the
screen composed for their own window.

The Android client is native, with its own VT parser driving a Compose
renderer instead of a web view wrapped around the same page. It was the hardest
thing here and the most fun.

```
docker compose up   →   localhost:8765
```

**[llm-protocol-gateway](https://github.com/eranoix/llm-protocol-gateway)** · TypeScript · SQL

I had a handful of tools that spoke one provider's API and an account with a
provider that spoke a different one. The options were to patch every tool, or
to put something in the middle that translates. I put something in the middle.

It accepts either request shape on one endpoint and answers in the shape you
asked for — streaming, tool calls and image parts included, in both directions.
It has run on my own machine for months.

The part worth opening is the token refresh, because that is where a shared
credential quietly breaks. Several processes notice the token expired at the
same moment, all of them refresh, and the last writer wins — leaving the others
holding a token that was already replaced. The fix is three layers: single
flight inside the process, a lock between processes, and a re-read of the file
*inside* that lock. The re-read is the one people skip, and it is the one that
makes the difference.

You can run the whole thing with no provider account at all.

**[publication-gate](https://github.com/eranoix/publication-gate)** · Python

I had eleven private repositories full of work I was proud of and could not
show anybody. Not because of anything clever — because of production addresses,
e-mail, client names, a phone number, all sitting in the code. "I built this,
but I can't show you" is a sentence I have said in interviews, and it is worth
nothing.

Copying the repo and running `sed` over it works exactly once. A month later
the private version has moved on, you re-sanitise from memory, and that is when
something gets through. So this derives the public copy instead, repeatably —
and **refuses to publish** when a check fails.

Every gate here exists because something already got past me. It reads the
output tree rather than the sources, because a minified bundle is a second copy
that kept a production address alive after I had fixed the source. It reads the
file *path* as well as the content, because a directory name carried a tracker
key while every file inside it was clean.

The example ships leaking on purpose: the first run refuses, the README says
which line fixes it, and CI asserts the refusal still happens. A tool whose
whole value is saying no has one interesting way to fail, and that is going
quiet.

Every repository on this profile was produced by it.

**[offshore-competency-forms](https://github.com/eranoix/offshore-competency-forms)** · JavaScript, CSS, Python

Someone finishes a job offshore and now has to write it up: what the task was,
what they did, and the evidence that they are competent to have done it. It is
long, the wording is formulaic, and it has to be right, because a person signs
it and someone else audits it later.

Two things make it harder than paperwork usually is. The first is the
connection: on a vessel it drops and does not come back for a while, so the app
installs to the phone and runs from a single file with no network at all. The
second is that the finished document has to come out looking exactly like the
official form — so print fidelity is computed, not eyeballed, and the tests
read the `.docx` that comes out instead of the screen that drew it.

It will help you write, under a rule I care about: one mode borrows your
writing voice and takes **no** facts from the reference material, the other may
state nothing that is not in it. The thing worth preventing is a fluent,
confident sentence about a job that never happened, in a document somebody
signs.

**[durable-op-queue](https://github.com/eranoix/durable-op-queue)** · TypeScript

You charge a customer's card through somebody else's API. The charge goes
through. Your process dies before it can write down that it went through.

Now your records say the money is still owed. Retry and you charge them twice;
skip it and you lose the work quietly, and nobody finds out until someone
reconciles the books months later. No amount of care in the calling code fixes
this, because the calling code is the thing that died.

So the handler has to answer a question the queue cannot answer for it — did
**I** make this change, or did I find it already done — and the queue records
the difference. Attempts are kept as separate rows, so "failed four times and
then worked" stays distinguishable from "worked", and the database, not the
application, is what refuses a duplicate.

The system this comes from runs in production and is not mine to publish, so
this is a smaller rebuild of the same problem, written from scratch. That is
also why it is small: it is the argument, not the product.

**[scheduling-engine](https://github.com/eranoix/scheduling-engine)** · TypeScript

A shop takes appointments. Someone books Tuesday at nine, and four seconds
later so does someone else, and now two people arrive for the same slot and
somebody has to make an apologetic phone call. That is the failure this exists
to make impossible.

It turns opening hours and exceptions into actual bookable slots, expands
appointments that repeat, and writes a booking that cannot collide with
another. Rescheduling and cancelling work from a link, with no account and no
password, because someone booking a haircut is not going to create one.

Most of the work is in the places where calendars lie. Days are not always 24
hours long, so a weekly appointment at 09:00 has to still be at 09:00 after the
clocks change rather than drifting an hour. The 31st of a 30-day month is
skipped rather than clamped to the 30th — clamping invents an appointment
nobody asked for, and it turns up as a stranger in someone's calendar.

And availability is only advice: the check that matters runs inside the same
transaction as the insert, not in the code that ran a moment earlier and
believed the slot was free. Same origin as the queue above, rebuilt small.


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
