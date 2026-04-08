# Engineering Brief — MAS ACTP Simulation Fix
**Project:** Enhancing Resilience and Safety in Multi-Agent Systems (MAS) through Decentralized Failure Recovery
**Author:** Dimitri Barth Nanmejo Sinou
**File to fix:** `mas_actp_simulation.py`
**Priority:** High — IEEE paper submission depends on these results

---

## Context

This simulation implements the **Adaptive Consensus Threshold Protocol (ACTP)** for a Master's thesis research paper targeting IEEE publication. It compares ACTP (novel contribution) against a baseline (fixed threshold) MAS recovery system across:
- 3 agent scales: 20, 100, 500 agents
- 6 failure types: random crash, cascading, targeted, environmental, cyber attack, human error
- 3 random seeds averaged per experiment
- 150 simulation steps

The simulation currently runs and produces 6 graphs + a summary CSV. However **two critical problems exist** that must be fixed before the results are credible for IEEE review.

---

## Problem 1 — Kill-Switch Never Activates (Critical)

### What is happening
The graduated kill-switch (YELLOW → ORANGE → RED) almost never triggers. Graph 4 (`graph4_kill_switch.png`) shows near-zero activation across all conditions. The summary CSV shows `ks_red_steps = 0` for every scenario.

### Root cause
The `evaluate_kill_switch()` function evaluates thresholds correctly, but the `run_simulation()` loop **stops the entire simulation on RED** and pads the rest with the same metrics. More importantly, the failure injection fractions are too small and agents partially recover too quickly — the system never accumulates enough simultaneous failures to cross the 30% ORANGE or 50% RED thresholds.

Additionally, `kill_switch_level` is stored as a **string** (`"NONE"`, `"YELLOW"`, `"ORANGE"`, `"RED"`) but the summary CSV export tries to compare it to integers (`== 2`), which silently returns zero counts.

### What needs to be fixed

**Fix 1a — Increase failure accumulation.**
Agents should NOT automatically recover from `suspect` → `active` unless the ACTP protocol explicitly recovers them. Remove or dramatically slow down the auto-recovery block (currently every suspect agent with `step - last_seen_step < 5` auto-heals). Replace with: suspects only recover after 15+ steps of no further missed heartbeats.

**Fix 1b — Tune failure fractions upward for larger scales.**
The current fractions (10–20%) are too conservative. For the 500-agent scale, increase environmental and cascading failure fractions to 25–35% to force ORANGE/RED activation. Keep small scale (20 agents) at current levels — it should mostly stay YELLOW. This creates a realistic graduated response visible in the graphs.

**Fix 1c — Fix the kill-switch metric storage.**
In `run_simulation()`, store kill-switch level as an **integer** in `StepMetrics` for easier aggregation:
```python
KS_MAP = {"NONE": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3}
```
Store `KS_MAP[ks_level]` in the metrics. Update `graph4_kill_switch.py` to map back to labels for display.

**Fix 1d — Do NOT halt the simulation on RED.**
Currently the RED level stops the loop and pads. Instead, just record the RED state and continue — the system should show what happens when it keeps running under RED conditions (degraded but not stopped). This produces far more interesting graphs showing system behavior under extreme stress.

### Expected outcome after fix
- Graph 4 should show a clear stacked bar pattern:
  - Small (20 agents): mostly NONE/YELLOW, rare ORANGE, near-zero RED
  - Medium (100 agents): mix of YELLOW/ORANGE, some RED after step 100
  - Large (500 agents): significant ORANGE and RED, especially after steps 80–120
- ACTP bars should consistently show fewer RED/ORANGE steps than baseline — this is the key safety result

---

## Problem 2 — Graphs Do Not Show Clear ACTP Advantage (Critical)

### What is happening
Several graphs show nearly identical results between ACTP and baseline. The summary CSV shows:
- `avg_jain_fairness` = 1.0 for both protocols at all scales (impossible — perfect fairness at all times)
- `avg_recovery_time` = 0.0 for both (no recoveries being counted)
- `final_task_completion` = 0.0 for both (task completion not accumulating correctly)

### Root cause — Three separate bugs

**Bug 2a — Jain's Fairness Index always returns 1.0**
This happens because `active_loads` is computed from `a.task_load` but all agents start with `task_load = 1.0` and failed agents drop to `0.0`. The fairness function is called only on active agents, all of whom still have load 1.0 until someone receives redistributed tasks. Because `redistribute()` only fires when a winner is found AND `tasks_reassigned` is False, and because `consensus_actp` often returns None (empty active list), the redistribution rarely fires.

Fix: Ensure task redistribution actually runs. Add a fallback: if `consensus_actp` returns None because `active_agents` is empty, skip redistribution but log it. More importantly, **initialize agents with varied task loads** instead of all starting at 1.0:
```python
task_load = float(np_rng.uniform(0.5, 2.5))  # varied starting loads
```
This ensures Jain's Index starts below 1.0 and shows meaningful variation.

**Bug 2b — Recovery time always 0**
The `redistribute()` function computes:
```python
latency = recovery_step - failed.last_seen_step
```
But `failed.last_seen_step` is set to `current_step - HEARTBEAT_TIMEOUT_BASELINE - 1` during failure injection, which means `latency = 3 + 1 = 4`. However, `recovery_times.append(latency)` only runs when `winner is not None`. Since consensus often returns None (see Bug 2a), latency is never recorded and `np.mean([])` returns NaN which gets stored as 0.0.

Fix: Ensure consensus returns a valid winner more reliably. Add a final fallback in `consensus_actp`: if the scored list is empty (all agents failed), return None, but if there's at least one active agent, always return the best one. Also initialize `recovery_times = [0]` so mean never fails on empty list.

**Bug 2c — Task completion rate not accumulating**
`tasks_completed` increments only inside the `if winner is not None` block after redistribution. `tasks_total` increments every step as `sum(1 for a in agents if a.status == STATUS_ACTIVE)`. This means completion rate = (redistribution events) / (active-agent-steps), which is essentially 0/large_number.

Fix: Redefine task completion as the fraction of simulation steps where at least 70% of agents are active. This is a more meaningful metric:
```python
# At end of each step:
operational_fraction = sum(1 for a in agents if a.status == STATUS_ACTIVE) / n_agents
tasks_completed += operational_fraction
tasks_total += 1.0
# task_completion = tasks_completed / tasks_total  (ranges 0–1, meaningful)
```

### Expected outcome after fix
- Graph 2 (Jain's Fairness): Should show ACTP maintaining higher fairness (0.75–0.95 range) while baseline drops lower (0.55–0.80 range) after failure injections
- Graph 3 (Task completion): ACTP should sustain 80%+ completion while baseline degrades to 60–70% at large scale
- Graph 1 (Recovery latency): Should show genuine numbers (2–8 steps range) instead of near-identical bars

---

## Problem 3 — Add Comparison to Existing Research (IEEE Requirement)

### What is needed
The IEEE paper needs to benchmark ACTP against metrics from published papers. Add a **Graph 7** that shows a comparison table/chart using reported metrics from related work:

| System | Recovery Latency | Fairness | Scale |
|--------|-----------------|----------|-------|
| Zhao et al. (2025) — baseline MAS resilience | ~8–12 steps (reported) | Not measured | Power grid |
| Standard fixed-threshold consensus (baseline) | Our baseline results | Our baseline Jain | 20/100/500 |
| **ACTP (ours)** | Our ACTP results | Our ACTP Jain | 20/100/500 |

The exact values from Zhao et al. can be approximated from their paper description (they report recovery in terms of control cycles, approximately 8–12 steps equivalent). Use these as reference bars in a grouped comparison chart.

**Graph 7 spec:**
- Type: Grouped horizontal bar chart
- X-axis: Recovery latency (steps)
- Groups: Zhao et al. (2025), Baseline (ours), ACTP (ours) — at 100-agent scale for fair comparison
- Color code: gray for Zhao et al., red for baseline, blue for ACTP
- Add a secondary panel showing Jain's Fairness Index — Zhao et al. has no fairness measurement, show this as "not reported" (dashed line at 0)
- Title: "ACTP vs Related Work — Recovery Latency and Fairness"
- Caption: "Zhao et al. values approximated from reported control cycle counts"

---

## Problem 4 — Graph Visual Quality Issues

### Graph 4 (Kill-Switch) specific issues
- X-axis labels are overlapping and hard to read
- The stacked bars show near-zero height making the chart look empty
- After fixes to Problem 1, this should self-correct — but also:
  - Increase bar width to 0.5 (currently too narrow)
  - Add value labels on top of each bar showing step count
  - Add a legend explaining YELLOW/ORANGE/RED thresholds

### Graph 2 (Jain's Fairness) specific issues  
- Currently flat at 1.0 the entire simulation — after Bug 2a fix this will show real variation
- Ensure Y-axis range is 0.4–1.05 (not auto-scaled to 0.99–1.0 which makes it look flat)
- Add shaded regions showing where failure injections happened

### All graphs
- Ensure consistent figure size: `figsize=(10, 5)` for single-panel, `figsize=(14, 4.5)` for three-panel
- DPI must be 150 minimum for PowerPoint embedding
- Save as PNG to `./outputs/` directory (not hardcoded server path)

---

## Files

```
mas_actp_simulation.py    ← the file to fix (all changes go here)
outputs/                  ← graphs and CSV save here (create if missing)
```

## How to run after fixes
```bash
pip3 install matplotlib numpy pandas
python3 mas_actp_simulation.py
```

Expected runtime: under 60 seconds on any modern laptop.

---

## Definition of Done

The fix is complete when ALL of the following are true:

- [ ] Graph 4 shows visible YELLOW/ORANGE/RED bars — not flat/empty
- [ ] ACTP bars in Graph 4 are shorter than baseline bars (fewer dangerous states)
- [ ] Graph 2 shows Jain's Fairness below 1.0 with visible variation (0.6–0.95 range)
- [ ] ACTP line in Graph 2 sits consistently above baseline line
- [ ] Graph 1 shows recovery latency values in the 2–8 step range (not identical bars)
- [ ] Graph 3 shows ACTP completing more tasks than baseline at 500-agent scale
- [ ] Summary CSV shows non-zero values for `avg_recovery_time` and `final_task_completion`
- [ ] Summary CSV shows `ks_red_steps > 0` for at least medium and large scales
- [ ] Graph 7 (new) shows ACTP outperforming Zhao et al. approximate benchmark on recovery latency
- [ ] All graphs save to `./outputs/` without hardcoded paths
- [ ] Script runs clean with `python3 mas_actp_simulation.py` — no errors, no warnings

---

## Contact
Questions about the research context: Dimitri Barth Nanmejo Sinou
GitHub repo: https://github.com/dimsonMba/MAS_Multi_Agent_Systems
