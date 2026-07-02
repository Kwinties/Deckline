<h2>&#128216; Deckline (v2.4)</h2>

<p>
  Deckline helps you finish Anki decks before a chosen <b>deadline</b> by turning remaining work into a clear
  <b>daily target</b>. It shows what to do today, whether you are on pace, and how your deadline progress looks
  directly inside Anki — without touching Anki's scheduler.
</p>

<hr>

<h3>&#9989; What Deckline does</h3>
<ul>
  <li>Creates a <b>deadline-based study plan</b> per deck, split into a NEW phase and REVIEW phase.</li>
  <li>Converts remaining work into a <b>stable daily quota</b> that adjusts for rest days and day-off targets.</li>
  <li>Shows <b>daily progress</b> in Deck Overview and on the Review screen.</li>
  <li>Shows <b>overall deadline progress</b> in the Deck Browser.</li>
  <li>Includes subdecks automatically in targets, progress, and today counts.</li>
  <li>Supports start dates, skipped weekends, vacation/time-off days, custom display names, expected total cards, and daily target overrides.</li>
  <li>Creates a <b>smart filtered deck</b> with exactly the cards needed to hit your daily target — click the <b>NEW</b> or <b>REVIEW</b> phase button on a deck card.</li>
</ul>

<h3>&#128683; What Deckline does not do</h3>
<ul>
  <li>Does not change Anki scheduling (FSRS, SM-2, ease, intervals, leeches).</li>
  <li>Does not force cards to appear — it reads your collection to calculate targets and feedback.</li>
</ul>

<hr>

<h3>&#129504; Core concepts</h3>

<b>Deadline</b> — the final date you want to finish a deck.<br><br>

<b>Cut-off date</b> — splits the plan into two phases:
<ul>
  <li><b>Phase 1: NEW → Cut-off</b> — finish introducing new cards early.</li>
  <li><b>Phase 2: REVIEW → Deadline</b> — stabilize young cards before the deadline.</li>
</ul>

<b>Young vs mature</b> — cards become mature at interval ≥ 21 days.<br><br>

<b>Done today</b> — counts distinct cards reviewed today, not raw revlog actions.

<hr>

<h3>&#129513; Where you see Deckline</h3>

<h4>Deck Browser — deadline cards</h4>
<p>Each deadline deck appears as a card showing deck name, deadline status, phase (click <b>NEW</b> or <b>REVIEW</b> to create a smart filtered deck), pending cards, today's progress, overall progress, status badge, and an optional smart message.</p>

<h4>Deckline Home</h4>
<p>A modern web-based home view inside the stats window. Shows a <b>clear plan for today</b>, a <b>7-day weekly rhythm</b> with upcoming targets, a forecast of deadlines ahead, and attention cards for any deck that needs focus. Open it via the stats button in the topbar.</p>

<h4>Topbar (Deck Browser)</h4>
<p>Focus mode, sort options, behind filter, Timeline panel, Pomodoro panel, and the stats button.</p>

<h4>Main-screen bottom bar</h4>
<p>Smart messages, curated study facts, and optional Timeline/Pomodoro controls. Can be hidden from settings.</p>

<h4>Deck Overview</h4>
<p>Daily progress as <b>done / target</b> with phase and rest-day context.</p>

<h4>Review screen</h4>
<p>A bottom progress bar that updates while reviewing, showing your daily target and phase context — with Premium: completion effects, after-target behavior, checkpoints, and Pomodoro timing.</p>

<hr>

<h3>&#128200; Stats window</h3>
<p>Open via the stats button in the topbar. Contains six tabs:</p>
<ul>
  <li><b>Home</b> — daily plan and 7-day weekly rhythm overview.</li>
  <li><b>Metrics</b> — deadline activity and progress patterns across all your decks.</li>
  <li><b>Chart</b> — recent done-vs-target per deck; Premium adds an all-decks timeframe and full deadline projection.</li>
  <li><b>Heatmap</b> — per-deck study-day history colored by progress against daily targets.</li>
  <li><b>Milestones</b> — satisfying rewards for consistency, without changing Anki scheduling.</li>
  <li><b>Archive</b> — completed deadlines with their full history.</li>
</ul>

<hr>

<h3>&#128197; Timeline</h3>
<p>Shows all deadlines, cut-off dates, and custom dates (exams, trips, milestones) in one range view.</p>

<h3>&#9201;&#65039; Pomodoro <i>(Premium)</i></h3>
<p>Timers in Deckline surfaces with work/break controls and review-screen timing feedback. Resets overnight.</p>

<hr>

<h3>&#9881;&#65039; Settings</h3>
<p><b>Per deck:</b> Deck Browser → right-click deck → <b>Deadline</b> &nbsp;|&nbsp; <b>Global:</b> Tools → <b>Deckline settings</b></p>

<table>
  <tr><th>Page</th><th>What you configure</th></tr>
  <tr><td><b>Schedule</b></td><td>Deck name, start date, cut-off date, deadline.</td></tr>
  <tr><td><b>Planning</b></td><td>Expected total cards, daily target override, day rollover, days off.</td></tr>
  <tr><td><b>Progress</b></td><td>Progress bar visibility, time-estimate multipliers, streaks <i>(Premium)</i>.</td></tr>
  <tr><td><b>Plugins</b></td><td>Timeline, Pomodoro, bottom bar, review messages, deck card layout.</td></tr>
  <tr><td><b>Visuals</b></td><td>Theme, card styling, icon customization (unlock button for free users), status colors <i>(Premium)</i>, review bar effects <i>(Premium)</i>.</td></tr>
  <tr><td><b>Premium</b></td><td>License code entry and feature overview.</td></tr>
</table>

<hr>

<h3>&#11088; Premium features</h3>
<ul>
  <li>Pomodoro timers in Deckline surfaces.</li>
  <li>Streak tracking.</li>
  <li>Vacation/time-off planning.</li>
  <li>Unlimited deadlines.</li>
  <li>Custom deck icon pack.</li>
  <li>Custom status colors.</li>
  <li>Review bar: completion effect, after-target behavior, and checkpoints.</li>
  <li>Full deadline projection chart and all-decks timeframe.</li>
</ul>

<hr>

<h3>&#128640; New in v2.4</h3>

<b>Free</b>
<ul>
  <li><b>Unlock button</b> — free users can now access custom icon drawing and card blur/opacity controls.</li>
  <li><b>Reworked Deckline Home</b> — modern web UI with a clear daily plan and 7-day weekly rhythm.</li>
  <li><b>Quick filtered deck</b> — click <b>NEW</b> or <b>REVIEW</b> on a deck card to instantly create a filtered deck sized to your daily target.</li>
  <li>Performance and UI tweaks.</li>
</ul>

<b>Premium</b>
<ul>
  <li><b>Completion effect</b> — visual effect when you hit your daily target.</li>
  <li><b>After completed target</b> — control how the review bar behaves once your goal is reached.</li>
  <li><b>Checkpoints</b> — milestones along the review bar for at-a-glance session progress.</li>
</ul>

<hr>

<h3>&#128202; How targets are calculated</h3>
<ol>
  <li>Choose the current phase (NEW until cut-off, then REVIEW until deadline).</li>
  <li>Exclude rest days (skipped weekends, vacation/time-off).</li>
  <li>Apply the day-off learning amount for partial rest days.</li>
  <li>Divide remaining work by remaining study days.</li>
  <li>Compare done today against the quota and assign a status badge.</li>
</ol>

<hr>

<h3>&#10067; FAQ</h3>

<b>Does Deckline modify FSRS or scheduling?</b><br>
No. It only provides planning and feedback.<br><br>

<b>Do subdecks count?</b><br>
Yes — automatically included in targets, progress, and done-today values.<br><br>

<b>Why does today show fewer reviews than Anki's raw count?</b><br>
Deckline counts distinct cards, not revlog actions, so repeated learning steps don't inflate progress.<br><br>

<b>Is progress daily or total?</b><br>
Daily: Overview, review bar, chart details, today counters. Total: Deck Browser progress and deadline projections.

<hr>

<h3>&#128736;&#65039; Troubleshooting</h3>
<ul>
  <li><b>Overview bar missing</b> — check Progress settings → Show daily progress bar in deck overview.</li>
  <li><b>Review bar missing</b> — check Progress settings → Show daily progress bar in review screen.</li>
  <li><b>Targets seem off</b> — verify dates, skipped weekends, vacation days, day-off learning amount, and expected total cards.</li>
  <li><b>Pomodoro unavailable</b> — requires Premium, must be enabled in Plugins settings.</li>
</ul>

<hr>

<h3>&#129529; Managing plans</h3>
<ul>
  <li><b>Edit:</b> right-click deck → Deadline.</li>
  <li><b>Complete:</b> use Deckline's completion flow when a deadline is finished.</li>
  <li><b>Archive:</b> move completed plans to the metrics archive.</li>
  <li><b>Clear:</b> right-click deck → Clear.</li>
</ul>

<hr>

<h3>&#128204; Quick tips</h3>
<ul>
  <li>Set the cut-off a few days before the final deadline.</li>
  <li>Use expected total cards for growing decks.</li>
  <li>Use Timeline for cross-deck planning and exam dates.</li>
  <li>Check Deckline Home before you start reviewing.</li>
  <li>Use the review bar as your done-for-today indicator.</li>
</ul>

<hr>

<p>Found a bug or mistake? Please <a href="https://github.com/Kwinties/Deckline/issues">open an issue on GitHub</a>.</p>
