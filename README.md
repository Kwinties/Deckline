<h2>&#128216; Deckline Documentation (v2.1)</h2>

<p>
  Deckline helps you finish Anki decks before a chosen <b>deadline</b> by turning remaining work into a clear
  <b>daily target</b>. It shows what to do today, whether you are on pace, and how your deadline progress looks
  directly inside Anki.
</p>

<hr>

<h3>&#9989; What Deckline does</h3>
<ul>
  <li>Creates a <b>deadline-based study plan</b> per deck.</li>
  <li>Splits planning into a <b>NEW phase</b> and <b>REVIEW phase</b> with a configurable cut-off date.</li>
  <li>Converts remaining work into a <b>stable daily quota</b>.</li>
  <li>Shows <b>daily progress</b> in Deck Overview and on the Review screen.</li>
  <li>Shows <b>overall deadline progress</b> in the Deck Browser.</li>
  <li>Includes subdecks automatically in targets, progress, and today counts.</li>
  <li>Supports start dates, skipped weekends, vacation/time-off days, custom display names, and expected total cards.</li>
  <li>Adds Timeline, smart bottom-bar feedback, stats, charts, heatmaps, appearance controls, and Pomodoro surfaces.</li>
</ul>

<h3>&#128683; What Deckline does not do</h3>
<ul>
  <li><b>Does not change Anki scheduling</b> such as FSRS, SM-2, ease, intervals, or leeches.</li>
  <li><b>Does not force cards to appear.</b> It reads collection data to calculate targets and feedback.</li>
</ul>

<hr>

<h3>&#129504; Core concepts</h3>

<h4>Deadline</h4>
<p>The final date you want to be done with a deck.</p>

<h4>Cut-off date</h4>
<p>Deckline uses the cut-off date to split each plan into two phases:</p>
<ul>
  <li><b>Phase 1: NEW -> Cut-off</b> - finish introducing new cards early.</li>
  <li><b>Phase 2: REVIEW -> Deadline</b> - stabilize young cards and clean up review work before the deadline.</li>
</ul>
<p>This reduces the chance of a large learning-card pileup near the end of the plan.</p>

<h4>Young vs mature</h4>
<p>
  Deckline follows Anki's definition: cards become <b>mature</b> at interval &ge; <b>21 days</b>.
  Everything below that is <b>young</b>.
</p>

<h4>Done today</h4>
<p>
  Done today counts <b>distinct cards reviewed today</b>, not raw revlog actions, so repeated learning steps do not
  artificially inflate progress. v2.1 also improves reset-card counting.
</p>

<hr>

<h3>&#129513; Where you see Deckline</h3>

<h4>1) Deck Browser - deadline cards</h4>
<p>Each enabled deadline deck appears as a modern card in the Deck Browser.</p>

<p><b>Each card can show:</b></p>
<ul>
  <li><b>Deck name</b> with click-through to Overview.</li>
  <li><b>Deadline status</b> such as Today, in X days, Overdue, or Not started.</li>
  <li><b>Phase</b> for the current part of the plan.</li>
  <li><b>Pending</b> cards for the current flow, excluding suspended cards.</li>
  <li><b>Today</b> as done today / target today.</li>
  <li><b>Overall progress</b> from 0-100%.</li>
  <li><b>Status badge</b>: ON TRACK, BEHIND, REST DAY, or NOT STARTED.</li>
  <li><b>Optional smart message per deck</b> for more specific daily feedback.</li>
</ul>

<h4>Deckline topbar</h4>
<ul>
  <li><b>Focus mode</b> - show one deadline deck.</li>
  <li><b>Sort</b> - organize cards by deadline, progress, or today.</li>
  <li><b>Behind filter</b> - show only decks behind target.</li>
  <li><b>Timeline panel</b> - inspect deadlines and custom timeline dates.</li>
  <li><b>Pomodoro panel</b> - start, pause, and reset study blocks when Premium is unlocked.</li>
  <li><b>Stats button</b> - open chart and heatmap views.</li>
</ul>

<h4>2) Main-screen bottom bar</h4>
<ul>
  <li>Shows a calm smart message when there is no urgent deadline feedback.</li>
  <li>Can rotate curated study facts by category.</li>
  <li>Can expose Timeline and Pomodoro controls directly from the main screen.</li>
</ul>

<h4>3) Deck Overview - Daily Deckline Progress</h4>
<ul>
  <li>Shows daily progress as <b>done today / target today</b>.</li>
  <li>Shows phase context for NEW -> cut-off or REVIEW -> deadline.</li>
  <li>Shows explicit rest-day status when the target is 0.</li>
</ul>

<h4>4) Review screen - bottom progress bar</h4>
<ul>
  <li>Updates while reviewing.</li>
  <li>Shows target and phase context in the tooltip.</li>
  <li>Can show Pomodoro review timing when enabled.</li>
</ul>

<hr>

<h3>&#128200; Stats, charts, and heatmaps</h3>

<h4>Chart tab</h4>
<ul>
  <li>Shows recent done-vs-target progress.</li>
  <li>Supports totals across multiple deadline decks.</li>
  <li>v2.1 adds clearer chart hover details with today's progress and daily target.</li>
</ul>

<h4>Heatmap tab</h4>
<ul>
  <li>Shows per-deck study-day history.</li>
  <li>Colors each day by progress against that day's target.</li>
  <li>Tooltips include done, target, phase, and streak context.</li>
  <li>v2.1 improves refresh behavior across multiple devices and fixes constant-window sizing issues.</li>
</ul>

<h4>Deadline projection</h4>
<ul>
  <li>Premium unlocks deeper chart views, including the full deadline projection.</li>
</ul>

<hr>

<h3>&#128197; Timeline</h3>
<ul>
  <li>Shows deadlines, cut-off dates, and custom timeline dates in one place.</li>
  <li>Supports range views for short-term and long-term planning.</li>
  <li>Custom dates can be added for exams, milestones, trips, or other planning anchors.</li>
  <li>v2.1 reworks Timeline hover behavior for a cleaner main-screen experience.</li>
</ul>

<hr>

<h3>&#9201;&#65039; Pomodoro</h3>
<ul>
  <li>Premium unlocks Pomodoro timers in Deckline surfaces.</li>
  <li>Supports work/break phase controls, main-screen timer access, and review-screen timing feedback.</li>
  <li>v2.1 resets Pomodoro progress overnight so a new study day starts cleanly.</li>
</ul>

<hr>

<h3>&#9881;&#65039; Settings</h3>
<p>
  <b>Per deck:</b> Deck Browser -> right-click deck -> <b>Deadline</b><br>
  <b>Global:</b> Tools -> <b>Deckline settings</b>
</p>

<h4>Deadline</h4>
<ul>
  <li>Enable or disable a deadline for a deck.</li>
  <li>Set custom display name, start date, cut-off date, and final deadline.</li>
  <li>Use expected total cards to keep planning stable for growing decks.</li>
  <li>Use a daily target override when you want a fixed manual target.</li>
  <li>Skip weekends when you want rest days built into the plan.</li>
</ul>

<h4>Feedback</h4>
<ul>
  <li>Show or hide progress bars in Overview and Review.</li>
  <li>Configure smart messages, streak feedback, and phase-specific time multipliers.</li>
  <li>Optionally show smart messages per deck instead of only in the bottom bar.</li>
</ul>

<h4>Appearance</h4>
<ul>
  <li>Choose Deckline theme behavior for cards, progress bars, stats, and browser surfaces.</li>
  <li>Adjust card opacity and visual style.</li>
  <li>v2.1 fixes card opacity and improves the Follow Deckline Theme deck-browser layout for long deck names.</li>
</ul>

<h4>Plugins</h4>
<ul>
  <li>Manage Timeline, Pomodoro, and bottom-bar settings from one place.</li>
  <li>Choose bottom-bar study fact categories and rotation behavior.</li>
</ul>

<h4>Premium</h4>
<ul>
  <li>Paste your premium code to unlock Premium features.</li>
  <li>Premium in Deckline V2 unlocks Pomodoro, richer appearance controls, vacation/time-off planning, unlimited deadlines, streaks, premium visuals, and deeper chart views.</li>
</ul>

<hr>

<h3>&#128640; New in v2.1</h3>
<ul>
  <li><b>Chart hover details:</b> hover any chart day to see today's progress and daily target.</li>
  <li><b>Optional smart messages per deck:</b> show smart feedback on each deadline card.</li>
  <li><b>Better multi-device updates:</b> charts and heatmaps refresh more reliably after studying across devices.</li>
  <li><b>Card opacity fixed:</b> the opacity setting now changes card opacity correctly.</li>
  <li><b>Timeline hover reworked:</b> Timeline interaction feels cleaner on the main screen.</li>
  <li><b>Deck browser layout fixed:</b> Follow Deckline Theme uses a fixed browser size to avoid overlap with long deck names.</li>
  <li><b>Heatmap fixes:</b> heatmaps keep a constant window size more reliably.</li>
  <li><b>Pomodoro overnight reset:</b> Pomodoro progress resets between study days.</li>
  <li><b>Reset-card counting improved:</b> reset cards are counted correctly again.</li>
</ul>

<hr>

<h3>&#128202; How targets are calculated</h3>
<ol>
  <li>Choose the current phase: NEW until cut-off, then REVIEW until deadline.</li>
  <li>Exclude rest days such as skipped weekends and vacation/time-off days.</li>
  <li>Calculate the stable daily quota from remaining work and remaining study days.</li>
  <li>Compare done today against target today.</li>
  <li>Assign a status badge such as ON TRACK, BEHIND, REST DAY, or NOT STARTED.</li>
</ol>

<hr>

<h3>&#10067; FAQ</h3>

<h4>Is progress daily or total?</h4>
<ul>
  <li><b>Daily:</b> Overview card, review bar, chart hover details, and today counters.</li>
  <li><b>Total:</b> overall progress on Deck Browser cards and deadline projections.</li>
</ul>

<h4>Does Deckline modify FSRS or scheduling?</h4>
<p>No. Deckline does not modify scheduling. It only provides planning and feedback.</p>

<h4>Do subdecks count?</h4>
<p>Yes. Subdecks are automatically included in targets, progress, and done-today values.</p>

<h4>Why does today show fewer reviews than Anki's raw review count?</h4>
<p>Deckline counts distinct cards reviewed today so repeated learning steps do not inflate deadline progress.</p>

<hr>

<h3>&#128736;&#65039; Troubleshooting</h3>
<ul>
  <li><b>Overview bar missing:</b> check Feedback -> Show daily progress bar in deck overview.</li>
  <li><b>Review bar missing:</b> check Feedback -> Show daily progress bar in review screen.</li>
  <li><b>Targets seem off:</b> verify start date, cut-off, deadline, skipped weekends, vacation days, and expected total cards.</li>
  <li><b>Layout looks cramped:</b> check Appearance settings and update to v2.1 for the latest Deck Browser layout fixes.</li>
  <li><b>Pomodoro unavailable:</b> Pomodoro is a Premium feature and must be enabled in Deckline settings.</li>
</ul>

<hr>

<h3>&#129529; Managing plans</h3>
<ul>
  <li><b>Edit plan:</b> right-click deck -> Deadline.</li>
  <li><b>Mark complete:</b> use Deckline's completion flow when a deadline is effectively finished.</li>
  <li><b>Archive completed deadline:</b> move completed plans out of the active deadline list and into the stats archive.</li>
  <li><b>Clear plans:</b> right-click deck -> Clear.</li>
</ul>

<hr>

<h3>&#128204; Quick tips</h3>
<ul>
  <li>Set your cut-off a few days before your final deadline.</li>
  <li>Use expected total cards when your deck is still growing.</li>
  <li>Use skipped weekends and vacation/time-off days for realistic targets.</li>
  <li>Use Timeline for exams, milestones, and cross-deck deadline pressure.</li>
  <li>Use the review bar as your done-for-today indicator.</li>
</ul>
