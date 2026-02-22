<h2>📘 Deckline Documentation (v1.0)</h2>

<p>
  Deckline helps you finish a deck before a chosen <b>deadline</b> by converting the remaining work into a clear
  <b>daily target</b>.
  It shows what to do <b>today</b>, whether you’re on pace, and visualizes both <b>daily</b> and <b>overall</b>
  progress — directly inside Anki.
</p>

<hr>

<h3>✅ What Deckline Does</h3>
<ul>
  <li>Creates a <b>deadline-based study plan</b> per deck.</li>
  <li>Converts remaining work into a <b>stable daily quota</b>.</li>
  <li>Shows <b>daily progress</b> (Deck Overview + Review screen).</li>
  <li>Shows <b>overall progress</b> in the Deck Browser.</li>
  <li>Supports <b>skip weekends</b> (days off) and redistributes the workload.</li>
  <li><b>Vacation days</b> (Premium) — exclude custom days off and adjust targets automatically.</li>
  <li><b>7-day Stats dashboard</b> (Premium).</li>
</ul>

<h3>🚫 What Deckline Does NOT Do</h3>
<ul>
  <li><b>It does not change Anki scheduling</b> (FSRS/SM-2, ease, intervals, leeches, etc.).</li>
  <li><b>It does not force cards to appear.</b> It only reads your collection to compute targets and show feedback.</li>
</ul>

<hr>

<h3>🧠 Core Concepts</h3>

<h4>Deadline</h4>
<p>The date you want to be finished with the deck.</p>

<h4>Cut-off (Finish new cards)</h4>
<p>Deckline splits your plan into 2 phases:</p>
<ul>
  <li><b>Phase 1: NEW → Cut-off</b> (finish introducing new cards early)</li>
  <li><b>Phase 2: REVIEW → Deadline</b> (clean up young cards / stabilize reviews)</li>
</ul>
<p>This prevents a large pile-up of learning cards close to your deadline.</p>

<h4>Young vs. Mature</h4>
<p>
  Deckline follows Anki’s definition:
  cards become <b>mature</b> at an interval ≥ <b>21 days</b>. Everything below is <b>young</b>.
</p>

<h4>Done Today (important!)</h4>
<p>
  “Done today” is counted as <b>distinct cards reviewed today</b> (not the raw number of revlog actions).
  This avoids inflated counts from learning steps.
</p>

<hr>

<h3>🧩 Where You See Deckline (v1.0 UI)</h3>

<h4>1) Deck Browser — Card View (NEW in v1.0)</h4>
<p>
  Deckline now uses a modern <b>card layout</b> instead of a table.
  Each enabled deadline deck appears as a card.
</p>

<p><b>Each Deckline card shows:</b></p>
<ul>
  <li><b>Deck name</b> — click to open the deck’s Overview.</li>
  <li><b>Deadline</b> — “Today”, “in X days”, or “Overdue”.</li>
  <li><b>Phase</b> — NEW (Phase 1) or REVIEW (Phase 2).</li>
  <li><b>Pending</b> — remaining cards in the current pipeline (NEW + YOUNG, excluding suspended).</li>
  <li><b>Today</b> — “done today / target today”.</li>
  <li><b>Overall progress</b> — a progress bubble (0–100%).</li>
  <li><b>Status badge</b>:
    <ul>
      <li><b>ON TRACK</b> — today’s quota met</li>
      <li><b>BEHIND</b> — below today’s quota</li>
      <li><b>REST DAY</b> — excluded day (weekends/vacation)</li>
      <li><b>NOT STARTED</b> — start date is in the future</li>
    </ul>
  </li>
</ul>

<p><b>Subdecks:</b> all counts for a deck include its subdecks automatically.</p>

<hr>

<h4>Deckline Topbar (NEW in v1.0)</h4>
<p>
  Above the cards, Deckline includes a small topbar to quickly filter/sort what matters:
</p>
<ul>
  <li><b>Focus mode</b> — show only one deck</li>
  <li><b>Sort</b> — sort by Deadline / Progress / Today</li>
  <li><b>Behind filter</b> — show only decks that are behind</li>
  <li><b>Stats button</b> (Premium)</li>
</ul>

<hr>

<h4>2) Deck Overview Page: “Daily Deckline Progress” Card</h4>
<p>
  This appears on the deck’s Overview screen.
</p>
<ul>
  <li><b>Daily progress</b> = “done today / target today”</li>
  <li><b>Shows phase hint</b> (NEW → cutoff or REVIEW → deadline)</li>
  <li><b>Rest days</b> show as “Rest day (excluded)” and target 0</li>
</ul>
<p>You can toggle this card on/off in Settings → Feedback.</p>

<hr>

<h4>3) Review Screen: Bottom Progress Bar</h4>
<p>
  While reviewing, Deckline can show a thin progress bar at the bottom of the Anki window.
  This is also daily progress: <b>done today / target today</b>.
</p>
<ul>
  <li>Updates as you review.</li>
  <li>Has a tooltip with <b>Target</b> + phase hint.</li>
</ul>
<p>You can toggle this bar on/off in Settings → Feedback.</p>

<hr>

<h3>⚙️ Deckline Settings</h3>
<p>
  <b>Per-deck settings:</b> Deck Browser → right-click a deck → <b>Deadline</b><br>
  <b>Global settings:</b> Tools → <b>Deckline settings</b>
</p>

<h4>Tab — Deadline (per deck)</h4>
<ul>
  <li><b>Enable Deadline for “Deck Name”</b> — turns the plan on/off for that deck.</li>
  <li><b>Deck name</b> — custom display name (does not rename the deck in Anki).</li>
  <li><b>Start date</b> — if in the future, Deckline shows “NOT STARTED”.</li>
  <li><b>Cutoff</b> — when you want NEW cards done (moves with deadline).</li>
  <li><b>Deadline</b> — final date you want to be finished.</li>
</ul>

<h4>Tab — Optional (per deck)</h4>
<ul>
  <li>
    <b>Expected total cards</b> — planning override for decks that grow over time.
    Helps keep targets stable from day 1.
  </li>
  <li><b>Daily target override</b> — manually set today’s target (0 = auto).</li>
  <li><b>Skip weekends</b> — excludes Sat/Sun and redistributes workload.</li>
</ul>

<h4>Tab — Feedback (global)</h4>
<ul>
  <li><b>Show daily progress bar in deck overview</b></li>
  <li><b>Show daily progress bar in review screen</b></li>
  <li><b>Time estimate multiplier (new cards)</b> — used during NEW phase only.</li>
  <li><b>Time estimate multiplier (reviews)</b> — used during REVIEW phase only.</li>
</ul>

<p><b>Premium visuals (Premium):</b></p>
<ul>
  <li><b>Bar color mode</b>: Auto / Solid / Gradient</li>
  <li><b>Celebration animation</b> when you hit 100% for the first time that day</li>
</ul>

<h4>Tab — Vacation (Premium)</h4>
<p>
  Vacation days are excluded from target calculations (like weekends), and the plan is redistributed.
</p>
<ul>
  <li><b>Add day</b> — add one excluded day.</li>
  <li><b>Add range</b> — add an excluded date range.</li>
  <li><b>Remove selected</b> — remove selected entries.</li>
  <li><b>Clear</b> — clear the entire list.</li>
</ul>

<h4>Tab — ⭐ Premium</h4>
<ul>
  <li>Paste your premium code and click <b>Unlock</b>.</li>
  <li>Premium unlocks:
    <ul>
      <li><b>Stats dashboard</b> (7-day view)</li>
      <li><b>Unlimited deadlines</b></li>
      <li><b>Vacation days</b></li>
      <li><b>Custom progress colors</b></li>
      <li><b>Celebration animation</b></li>
    </ul>
  </li>
</ul>

<hr>

<h3>📈 How Targets Are Calculated (Simple)</h3>
<ol>
  <li>
    <b>Pick the phase</b>:
    <ul>
      <li>If today is before cut-off and there are NEW (or planned new) cards → focus on <b>NEW</b>.</li>
      <li>Otherwise → focus on <b>REVIEW</b> (young + remaining new).</li>
    </ul>
  </li>
  <li><b>Exclude rest days</b> (skip weekends + vacation days).</li>
  <li><b>Compute today’s quota</b> with a stable “constant quota” approach.</li>
  <li><b>Done today</b> is distinct cards reviewed (or “new cards started today” during Phase 1).</li>
  <li>
    <b>Status badge</b>:
    <ul>
      <li>ON TRACK if done ≥ target</li>
      <li>BEHIND otherwise</li>
      <li>REST DAY if excluded</li>
      <li>NOT STARTED if start date is in the future</li>
    </ul>
  </li>
</ol>

<hr>

<h3>❓ FAQ</h3>

<h4>Is the progress indicator daily or total?</h4>
<ul>
  <li><b>Daily</b>: Overview card + Review bottom bar (today vs today’s target).</li>
  <li><b>Total</b>: Deck Browser progress bubble (overall toward finishing).</li>
</ul>

<h4>Does Deckline change FSRS or Anki’s scheduling?</h4>
<p>No. Deckline does not modify scheduling. It only reads your data to show targets and progress.</p>

<h4>Do subdecks count?</h4>
<p>Yes — targets and “done today” include subdecks automatically.</p>

<hr>

<h3>🛠️ Troubleshooting</h3>
<ul>
  <li>
    <b>Daily Deckline Progress card is missing</b><br>
    Check Settings → Feedback → “Show daily progress bar in deck overview”.
  </li>
  <li>
    <b>Review progress bar not visible</b><br>
    Enable it in Settings → Feedback → “Show daily progress bar in review screen”.
  </li>
  <li>
    <b>Targets look wrong</b><br>
    Double-check your deadline, cutoff, skip weekends, and vacation days.
    If your deck grows over time, consider using <b>Expected total cards</b>.
  </li>
</ul>

<hr>

<h3>🧹 Managing Plans</h3>
<ul>
  <li><b>Edit a plan</b>: Deck Browser → right-click deck → Deadline</li>
  <li><b>Clear plans</b>: Deck Browser → right-click deck → Clear</li>
</ul>

<hr>

<h3>📌 Quick Tips</h3>
<ul>
  <li>Set your <b>cut-off</b> a few days before the deadline (e.g., 5–10 days).</li>
  <li>If you add/import cards over time, use <b>Expected total cards</b>.</li>
  <li>Use <b>Skip weekends</b> + <b>Vacation</b> to match real life.</li>
  <li>Use the Review bar to know exactly when you’re “done for today”.</li>
</ul>
