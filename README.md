<h2>📘 Deckline Documentation (Beginner-Friendly)</h2>
<p>
  Deckline helps you finish a deck before a chosen <b>deadline</b> by converting the remaining work into a clear <b>daily target</b>.
  It shows what to do <b>today</b>, whether you’re on pace (🐇/🐢), and visualizes both <b>daily</b> and <b>overall</b> progress.
</p>
<hr>

<h3>✅ What Deckline Does (in plain English)</h3>
<ul>
  <li><b>Creates a plan</b> for each deck (deadline-based).</li>
  <li><b>Splits your work into a daily quota</b> so you don’t cram at the end.</li>
  <li><b>Shows daily progress</b> in the Deck Overview and in the Review screen.</li>
  <li><b>Shows overall progress</b> in the Deck Browser (the list of decks).</li>
  <li><b>Supports “days off”</b> (skip weekends + vacations) and redistributes the workload.</li>
</ul>

<h3>🚫 What Deckline Does NOT Do</h3>
<ul>
  <li><b>It does not change Anki scheduling</b> (FSRS/SM-2, ease, intervals, leeches, etc.).</li>
  <li><b>It does not force cards to appear.</b> It only reads your collection to compute targets and show feedback.</li>
</ul>
<hr>

<h3>🧠 Core Concepts</h3>

<h4>Deadline</h4>
<p>The date you want to be “done” with the deck (including review stabilization).</p>

<h4>Cut-off (Finish new cards)</h4>
<p>
  Deckline splits your plan into 2 phases:
</p>
<ul>
  <li><b>Phase 1: New → Cut-off</b> (finish introducing new cards early)</li>
  <li><b>Phase 2: Young → Deadline</b> (clean up young cards / stabilize reviews)</li>
</ul>
<p>
  This prevents a huge pile-up of young cards close to your deadline.
</p>

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

<h3>🧩 Where You See Deckline</h3>

<h4>1) Deck Browser Footer (Deck List Table)</h4>
<p>
  This is the table that appears in the Deck Browser (where you see your deck list).
  Each row represents one enabled deadline deck.
</p>

<ul>
  <li>
    <b>Deck</b> — clickable name. Click it to open that deck’s Overview page.
  </li>

  <li>
    <b>Deadline</b> — shows days remaining (or overdue).
    <br>
    <i>Hover</i> to see details about the cut-off and/or deadline.
  </li>

  <li>
    <b>Pending</b> — how many cards are left in your current “pipeline”:
    <b>new + young</b> (suspended not included).
  </li>

  <li>
    <b>Reviews</b> — how many <b>distinct cards</b> you reviewed today in this deck (including subdecks).
    <br>
    <i>Hover</i> to also see “total reviews” (raw revlog count).
  </li>

  <li>
    <b>Target</b> — your <b>exact daily quota</b> for today (constant during the day).
    <ul>
      <li>If today is a rest day (weekend/vacation), target becomes <b>0</b>.</li>
      <li>If you passed the cut-off while still having new (or planned new) cards, you may see a <b>⚠️</b> warning.</li>
    </ul>
  </li>

  <li>
    <b>Tempo</b> — your pace for <b>today</b>:
    <ul>
      <li>🐇 = today’s quota met</li>
      <li>🐢 = behind today</li>
      <li>😴 = rest day (excluded)</li>
      <li>⏳ = not started yet (start date in the future)</li>
    </ul>
    <i>Hover</i> to see: Quota • Done • Left • today’s % + which phase you are in.
  </li>

  <li>
    <b>Progress</b> — your overall progress toward finishing the deck:
    <ul>
      <li><b>0–67%</b>: progress through Phase 1 (getting through new cards)</li>
      <li><b>67–100%</b>: progress through Phase 2 (turning young → mature)</li>
    </ul>
    Display style is configurable (bar, %, or both).
  </li>
</ul>

<p>
  <b>Subdecks:</b> all counts for a deck include its subdecks automatically.
</p>
<hr>

<h4>2) Deck Overview Page: “Daily Deckline Progress” Card</h4>
<p>
  This appears on the deck’s Overview screen (near your top stats / heatmap area).
</p>

<ul>
  <li><b>Daily progress</b> = “done today / target today”</li>
  <li><b>Progress bar color</b> shifts from red → yellow → green as you approach 100%</li>
  <li><b>Shows phase hint</b> (new → cutoff or young → deadline)</li>
  <li><b>Rest days</b> show as “Rest day (excluded)” and target 0</li>
</ul>

<p>
  You can toggle this card on/off in Settings.
</p>
<hr>

<h4>3) Review Screen: Bottom Progress Bar</h4>
<p>
  While reviewing, Deckline can show a thin progress bar at the bottom of the Anki window.
  This is the same idea as the Overview card: <b>daily progress</b> toward today’s quota.
</p>

<ul>
  <li>Updates as you review (question/answer).</li>
  <li>Uses the same red→yellow→green color logic.</li>
  <li>Has a tooltip: <b>Target</b> + phase hint.</li>
</ul>

<p>
  You can toggle this bar on/off in Settings.
</p>
<hr>

<h3>⚙️ Deckline Settings (Explained)</h3>
<p>
  Open settings from the Deck Browser: right-click a deck → <b>Deadline</b>.
</p>

<h4>Tab 1 — Deadline</h4>
<ul>
  <li>
    <b>Enable Deadline for “Deck Name”</b>
    <br>
    Turns the plan on/off for that deck. Disabling hides it from Deckline’s UI.
  </li>

  <li>
    <b>Deck name</b>
    <br>
    A custom display name for Deckline (does not rename the deck in Anki).
  </li>

  <li>
    <b>Deadline</b>
    <br>
    The final date you want to be finished.
  </li>

  <li>
    <b>Start date</b>
    <br>
    The day your plan begins. If it’s in the future, Deckline shows ⏳ and hides targets until it starts.
  </li>

  <li>
    <b>Finish new cards</b> (Cut-off)
    <br>
    Set how many days before the deadline you want all <b>new</b> cards introduced.
    This automatically moves when you change the deadline.
  </li>

  <li>
    <b>Expected total cards</b> (Planning override)
    <br>
    Use this if you will <b>add/import cards gradually</b> and want stable targets from day 1.
    <ul>
      <li>Deckline will treat the deck as if it will eventually contain that many cards.</li>
      <li>This prevents early targets from being “too low” just because future cards aren’t in the deck yet.</li>
      <li>If expected total is set, Deckline also shows “planned” info in tooltips (and may cap unrealistic daily quotas).</li>
    </ul>
  </li>

  <li>
    <b>Days off → Skip weekends</b>
    <br>
    Excludes Saturdays/Sundays from target calculations. The workload is redistributed across study days.
  </li>
</ul>

<h4>Tab 2 — Feedback</h4>

<h5>Progress bar</h5>
<ul>
  <li>
    <b>Show progress bar (Deck overview)</b>
    <br>
    Toggles the Overview “Daily Deckline Progress” card.
  </li>

  <li>
    <b>Show progress bar (Review screen)</b>
    <br>
    Toggles the bottom bar while reviewing.
  </li>
</ul>

<h5>Feedback settings</h5>
<ul>
  <li>
    <b>Progress display</b> (Deck Browser “Progress” column)
    <br>
    Choose:
    <ul>
      <li><b>Bar + Percentage</b></li>
      <li><b>Only Bar</b></li>
      <li><b>Only Percentage</b></li>
    </ul>
  </li>

  <li>
    <b>Show daily message</b>
    <br>
    Shows a small line under each deck row in the Deck Browser explaining what to do today.
  </li>

  <li>
    <b>Enable streaks</b>
    <br>
    Tracks consecutive days where you meet your <b>daily quota</b>.
    Shows ❄️ for 0, 🔥 for 1+.
  </li>

  <li>
    <b>Time estimate multiplier</b>
    <br>
    Only affects the <b>displayed time estimate</b> in the daily message.
    <ul>
      <li>Example: if Anki suggests ~20m and multiplier is 1.5× → Deckline shows ~30m.</li>
      <li>This does <b>not</b> change scheduling or targets.</li>
    </ul>
  </li>
</ul>

<h4>Tab 3 — Vacation</h4>
<p>
  Vacation days are excluded from target calculations (like weekends), and the plan is redistributed.
</p>
<ul>
  <li><b>Add day</b> — adds one excluded day.</li>
  <li><b>Add range</b> — adds an excluded range using the format <code>DD-MM-YYYY/DD-MM-YYYY</code>.</li>
  <li><b>Remove selected</b> — removes selected entries.</li>
  <li><b>Clear</b> — clears the entire list.</li>
</ul>
<hr>

<h3>📈 How Targets Are Calculated (Simple Version)</h3>
<ol>
  <li>
    <b>Pick the current phase</b>:
    <ul>
      <li>If today is before cut-off and there are still <b>new</b> (or planned new) cards → focus on <b>new</b>.</li>
      <li>Otherwise → focus on <b>young</b>.</li>
    </ul>
  </li>

  <li>
    <b>Exclude rest days</b> (skip weekends + vacation days) from the remaining day count.
  </li>

  <li>
    <b>Compute today’s quota</b> (constant during the day):
    <br>
    Deckline uses a “constant quota” approach so your target does not fluctuate mid-day as you review.
  </li>

  <li>
    <b>Done today</b> is the count of distinct cards reviewed today (includes subdecks).
  </li>

  <li>
    <b>Tempo</b>:
    <ul>
      <li>🐇 if done_today ≥ quota_today</li>
      <li>🐢 otherwise</li>
    </ul>
  </li>

  <li>
    <b>Time estimate</b>:
    <br>
    remaining_today × your measured average time per review (learning/review/relearn), then multiplied by your time multiplier.
  </li>
</ol>
<hr>

<h3>❓ FAQ</h3>

<h4>Is the progress indicator daily or total?</h4>
<ul>
  <li><b>Daily</b>: Overview card + Review bottom bar (today vs today’s target).</li>
  <li><b>Total</b>: Deck Browser “Progress” column (overall toward deadline).</li>
</ul>

<h4>What does the time estimate multiplier do?</h4>
<p>
  It only changes the <b>displayed</b> time estimate in the daily message. It does not affect scheduling or targets.
</p>

<h4>Does Deckline change FSRS or Anki’s scheduling?</h4>
<p>
  No. Deckline does <b>not</b> modify Anki scheduling (FSRS/SM-2, intervals, ease, leeches, etc.).
  It only reads your data to show targets, progress, and estimates.
</p>

<h4>Why is my target very low at the start?</h4>
<p>
  If you add cards gradually, Deckline can’t “see” future cards yet. Use <b>Expected total cards</b> to plan ahead and keep targets stable.
</p>

<h4>Do subdecks count?</h4>
<p>Yes — targets and “done today” include subdecks.</p>

<h4>Why do I see ⚠️ after the cut-off?</h4>
<p>
  That means your cut-off date has passed but you still have new (or planned) cards left to introduce.
  Deckline warns you because the plan expected those to be finished earlier.
</p>

<h4>How can I focus on young cards only?</h4>
<p>
  Use a <b>Filtered Deck</b>:
</p>
<pre><code>deck:"Your Deck Name" is:due prop:ivl&lt;21</code></pre>
<p>
  Optional: include learning cards too:
</p>
<pre><code>(is:learn OR is:review) is:due</code></pre>
<hr>

<h3>🛠️ Troubleshooting</h3>
<ul>
  <li>
    <b>“Daily Deckline Progress” card is missing</b>
    <br>
    Check Settings → Feedback → “Show progress bar (Deck overview)”.
    If you use other Overview add-ons, placement can vary depending on your layout.
  </li>

  <li>
    <b>Review progress bar not visible</b>
    <br>
    Enable it in Settings → Feedback → “Show progress bar (Review screen)”.
  </li>

  <li>
    <b>Numbers look “off”</b>
    <br>
    Double-check:
    <ul>
      <li>Correct deck has a deadline enabled</li>
      <li>Deadline date / cut-off date make sense</li>
      <li>Skip weekends / vacations are correct</li>
      <li>If you add cards gradually, consider setting Expected total cards</li>
    </ul>
  </li>

  <li>
    <b>Targets jump after adding cards</b>
    <br>
    That’s normal if Expected total cards is 0. Set Expected total cards to stabilize.
  </li>
</ul>
<hr>

<h3>🧹 Managing Plans</h3>
<ul>
  <li>
    <b>Edit a plan</b>: Deck Browser → right-click deck → Deadline
  </li>
  <li>
    <b>Clear plans</b>: use the “Clear” option to remove selected deadlines from Deckline.
  </li>
</ul>
<hr>

<h3>📌 Quick Tips (Less Confusion, Better Results)</h3>
<ul>
  <li>Set your <b>cut-off</b> a few days before the deadline (e.g., 5–10 days) to avoid last-minute review chaos.</li>
  <li>If you’re still building/importing a deck, set <b>Expected total cards</b>.</li>
  <li>Use <b>Skip weekends</b> + <b>Vacation</b> so your targets match real life.</li>
  <li>Use the Review bar to know exactly when you’re “done for today”.</li>
</ul>
