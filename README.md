<h2>📘 Deckline Documentation (v1.2)</h2>

<p>
  Deckline helps you finish a deck before a chosen <b>deadline</b> by converting remaining work into a clear
  <b>daily target</b>.
  It shows what to do <b>today</b>, whether you are on pace, and how your progress looks — directly inside Anki.
</p>

<hr>

<h3>✅ What Deckline does</h3>
<ul>
  <li>Creates a <b>deadline-based study plan</b> per deck.</li>
  <li>Converts remaining work into a <b>stable daily quota</b>.</li>
  <li>Shows <b>daily progress</b> on Deck Overview and in the Review screen.</li>
  <li>Shows <b>overall progress</b> in the Deck Browser.</li>
  <li>Supports <b>skipping weekends</b> (rest days) with automatic workload redistribution.</li>
  <li>Supports <b>expected total cards</b> to keep targets stable for growing decks.</li>
  <li><b>Premium:</b> Stats (Chart + Heatmap), streaks, vacation days, custom colors, and celebration animation.</li>
</ul>

<h3>🚫 What Deckline does not do</h3>
<ul>
  <li><b>Does not change Anki scheduling</b> (FSRS/SM-2, ease, intervals, leeches, etc.).</li>
  <li><b>Does not force cards to appear.</b> It only reads collection data to compute targets and feedback.</li>
</ul>

<hr>

<h3>🧠 Core concepts</h3>

<h4>Deadline</h4>
<p>The date you want to be done with a deck.</p>

<h4>Cut-off (finish new cards)</h4>
<p>Deckline splits planning into two phases:</p>
<ul>
  <li><b>Phase 1: NEW → Cut-off</b> (finish introducing new cards early)</li>
  <li><b>Phase 2: REVIEW → Deadline</b> (clean up young cards and stabilize reviews)</li>
</ul>
<p>This helps prevent a large learning-card pileup near your deadline.</p>

<h4>Young vs Mature</h4>
<p>
  Deckline follows Anki's definition: cards become <b>mature</b> at interval ≥ <b>21 days</b>.
  Everything below that is <b>young</b>.
</p>

<h4>Done today</h4>
<p>
  “Done today” counts <b>distinct cards reviewed today</b> (not raw revlog action count),
  so learning steps do not artificially inflate progress.
</p>

<hr>

<h3>🧩 Where you see Deckline (v1.2)</h3>

<h4>1) Deck Browser — card view</h4>
<p>Each enabled deadline deck appears as a card in a modern card layout.</p>

<p><b>Each card shows:</b></p>
<ul>
  <li><b>Deck name</b> (click to open Overview)</li>
  <li><b>Deadline status</b> (“Today”, “in X days”, “Overdue”)</li>
  <li><b>Phase</b> (NEW or REVIEW)</li>
  <li><b>Pending</b> (remaining cards in the current flow, excluding suspended)</li>
  <li><b>Today</b> (“done today / target today”)</li>
  <li><b>Overall progress</b> (0–100%)</li>
  <li><b>Status badge</b>: ON TRACK / BEHIND / REST DAY / NOT STARTED</li>
</ul>

<p><b>Subdecks are included automatically</b> in targets and progress.</p>

<h4>Deckline topbar</h4>
<ul>
  <li><b>Focus mode</b> — show one deck</li>
  <li><b>Sort</b> — by Deadline / Progress / Today</li>
  <li><b>Behind filter</b> — show only decks behind target</li>
  <li><b>Stats button</b> (Premium)</li>
</ul>

<hr>

<h4>2) Deck Overview — “Daily Deckline Progress”</h4>
<ul>
  <li>Shows daily progress: <b>done today / target today</b>.</li>
  <li>Shows phase hint (NEW → cut-off or REVIEW → deadline).</li>
  <li>On rest days: target = 0 with explicit rest-day status.</li>
</ul>

<h4>3) Review screen — bottom progress bar</h4>
<ul>
  <li>Live progress while reviewing.</li>
  <li>Tooltip with target + phase context.</li>
</ul>

<hr>

<h3>📊 Stats (Premium)</h3>

<h4>Chart tab</h4>
<ul>
  <li>Overview of recent done-vs-target trend.</li>
  <li>Supports totals across multiple deadline decks.</li>
</ul>

<h4>Heatmap tab (new in v1.2)</h4>
<ul>
  <li>Per-deck heatmap of recent study days.</li>
  <li>Day-cell color reflects progress against that day's target.</li>
  <li>Tooltip includes done, target, phase, and streak-day context.</li>
  <li>Helps quickly spot pacing issues and deadline pressure.</li>
</ul>

<hr>

<h3>⚙️ Settings</h3>
<p>
  <b>Per deck:</b> Deck Browser → right-click deck → <b>Deadline</b><br>
  <b>Global:</b> Tools → <b>Deckline settings</b>
</p>

<h4>Tab — Deadline (per deck)</h4>
<ul>
  <li>Enable/disable deadline for this deck.</li>
  <li>Custom display name (does not rename the actual Anki deck).</li>
  <li>Start date (shows NOT STARTED if in the future).</li>
  <li>Cut-off date for new cards.</li>
  <li>Final deadline date.</li>
</ul>

<h4>Tab — Optional (per deck)</h4>
<ul>
  <li><b>Expected total cards</b> (planning override for growing decks).</li>
  <li><b>Daily target override</b> (0 = automatic).</li>
  <li><b>Skip weekends</b>.</li>
</ul>

<h4>Tab — Feedback (global)</h4>
<ul>
  <li>Show daily progress bar in deck overview.</li>
  <li>Show daily progress bar in review screen.</li>
  <li><b>Separate time multipliers</b> for NEW and REVIEW phases.</li>
  <li><b>Premium:</b> bar color mode, celebration animation, streaks.</li>
</ul>

<h4>Tab — Vacation (Premium)</h4>
<ul>
  <li>Add single days or ranges as excluded days.</li>
  <li>Deckline treats these days as rest days and redistributes targets.</li>
</ul>

<h4>Tab — ⭐ Premium</h4>
<ul>
  <li>Paste your premium code to unlock.</li>
  <li>Unlocks Stats, unlimited deadlines, vacation days, streaks, and premium visuals.</li>
</ul>

<hr>

<h3>📈 How targets are calculated (simple)</h3>
<ol>
  <li>Choose phase (NEW until cut-off, then REVIEW until deadline).</li>
  <li>Exclude rest days (weekends + vacation).</li>
  <li>Compute stable daily quota using remaining work / remaining study days.</li>
  <li>Compare done today versus target today.</li>
  <li>Assign status badge (ON TRACK / BEHIND / REST DAY / NOT STARTED).</li>
</ol>

<hr>

<h3>❓ FAQ</h3>

<h4>Is progress daily or total?</h4>
<ul>
  <li><b>Daily:</b> Overview card + review bar.</li>
  <li><b>Total:</b> progress in the Deck Browser card.</li>
</ul>

<h4>Does Deckline modify FSRS or scheduling?</h4>
<p>No. Deckline does not modify scheduling; it only provides planning and feedback.</p>

<h4>Do subdecks count?</h4>
<p>Yes, subdecks are automatically included in targets and done-today values.</p>

<hr>

<h3>🛠️ Troubleshooting</h3>
<ul>
  <li><b>Overview bar missing:</b> check Feedback → “Show daily progress bar in deck overview”.</li>
  <li><b>Review bar missing:</b> check Feedback → “Show daily progress bar in review screen”.</li>
  <li><b>Targets seem off:</b> verify deadline/cut-off/weekends/vacation and, if needed, expected total cards.</li>
</ul>

<hr>

<h3>🧹 Managing plans</h3>
<ul>
  <li><b>Edit plan:</b> right-click deck → Deadline.</li>
  <li><b>Clear plans:</b> right-click deck → Clear.</li>
</ul>

<hr>

<h3>📌 Quick tips</h3>
<ul>
  <li>Set your cut-off a few days before your deadline.</li>
  <li>Use expected total cards when your deck is still growing.</li>
  <li>Use skip weekends + vacation for realistic planning.</li>
  <li>Use the review bar as a “done for today” indicator.</li>
</ul>
