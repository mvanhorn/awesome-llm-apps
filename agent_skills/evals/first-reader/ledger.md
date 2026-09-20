# first-reader development ledger

What each test taught the skill, scandinavian-design style: feedback stays
feedback until it generalizes into a rule, and rules carry their provenance
so stale ones can be found and pruned. Dates are absolute.

## 26 Aug 2026: Round 1: fixtures, six readers, one rerun

The design bet was that the experience layer separates hollow from human
where the surface layer cannot. Round 1 tested it with two fixtures built
as opposites: `hollow-clean.md` (passes every anti-slop ban, commits to
nothing: portable share 1.0, zero costly signals) and `human-tells.md`
(full of surface "tells": em dashes, mirrored contrasts, a quotable
kicker: but staked and specific: portable 0.17, 9 numbers, 3 admissions).

**The bet held, on every instrument.**

- Skim gate: the skeptic bounced off hollow citing "numbers=NONE plus
  every paragraph opening as a truism," and committed to the outage piece
  because "an author indicting their own review is the rarest postmortem."
- Timed reads: the doc skeptic quit at chunk 2/4 ("the same post I have
  read a hundred times under other titles"). The outage skeptic finished
  at +2 and *checked the connection-pool math* unprompted. Neither reader
  flagged an em dash, a triad, or the kicker, because none of them broke
  the read. The false positive every humanizer commits did not occur.
- The sympathetic reader on hollow neither quit nor flattered: finished,
  kept three usable lines, verdict "a clean, well-phrased outline of
  things I already believed when I clicked; I would not forward it."
  So the needle is not sycophantic and not manufactured-negative.
- Recall: outage gist matched the intended thesis with the center of
  gravity aligned; doc recall surfaced that only one-line framings
  survived, "its life was in one-line framings rather than the
  demonstration it promised." That sentence is the whole case for the
  recall instrument.
- Reproducibility: an independent rerun of the doc skeptic quit at the
  same chunk (2/4) for the same class of reason. Readers agree on where.
- Miscast probe: a non-technical reader on the outage piece skimmed the
  Postgres math "without guilt" but finished on the confession spine.
  Divergence between casts localizes a problem to audience fit instead of
  the draft; this is how the orchestrator distinguishes casting errors.

**Bugs the deterministic suite caught, both fixed:**

- `signals.py` counted heading words as named entities (clean() now runs
  before the entity scan) and missed unit-bearing specifics like `v2.3`,
  `48MB`, `90-second`, which are exactly the costly kind. The number
  detector now counts any digit-bearing token.
- `feed.py` served a punctuation-less 500-word blob as a single chunk
  (transcripts and list dumps have no sentence boundaries). Hard
  word-count split added; a chunk can never exceed MAX_WORDS.

**Candidate rules that landed in SKILL.md or references from this round:**

- Quitting needed explicit permission and status ("quitting is a finding,
  not a failure; there is no reward for finishing") or readers finish out
  of assistant politeness. With the framing, quits happen and are the
  sharpest data in the run.
- The sympathetic persona needs a stake sentence with teeth ("your team
  will judge what you bring them"), otherwise wanting-it-to-be-good decays
  into rating it good.
- Reader prompts must be symmetric: no hint that the text might be slop,
  no hint that it might be great. The persona and patience budget are the
  only pressure. Both fixtures got identical framing and the transcripts
  still separated, which is the point.

## 26 Aug 2026: Round 2: cold end-to-end run

A writer agent produced a deliberately mixed draft (strong specific open,
generic marketing middle, partial recovery at the end) that the
orchestrator never saw; a fresh agent followed SKILL.md cold. Both persona
readers independently recovered the hidden construction from the feed
alone: the sympathetic reader logged "the brochure-copy middle sent me
from leaning-in to skimming," and the skeptic finished unconvinced because
the marketing middle displaced the two questions it needed answered (diff
noise, write-endpoint replay). The instrument reconstructed ground truth
it never saw.

The full run completed with five subagent readers and no solo fallback.
Its sharpest findings: both
personas and the skim scanner broke at the same sentence ("But Retracer
is more than a replay tool."), the recall agents reproduced the marketing
lines verbatim as the moment the voice changed, and the implied-author
pass located the seam to the word ("the word 'concretely' reads as the
first author apologizing for the second").

The reviewer returned five defects in the skill itself, all fixed:

- The altitude rule contradicted itself when the skim gate fails but the
  reads finish and recall passes. references/report.md now defines that
  as wounded-not-dead: report everything, lead with the gate, name which
  audience each result speaks for.
- Step 2 quietly contaminated the orchestrator (running skim.py shows
  draft fragments). SKILL.md now has the subagent run the script itself,
  or the output goes to a file the orchestrator never opens.
- The feed.py quit invocation was underspecified, and a finished reader's
  final line was labeled QUIT in the transcript. Syntax now spelled out;
  the final line of a finished read prints as FINAL.
- Nothing said when signals.py output was safe to read. SKILL.md now says
  only after the timed reads, because it quotes draft sentences.
- The admissions detector missed "our test data was a fantasy." Patterns
  widened, and SKILL.md now calls all counters floors to be confirmed in
  the reviewer's own read, never trusted at zero.


## 27 Aug 2026: Round 3: the Reading Room and the feedback loop

The report became a page. A hand-built prototype on the real MCP-article
run validated the design (margin notes, needle strip, lenses, replay),
and the author's first reaction produced three corrections that landed:
no invented codenames anywhere a person looks (flags now say "felt
misled here", not "the jolt"; "passage", not "chunk"), a how-this-was-
made fold explaining the 85-word passages and the no-lookahead rule, and
a two-way notes channel. The channel is the artifact self-publish
capability: notes live in the page's fb-state block, send republishes
the page, the republish wakes the building session. Proven live: a note
on passage 11 ("can you fix this") round-tripped from page to session to
an acted-on answer with no backend.

Productionized as `scripts/room.py` + `room_template.html`: builds from
raw sessions with deterministic fallbacks (auto-excerpts, hidden lenses)
and takes `room-annotations.json` for the curated layer (plain verdict,
reader-voiced excerpts, recall phrases, flags, opinions, and the
previous-run comparison line). Quit points render as a fold line with
everything after it dimmed for that reader. SKILL.md gained the live
narration rule (one plain line per reader event, never silence), the
cast-card-then-manifest step, and step 7: the room as the primary
delivery, with the republish-notification loop for acting on notes.
Ten new deterministic tests cover room.py, including the quit fold and
the lens-gating.

## 27 Aug 2026: Round 4: the product-sense reset

The author's verdict on the skill itself: "super complicated to use and
not a fun experience." Accurate. The engine was good and the interface
had become an operator's manual: casts, manifests, lenses, passage
vocabulary, contamination talk, four ways to edit a draft. The tell was
the author asking "how do I use this" twice and getting documentation
both times.

The reset, now in SKILL.md as "The user contract," which overrides
everything else in the file: the skill is two phrases and one page.
"review this" gets one starting line, silence, then three to six plain
sentences where every finding arrives with a suggested fix attached,
plus one link. "fix it" applies fixes; "again" re-runs and opens with
what changed. Paste is fine and blinding is the reviewer's problem;
jargon is banned from user-facing output; at most one intake question;
at most one mid-run message. The reviewer-versus-assistant hat
distinction is gone: findings always ship with fixes, the author
chooses.

The room matched: findings are now cards under the verdict with fix-it
and leave-it buttons that ride the existing notes channel, the reader
and lens controls collapsed behind one "more views" disclosure, and the
legend row died. room.py takes a findings list in the annotations.

Rule recorded with provenance: every instrument you add will try to
climb into the user's lap. The engine can be arbitrarily rich only if
the interface stays two phrases and one page.

## 30 Aug 2026: Round 5: Clarity ships, and it's the other chair

addyosmani/clarity (0.2.0) landed: the strongest editor-side writing
skill yet: substance-first doctrine, an interview mode that extracts the
author's real material, hard truth guardrails ([TK] instead of
fabrication), medium registers, and a blinded eval protocol with hard
gates on invented facts. Its prose_stats.py refuses to print a composite
score because their own composite came out inverted on a human control:
independent convergence with our no-scores rule.

Dissection verdict: not a competitor, the complement. Clarity is
criterion-based feedback (the editor's chair); first-reader is
reader-based feedback (the reader's chair). Clarity has zero reader
simulation, no attention or quit measurement, no memory test, no
behavioral diff; we have no interview mode, weaker truth guardrails on
the fix path, and a cruder register system. Adopted from it, with
credit: the ask-author fix class (a fix that needs the author's material
becomes a precise question, never invented content), the
never-strengthen-a-fact rule on applying fixes, and the hollow-verdict
interview handoff. Positioned in the README as complements.

Flagship experiment: running our blind readers on clarity's own
before/after sample essays to measure whether its rewrite changes reader
behavior: the comparison its JUDGE.md asks for and cannot run itself.

## 30 Aug 2026: The clarity cross-experiment

Ran four blind readers (an ML skeptic and a curious layperson, on each
draft, neutral filenames) over clarity's own how-ai-works before/after
samples. Result, in reader behavior: the rewrite works for its target
reader. On the before, the skeptic quit at chunk 2 of 6 ("pure
boilerplate, no author present") and the layperson finished knowing
nothing new ("smooth is not the same as understanding"). On the after,
the skeptic finished (though "only because it was short") and the
layperson got most of what they came for ("I could now explain training
vs validation, layers, why the output can be confidently wrong...
7/10").

Two findings clarity's own process could not produce: both blind
readers independently flagged the same trust-breaking moment in the
shipped after sample, a leaked editorial sentence ("The source draft
does not explain... so this rewrite should not pretend to"), which
reads to a real reader as scaffolding left in the copy; and both
readers still could not picture attention, the exact gap the rewrite
honestly declined to fill, which is the case for the interview step.
The editor's chair improved the piece; the reader's chair measured the
improvement and caught what the editor's chair shipped past. That is
the complementarity thesis, demonstrated on his own samples.

## 8 Sep 2026: Round 6: the readers stay, the fixes go

Three days of trying to make the page do more (fix-it buttons, tracked
changes, a notes channel back to the agent, a generated better draft)
ended with the author rejecting all of it: "just the edit option is not
making sense." The failure was structural, not cosmetic. Every fix path
put the skill in the writer's chair, where it competes with editor
skills and loses on voice, and it turned the page from a report into a
console with a server behind it, which broke the moment the harness
was not Claude Code.

Removed: serve.py, edits.py, revise.py, the notes tray, fix-it and
leave-it, "apply my notes", the human-reader invite. Kept and finished:
the skim gate, the served no-lookahead feed (text lives only in the
feed process; readers get a token, never a path), recall, the trust
ledger, the page as a plain report, and one new instrument, `ask.py`:
the readers persist in the run directory and can be consulted
afterwards, answering only from their own log. The user contract is now
five phrases: "review this", "ask S ...", "again", "quick read", and
paste.

Rule recorded: the readers say what happened to them and what would
have had to be true for it to go differently. They never say what to
write. The author owns every decision about the text.

## 8 to 9 Sep 2026: Five reads of one essay

The finished skill ran five times on the author's own 2,100-word essay
(a PM apprenticeship piece for X long-form), same two casts each time
(a second-year PM reading on a train; a staff PM deciding a headcount),
fresh minds each run, with the author revising between runs from the
readers' comments and "ask" answers alone.

What the strip showed, read to read: the skeptic quit at passage 9 of
18 on draft one. Draft two: finished, dips at 9 and 15 to 17. Draft
three: finished, one dip at 10 (the author's own route, "a proposal
from an outsider"). Draft four: finished, no negative passage. Draft
five: finished, one new dip at a rung that contradicted the piece's
best passage, repaired one passage later; the skeptic's verdict, "I
finished, which I do for maybe one in ten of these."

What held constant: the peak was the same passage in all five reads
for both readers, and both readers' recall preserved the same three
lines each time. The skim gate opened the piece all five times, but
the element that decided it moved from a single manager-addressed
sentence to the sample log once the log existed.

What the consult step did: asked "what would have kept you past
passage 9", the skeptic named the missing evidence ("one shown instance
would have done it") rather than a rewrite; the author wrote that
instance, and the dip disappeared on the next read. Asked why the
headline nearly lost them, the skimmer answered "the headline has an
audience with an opinion; the sentence that pulled me in has a reader
with a calendar." The author changed the title; the next skimmer read
it as "who trains my reports" instead of "AI eats jobs".

Cost per read: about eight minutes wall clock, three subagents plus
two recall agents. The reading converged by read four; read five
confirmed it. Rule recorded: when the peak, the recall, and the quit
points stop moving between reads, the skill has nothing left to say
and says so.
