<h2>🚀 Changelog</h2>

<h3>Deckline v1.0</h3>
<h4>(2026-02-15)</h4>
<ul>
  <li>🆕 Deck Browser redesign — Deckline is now shown as <b>clean cards</b> instead of a table for faster scanning and a more modern look</li>
  <li>🎛️ New topbar controls — <b>Focus</b>, <b>Sort</b> and quick filters to instantly find the decks that matter most</li>
  <li>🟢🔴 Better status feedback — clearer <b>On track</b> / <b>Behind</b> / <b>Pending</b> indicators with improved badges and visuals</li>
  <li>📊 Premium: Stats dashboard — new <b>7-day Stats</b> window showing done vs target (per deck + “All deadlines” total)</li>
  <li>💎 Premium: Motivation & control — <b>Unlimited deadlines</b>, <b>Vacation days</b> (auto-adjust daily targets), <b>custom progress colors</b>, and <b>celebration</b> when hitting 100%</li>
  <li>🧠 UX polish — cleaner spacing/typography and improved clarity for <b>Phase 1 (NEW)</b> vs <b>Phase 2 (REVIEW)</b></li>
</ul>
<hr>


<h4>(2026-02-06)</h4>
<ul>
  <li>🎉 Celebration setting added — optional celebration animation when you reach 100% of today’s target in the review screen</li>
  <li>✨ Cleaner Deckline UI — refreshed <b>Tempo</b> indicator and <b>Total Progress</b> display for better alignment, spacing, and visual consistency</li>
  <li>📍 Improved overview placement — the Deckline table now appears in a more natural position on the main screen</li>
</ul>
<hr>


<h4>(2026-1-26)</h4>
<ul>
  <li>🎯 Daily target override refined — after the cutoff, daily targets have a better calculation method</li>
  <li>⚠️ Cutoff warning restored — the daily message once again clearly warns (in red, with an icon) when you still have <i>new cards left</i> after entering the <i>Young → Mature</i> phase</li>
  <li>🖱️ Clickable Deck link crash fixed — hopefully resolved an issue where clicking a deck name from the Deckline table could crash Anki on some systems</li>
</ul>
<hr>


<h4>(2026-1-24)</h4>
<ul>
  <li>🛠️ Review progress bar bugfix — the review progress bar no longer appears briefly on app startup when it’s disabled</li>
  <li>🧩 Subdeck stability fix — resolved an issue where clicking certain subdecks could cause the Deck Overview to fail on some Anki versions</li>
  <li>🛡️ Crash-safe overview rendering — Deckline now fails gracefully if an unexpected edge case occurs, preventing broken deck overviews</li>
</ul>
<hr>

<h4>(2026-1-23)</h4>
<ul>
  <li>🧮 Pending number improved — the <b>Pending</b> counter now also counts down correctly during the <i>New → Young</i> phase</li>
  <li>🎨 Bar color customization — new option to change the progress bar color (Auto / Solid / Gradient)</li>
  <li>🧼 Deckline settings restyle — settings UI has been restyled for a cleaner, more compact look and better visual consistency</li>
  <li>🧠 New → Young clarity — improved labels and tooltips so it’s clearer what happens in the <i>New → Young</i> phase</li>
  <li>✅ Daily progress logic change — only <b>new cards learned today</b> now count toward <b>Daily Reviews</b> (instead of distinct cards)</li>
</ul>
<hr>


<h4>(2026-1-17)</h4>
<ul>
  <li>📊 Review progress bar added — a compact progress bar is now shown at the bottom of the Review screen while studying</li>
  <li>✅ Deadline total progress fixed — an issue in the Deadline UI where total progress could be calculated incorrectly has been resolved</li>
  <li>🧹 Small bug fixes — minor stability improvements and UI polish across Deckline</li>
</ul>
<hr>


<h4>(2026-1-15)</h4>
<ul>
  <li>🛠️ Settings UI improved — cleaner, more compact layout with neatly aligned fields across 3 tabs (Deadline / Feedback / Vacation)</li>
  <li>📈 Daily progress logic updated — daily reviews now count distinct cards (not revlog actions), and new cards started today can be compared for more accurate “on target” progress</li>
</ul>
<hr>

<h4>(2026-1-12)</h4>
<ul>
  <li>📊 Daily Progress Bar now works in subdecks — the overview bar automatically uses the nearest parent deck with a deadline</li>
  <li>📅 Finish new cards before date — you can now choose a cutoff date with a calendar instead of only using “days before deadline”</li>
</ul>
<hr>

<h4>(2025-12-17)</h4>
<ul>
  <li>⏱️ Time estimate multiplier — new optional setting to scale the time estimate in the daily message (e.g. <code>1.5×</code> turns <i>23 min</i> into <i>~35 min</i>)</li>
</ul>
<hr>

<h4>(2025-12-16)</h4>
<ul>
  <li>🧮 Expected total cards (optional) — plan ahead by setting how many cards you <i>expect</i> to have in a deck by the end of the block; daily targets use this for smarter pacing when you add cards gradually</li>
  <li>🗂️ Deadline tab cleanup — settings are grouped into <b>Deadline settings</b> and <b>Optional settings</b> for better readability</li>
  <li>🗑️ Clear button — quickly reset <b>Expected total cards</b> back to <code>0</code> (disables the planning override)</li>
</ul>
<hr>

<h4>(2025-12-15)</h4>
<ul>
  <li>🗂️ Deadline settings split into tabs — <b>Deadline</b> (core settings) and <b>Additional</b> (extras) for a cleaner setup</li>
  <li>⏳ Pre-start indicator — if a deck’s <i>Start Date</i> is in the future, the <b>Tempo</b> column shows an hourglass with a “studying starts in …” tooltip</li>
  <li>💬 Pre-start daily message — daily message now shows “Studying starts in … days” before the start date</li>
  <li>🛌 Days off support — new per-deck option <b>Skip weekends</b> so weekends don’t count toward targets (targets increase on study days)</li>
  <li>🏖️ Vacation planner — add vacations via a friendly UI:
    <ul>
      <li><b>Add day</b> for a single date</li>
      <li><b>Add range</b> for start/end dates</li>
      <li>Remove selected items or clear all</li>
    </ul>
  </li>
  <li>📆 Vacation ranges — ranges use <code>/</code> as the separator (example: <code>20-12-2025/04-01-2026</code>)</li>
  <li>⚡ Performance improvements — reduced repeated DB queries while rendering the deckline table</li>
</ul>
<hr>

<h4>(2025-12-11)</h4>
<ul>
  <li>🖱️ Click-to-open decks — clicking a deck name opens its Overview (credits: Caladan0)</li>
  <li>📶 Daily Progress Bar (Overview) — big bar showing <i>Target today</i>, <i>Done today</i>, and % (toggleable)</li>
  <li>🐇/🐢 Tempo based on daily quota — hare only when today’s quota is met; tooltip shows <b>Quota • Done • Left • Today’s %</b> + phase</li>
  <li>💬 Daily message uses daily quota — “learn X more today” + time estimate</li>
  <li>📅 “Today” column — shows completed reviews today (instead of averages)</li>
  <li>⚙️ New setting — toggle daily progress bar on deck overview</li>
</ul>
<hr>

<h4>(2025-12-04)</h4>
<ul>
  <li>💬 Deadline column tooltip — hover remaining days to see when <i>new cards</i> are due (based on your cut-off)</li>
  <li>🔄 Bugfix — fixed an issue with setting multiple deadlines</li>
</ul>
<hr>

<h4>(2025-11-17)</h4>
<ul>
  <li>🔄 Minor tweaks and bugfixes for improved usability</li>
</ul>
<hr>

<h4>(2025-11-10)</h4>
<ul>
  <li>🔥 Streaks — track how many days in a row you hit your daily target (toggleable). Uses ❄️ at 0 and 🔥 for 1+.</li>
  <li>🗂️ Selective deadline removal — <b>Clear</b> now lets you pick specific decks to remove</li>
  <li>💾 Deadline dialog behavior — explicit <em>Save</em> or <em>Cancel</em>; closing with ✖ no longer saves changes</li>
</ul>
<hr>

<h4>(2025-09-29)</h4>
<ul>
  <li>🗑️ Clear deadlines — use <b>Clear</b> via the ⚙️ menu to remove deadlines</li>
</ul>

<h4>(2025-06-25)</h4>
<ul>
  <li>📅 One-time popup 3 days before a deck’s deadline</li>
  <li>⚙️ New setting: choose how progress is displayed — <i>bar + %</i>, <i>only bar</i>, or <i>only percentage</i></li>
  <li>📈 Smart daily message: shows if you're on pace or need to catch up (toggleable)</li>
  <li>💡 Tooltip improvements for tempo and target — clearer and more informative</li>
</ul>
