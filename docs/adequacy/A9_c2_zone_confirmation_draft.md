# A9 – C2: confirmation without the epicentral zone of the 2025-12-06 M6.8 (draft addendum)

Status: **eingefroren am 2026-10-26** mit dem zweiten Nachtrag (`PREREGISTRATION_v0.2_NACHTRAG_2.md`, `results/frozen_v04_addendum_2026-10-26.json`). Verbindlich sind der Nachtrag und die JSON; diese Datei ist die eingefrorene Begründung.

- Decision on the content: Johann Römer, 2026-10-23 (chat), after AP6c run 2 (`99ef046`).
- The freeze happens together with A8 in one dated addendum (second Nachtrag to
  `PREREGISTRATION_v0.2.md`), **before 2027-01-01**, with SHA-256 values in the addendum JSON.
- Machine-readable draft: `results/adequacy/c2_zone_spec.json`.
- Code: `etas_adequacy/zone_check.confirm_c2`.

## A9.1 Rule

The preregistered C2 statistic, its α levels (0.01 at the look ending 2029-12-31, 0.04 at the look
ending 2036-12-31), the baselines and A1–A8 stay **unchanged**. A9 only adds a condition for
interpreting a rejection:

> A rejection of C2 at a look counts as **confirmed** only if the **reduced statistic** has a
> one-sided p below the α of the same look. The reduced statistic is C2 computed with three
> differences:
> - the glacier region SE_Alaska_AK **without** the disc of radius **55 km** around the epicentre
>   of the M6.8 of 2025-12-06 20:41:51 UTC (60.3503° N, 139.3591° W; ComCat ak);
> - the **reduced baseline** log µ_ref = **3.99831**, σ_y = **0.38896**;
> - the control region and everything else unchanged.
>
> An unconfirmed rejection is reported as "C2 rejects, not confirmed outside the 2025 sequence
> zone" and does not count as support for H2/C2.

Distances are great-circle distances (`catalog.haversine_km`, R = 6371 km). Events at exactly
55 km count as outside.

## A9.2 Why

The M6.8 of 2025-12-06 in the glacier region produced 2,415 events ≥ Mc in its first 25 days. The
frozen ETAS cannot describe this sequence.

1. **AP5** (`sequence_tail.md`): if the tail decayed like 1/t, C2 would reject wrongly in most
   replicates.
2. **AP6** (`sequence_term_deviation.md`): the 2026 data show a much faster decay; an extra
   Omori term cannot be identified.
3. **AP6b** (`sequence_level.md`): the unchanged C2 is fine without an excess. A slowly decaying
   excess of 75–150 events/yr mimics the sought signal (false rejection up to 0.17 / 0.50).
   Whether such an excess exists cannot be decided from the 2026 data.
4. **AP6c** (`sequence_zone.md`): with this confirmation rule, the joint false-alarm rate stays
   at **0.007–0.018** in all calibrated scenarios (criterion ≤ 0.02 / ≤ 0.08). Power for a 50 %
   increase of the background falls only from 0.145 / 0.695 to **0.130 / 0.677**.

## A9.3 How the zone and the reduced baseline were fixed

- **Radius:** the 95 % quantile of the epicentral distances of the sequence events ≥ Mc from day
  2 to 2025-12-31 (frozen 2016–2025 snapshot only) is 51.44 km, rounded up to the next 5 km,
  giving 55 km.
  - The zone held 4.1 % of the events of 2016 to November 2025 and 81 % of the 2026 events up to
    2026-10-21.
  - The 2017 M6.2/6.3 is 159 km away and is not excluded. Its tail after 10 years is negligible
    (AP5 analog).
- **Reduced baseline:** relative to the frozen one, so that differences of method cancel.
  - Yearly log µ 2016–2025 with the frozen triggering are computed (`yearly_log_mu`) on the
    frozen snapshot, once for the full region and once without the zone.
  - log µ_ref,red = log µ_ref + mean(ly_red) − mean(ly_full) = 4.04662 − 0.04831 = 3.99831.
  - σ_y,red = σ_y · sd(ly_red)/sd(ly_full) = 0.38896.
- **Data from 2026** (AP6 snapshot to 2026-10-22, SHA in `snapshot_2026.json`) were used only to
  describe the sequence and to calibrate the simulation, **not** to set the radius or the
  baseline. Nothing from 2027 on was used.

## A9.4 Known limitations

- The zone is a disc around the mainshock epicentre, not the rupture geometry. AP6c assumes that
  95 % of the remaining excess lies inside. With 30 % outside (stress test) the joint false alarm
  rises to 0.037 / 0.095.
- Small upward offset of the reduced statistic without any excess in AP6c (D_red +0.06 at look 1,
  cause not examined). It does not affect the rule.
- AP6c simulates the inside and outside of the zone as separate processes without cross-zone
  triggering. A first run with independently drawn zone labels was biased and is documented as
  deviation D1 (`sequence_zone_run1.md`).
- The A4 operating rules apply unchanged to the reduced statistic: snapshot archiving, Mc
  homogeneity, the 2026 lead-in as triggers only, and numerics.

## Freeze steps (done 2026-10-26, Johann's decision)

- [x] Final text (A8 + A9 in one second Nachtrag), without the status ENTWURF.
- [x] `results/adequacy/c2_zone_spec.json` with status "frozen" and its SHA-256 in the addendum
      JSON.
- [x] A code tag that includes `zone_check.confirm_c2` (A4.6: reproduction of the released code).
