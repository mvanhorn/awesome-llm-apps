#!/usr/bin/env python3
"""Deterministic tests for first-reader's bundled scripts (eval tier 2b).

Self-contained: builds fixtures in a tempdir, exercises skim/feed/signals/
recall, exits 0 on pass, 1 on first failure. No network, stdlib only.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / "first-reader" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
FAILED = []


def check(name, cond, detail=""):
    status = "ok" if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(name)


def run(script, *args, expect_fail=False):
    r = subprocess.run([sys.executable, str(SKILL / script), *map(str, args)],
                       capture_output=True, text=True)
    if expect_fail:
        return r
    if r.returncode != 0:
        check(f"{script} {args[0] if args else ''} exits 0", False, r.stderr[:200])
        sys.exit(1)
    return r


def main():
    hollow = FIXTURES / "hollow-clean.md"
    human = FIXTURES / "human-tells.md"

    # --- skim.py: the scanner view must not leak the full text -------------
    out = run("skim.py", human).stdout
    full = human.read_text()
    body_words = len(full.split())
    leaked = sum(1 for w in out.split() if len(w) > 3 and w in full)
    check("skim withholds most of the text", leaked < body_words * 0.55,
          f"leaked~{leaked}/{body_words}")
    check("skim shows heading", "# The outage was a for loop" in out)
    check("skim surfaces fixation numbers", "4,100" in out)
    check("skim states read time and screens", "phone screens" in out)

    # --- signals.py: fixtures must separate on the costly/portable axes ---
    sig = lambda f: json.loads(run("signals.py", f, "--json").stdout)
    h, d = sig(human), sig(hollow)
    check("hollow fixture is ~fully portable", d["portable_sentences"]["share"] >= 0.9,
          str(d["portable_sentences"]["share"]))
    check("hollow fixture pays no costly signals",
          d["costly"]["numbers"]["count"] == 0 and d["costly"]["first_person_sentences"] == 0)
    check("human fixture is mostly non-portable", h["portable_sentences"]["share"] <= 0.35,
          str(h["portable_sentences"]["share"]))
    check("human fixture pays costly signals",
          h["costly"]["numbers"]["count"] >= 5
          and h["costly"]["admissions_against_interest"]["count"] >= 1)
    check("unit-bearing specifics counted (v2.3, 48MB class)",
          sig(FIXTURES / "tiny.md")["costly"]["numbers"]["count"] >= 3)

    # --- feed.py: the arrow of time is actually enforced -------------------
    with tempfile.TemporaryDirectory() as td:
        s = Path(td) / "sess"
        start = run("feed.py", "start", human, "--session", s, "--persona", "t").stdout
        check("feed shows chunk 1 only", "CHUNK 1/" in start and "for loop" in start)
        check("feed shows remaining budget", "words remain" in start)
        n_chunks = int(start.split("CHUNK 1/")[1].split()[0])
        check("feed withholds later chunks",
              "Cheap question" not in start)  # the fixture's last line
        r = run("feed.py", "next", s, "--log", "hi", expect_fail=True)
        check("feed refuses trivial log entries", r.returncode != 0 and "REFUSED" in (r.stdout + r.stderr))
        r2 = run("feed.py", "next", s, "--log",
                 "needle=+1 expected postmortem, got confession; leaning in").stdout
        check("feed releases chunk 2 after a real log", "CHUNK 2/" in r2)
        run("feed.py", "quit", s, "--log", "needle=-2 persona is out of patience here, stopping")
        t = run("feed.py", "transcript", s).stdout
        check("transcript records quit point", "QUIT" in t and f"of {n_chunks} chunks" in t)
        q = run("recall.py", s).stdout
        check("recall bundle contains quiz and log", "SAYBACK" in q and "needle=+1" in q)
        check("recall bundle withholds unread draft text", "Cheap question" not in q)

    # --- feed.py served mode: no-lookahead as mechanism ---------------------
    with tempfile.TemporaryDirectory() as td:
        draft = Path(td) / "d.md"
        draft.write_text(("zebra " * 90).strip() + ".\n\n" + ("quokka " * 90).strip() + ".\n")
        run_dir = Path(td) / "run"
        ready = Path(td) / "ready.json"
        srv = subprocess.Popen([sys.executable, str(SKILL / "feed.py"), "serve", str(draft),
                                "--run", str(run_dir), "--readers", "a,b", "--dwell", "0.02",
                                "--ready-file", str(ready)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for _ in range(50):
                if ready.exists():
                    break
                time.sleep(0.1)
            addr = json.loads(ready.read_text())
            env_a = dict(os.environ, READER_FEED=addr["readers"]["a"])
            def rd(*a, env=env_a):
                return subprocess.run([sys.executable, str(SKILL / "feed.py"), *a],
                                      capture_output=True, text=True, env=env)
            on_disk = lambda: any("quokka" in f.read_text() or "zebra" in f.read_text()
                                  for f in run_dir.rglob("*") if f.is_file())
            check("served: nothing of the piece on disk before reading", not on_disk())
            s1 = rd("start").stdout
            check("served: start shows passage 1 only", "zebra" in s1 and "quokka" not in s1)
            s1b = rd("start").stdout
            check("served: a second start re-shows, never advances", "nothing advanced" in s1b and "quokka" not in s1b)
            r = rd("next", "--log", "needle=0 expected words, got words, nothing felt")
            check("served: advancing faster than a person could read is refused",
                  r.returncode != 0 and "too fast" in (r.stdout + r.stderr))
            time.sleep(2.2)
            r2 = rd("next", "--log", "needle=0 expected words, got words, nothing felt")
            check("served: after the dwell floor the next passage is released", "quokka" in r2.stdout)
            check("served: still nothing on disk while another reader is unfinished", not on_disk())
            bad = rd("start", env=dict(os.environ, READER_FEED=addr["base"] + "/notatoken"))
            check("served: an unknown token gets nothing", bad.returncode != 0 and "zebra" not in bad.stdout)
            rd("quit", "--log", "needle=0 final: the end, nothing more to say here")
            rd("close", "--admin", addr["admin"])
            time.sleep(0.5)
            check("served: close writes state.json in the layout room.py expects",
                  (run_dir / "a" / "state.json").exists() and (run_dir / "b" / "state.json").exists()
                  and len(json.loads((run_dir / "a" / "state.json").read_text())["chunks"]) == 2)
            t = rd("transcript", str(run_dir / "a")).stdout
            check("served: transcript reads back from the closed run", "FINAL" in t and "the end" in t)
        finally:
            srv.kill()

    # --- feed.py chunking sanity -------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        big = Path(td) / "big.md"
        big.write_text("word " * 500)  # one 500-word paragraph
        s2 = Path(td) / "s2"
        out = run("feed.py", "start", big, "--session", s2, "--persona", "t").stdout
        n = int(out.split("CHUNK 1/")[1].split()[0])
        check("oversized paragraphs are split into beats", n >= 3, f"chunks={n}")

    # --- room.py: the Reading Room builds from raw sessions ----------------
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)
        for name, logs in {
            "keen": ["needle=+2 expected setup, got a confession; leaning in",
                     "needle=+1 expected mechanism, got it; still reading",
                     "needle=+1 final: finished, satisfied with the close"],
            "bored": ["needle=0 expected news, got things I already knew; started skimming",
                      "needle=-2 quitting: nothing here I could not recite myself"],
        }.items():
            s = run_dir / name
            run("feed.py", "start", human, "--session", s, "--persona", name)
            run("feed.py", "next", s, "--log", logs[0])
            if len(logs) == 3:
                run("feed.py", "next", s, "--log", logs[1])
                run("feed.py", "next", s, "--log", "needle=+1 expected more, got the fix section")
                run("feed.py", "quit", s, "--log", logs[2])
            else:
                run("feed.py", "quit", s, "--log", logs[1])
        run("room.py", run_dir, "--out", run_dir / "room.html")
        page = (run_dir / "room.html").read_text()
        check("room renders every passage", page.count('class="chunk"') >= 3)
        check("room renders the quit fold line", "stopped here" in page and "never saw anything below" in page)
        check("room marks passages the quitter never saw", "data-unseen-" in page)
        check("room parses needles from raw logs", 'class="chip nm2"' in page and 'class="chip n2"' in page)
        check("room is a report: nothing to send, no notes channel", "fb-state" not in page and "sendNotes" not in page
              and "serve.py" not in page and 'onclick="decide' not in page)
        check("room hides lenses that lack data", 'id="lensMem"' not in page)
        check("room auto-excerpts strip the needle prefix",
              "expected setup, got a confession" in page and "needle=+2 expected setup" not in page)
        ann = run_dir / "room-annotations.json"
        ann.write_text(json.dumps({"memory_phrases": ["retry loop"],
                                   "flags": {"1": "best moment"},
                                   "verdict_lead": "One reader quit; one finished."}))
        run("room.py", run_dir, "--out", run_dir / "room2.html")
        page2 = (run_dir / "room2.html").read_text()
        check("annotations add the memory lens and flags",
              'id="lensMem"' in page2 and 'mark class="mem"' in page2 and "best moment" in page2)
        check("annotations set the verdict", "One reader quit; one finished." in page2)

        # --- ask.py: readers can be consulted from their own logs -----------
        (run_dir / "skim.txt").write_text("A listicle. Moving on. Decided by the title.")
        q = run("ask.py", run_dir, "keen", "what kept you reading past the first passage?").stdout
        check("ask: the bundle carries the reader's persona, log, and the question",
              "keen" in q and "expected setup, got a confession" in q and "what kept you reading" in q)
        check("ask: the bundle never carries the draft", "Cheap question" not in q and "for loop" not in q)
        check("ask: readers may not propose rewrites", "Never suggest rewrites" in q)
        qs = run("ask.py", run_dir, "skim", "what would have made you open it?").stdout
        check("ask: the skimmer answers from their decision alone", "Moving on" in qs and "never the full text" in qs)
        qa = run("ask.py", run_dir, "all", "did anything stick?").stdout
        check("ask: 'all' bundles every reader and the skimmer",
              qa.count("===== reader:") == 3 and "reader: skim" in qa)
        r = run("ask.py", run_dir, "nobody", "hi", expect_fail=True)
        check("ask: an unknown reader is an error, not an invention", r.returncode != 0 and "no reader" in r.stderr)

        # --- the page shows the skimmer's verdict, and no fixes ---------------
        ann.write_text(json.dumps({"verdict_lead": "v", "skim": {"commits": False, "said": "A listicle. Moving on."}}))
        run("room.py", run_dir, "--out", run_dir / "room-s.html")
        ps = (run_dir / "room-s.html").read_text()
        check("page: the skimmer's verdict is on the page", "the skimmer moved on" in ps and "A listicle. Moving on." in ps)
        check("page: the author is told the readers can be consulted", '"ask' in ps and "ask the skimmer" in ps)
        check("page: no suggested fixes anywhere", "SUGGESTED FIX" not in ps and "fix it" not in ps and "fcard" not in ps)

        # --- previous-run strip: revision reads as progress -----------------
        ann.write_text(json.dumps({"verdict_lead": "Again.",
                                   "previous": {"summary": "Last time one reader quit.",
                                                "run": str(run_dir)}}))
        run("room.py", run_dir, "--out", run_dir / "room-again.html")
        again = (run_dir / "room-again.html").read_text()
        check("re-run page draws last time's strip above this time's",
              'class="scrub prev"' in again and "last time (" in again
              and again.index('class="scrub prev"') < again.index('class="scrub" role="group"'))
        check("re-run page states what changed", "Since last time:" in again and "Last time one reader quit." in again)


    print()
    if FAILED:
        print(f"{len(FAILED)} failure(s): {FAILED}")
        sys.exit(1)
    print("all first-reader script tests passed")


if __name__ == "__main__":
    main()
