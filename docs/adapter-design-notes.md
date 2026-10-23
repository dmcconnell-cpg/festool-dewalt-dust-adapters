# Festool 27mm ↔ Dewalt DW735 adapter — design notes

Printable friction adapter: **Festool CT MIDI II 27 mm twistlock hose** ↔ **Dewalt DW735 / DW735X planer dust stub**.

## Tool models

| End | Model / interface |
| --- | --- |
| Hose | Festool **CT MIDI II**, **27 mm** antistatic hose with twistlock collar — **not** the D36 / 36 mm hose |
| Planer | **Dewalt DW735** (and DW735X); mates to the true chip-ejection stub, not the optional 4″ round collector sleeve |

## Key dimensions

### Festool 27 mm twistlock (from reference STL)

Source mesh: `internal/Festool_27mm_HoseConnector.stl` (boolean-unioned into the print; not reinvented).

Measured on that mesh:

| Feature | Value |
| --- | --- |
| Overall height | 30 mm |
| Outer diameter | 40 mm |
| Bore ID (air path through sleeve) | ~36 mm |
| Twistlock | 3 internal bayonet lugs @ ~120°, lug nose ~r 16.5 mm, active ~Z 16–24 mm in the reference frame |

**Naming note:** Festool’s “27 mm” is the hose class (MIDI). The sleeve bore is larger (~36 mm ID) — that is airflow through the 27 mm twistlock connector, **not** a 36 mm hose interface.

**Hose-side assumption:** Reference **Z = 30** faces the hose (lug chamber entered from that open end). Reference **Z = 0** is joined to the reducer toward the Dewalt socket.

### Dewalt DW735 socket

| Parameter | Value |
| --- | --- |
| Primary fit target (user) | **61.50 mm** stub OD |
| Socket ID (confirmed fit ring) | **62.80 mm** (**+1.30 mm** clearance) |
| Socket depth | **25 mm** |
| Lead-in | ~1.5 mm deep flare to **64.80 mm** ID at the mouth |
| Wall thickness | **2.5 mm** → socket OD **67.80 mm** |
| Transition | 22 mm loft, 62.80 ID / 67.80 OD → 36 ID / 40 OD |

### DW735 community / commercial cross-checks

- **PortMatch** (DW735 true port): stub OD ≈ **62 mm** (2-7/16″); stock round port is for ~4″ / 100 mm hose (~3-15/16″).
- **ToolCurve** DW735 adapter (tool end): ID **61.50 mm** (base) → **62.56 mm** (top), OD 67 mm — tapered friction fit.
- Official DW735 manual: removable round dust port for 4″ (100 mm) collector; chips leave through the smaller true stub.

Shop fit-test locked socket ID at **62.80 mm** (+1.30 vs 61.50 OD). Straight and 90° adapter STLs regenerated to match.

## How it was generated

1. Measured the Festool reference with `trimesh` / ray probes (extents, bore, lug sectors).
2. Built Dewalt socket + conical transition in **build123d**.
3. **Manifold boolean union** with the translated Festool reference mesh.
4. Verified watertight mesh, open bore both ends, socket ID ≈ 61.79 mm, Festool lugs preserved.

Parametric source: `internal/festool-dewalt-dw735-adapter.py`  
Output STL: `docs/festool-27mm-to-dewalt-dw735-61.5mm-adapter.stl`

---

## 90° elbow variant

Same Festool 27 mm / DW735 fits, with a **90° bend leaving the planer** so the hose can run sideways/up instead of straight back.

| Parameter | Value |
| --- | --- |
| Dewalt socket | Same: **62.80 mm** ID, 25 mm deep, +1.30 clearance |
| Mid bore through elbow | **48 mm** ID / **53 mm** OD (keeps chips moving in the bend) |
| Elbow centerline radius | **42 mm** |
| Festool end | Same reference mesh, aimed **+X** after the bend |
| Overall size | ~135 × 67 × 112 mm |

**Path:** DW735 socket (+Z) → 18 mm reduce to mid → 90° elbow (lofted circular sections) → short mid straight → reduce to Festool → twistlock sleeve.

**Fix note:** An earlier torus+box clip sliced the elbow at the bend centerline and removed the outer wall. Regenerated with a full centerline loft so the outer radius is intact.

Parametric source: `internal/festool-dewalt-dw735-adapter-90deg.py`  
Output STL: `docs/festool-27mm-to-dewalt-dw735-61.5mm-adapter-90deg.stl` (~1.9 MB, watertight)

### Print tips — 90° (Bambu)

- **Orientation (preferred):** Dewalt socket flat on the bed (same as straight). Festool arm cantilevers sideways — enable **tree supports** under the horizontal arm / elbow underside.
- **Alternate:** Lay the bend plane flat on the bed (side of elbow down) for fewer supports; brace the socket ID against elephant foot.
- **Material / walls:** Same as straight — **PETG**, ≥3 walls, ≥25% infill.
- **Fit:** Identical socket ID to the straight adapter.

## Fit-test rings (shop iteration)

All rings slide **over** the tool male stub. Height **6.35 mm** (¼″), wall 2.5 mm. Print flat on bed, PETG.

| Tool | Stub OD | Ring ID | Notes | STL |
| --- | --- | --- | --- | --- |
| **DW735** planer | 61.50 mm | **62.80 mm** | Confirmed fit — adapters updated to match | `docs/dewalt-dw735-61.5mm-fit-test-ring.stl` |
| **DWS779** miter | 42.33 mm | **42.23 mm** | −0.5 mm vs prior 42.73 (that size was tight / fit guard instead) | `docs/dewalt-dws779-42.33mm-fit-test-ring.stl` |
| **DWE7491** rear | 63.51 mm | **65.41 mm** | Locked — straight + 90° adapters match | `docs/dewalt-dwe7491-rear-63.51mm-fit-test-ring.stl` |
| **DWE7491** blade guard | ~42.3 mm class | **42.73 mm** | Prior miter ring fitted the guard | `docs/dewalt-dwe7491-blade-guard-fit-test-ring.stl` |

DW735 and DWS779 full adapters match their locked rings. DWE7491 rear adapters match **65.41 mm**.

## Print tips (Bambu Lab) — straight

- **Orientation:** Dewalt socket flat on the bed (largest ring down). Festool twistlock points up. No rotation needed.
- **Supports:** None expected — vertical tube, walls ≥2.5 mm, chamfer only at bed.
- **Material:** **PETG** preferred (chip heat / impact); ABS/ASA fine in an enclosure. Avoid brittle PLA for planer chips.
- **Settings (starting point):** 0.20 mm layer, ≥3 walls, ≥25% gyroid/cubic infill, 0.4 mm nozzle. Outer wall first optional for dimensional accuracy on the ID.
- **Fit:** If too tight, light sand the socket ID or reprint with +0.1 mm ID. If loose, wrap the DW735 stub with a turn of electrical tape or reprint tighter.

## Output check — DW735

| Check | Straight | 90° |
| --- | --- | --- |
| Manifold / watertight | Yes | Yes |
| Dewalt socket ID | **62.80 mm** (~62.79 verified) | same |
| Clearance vs 61.50 mm | **+1.30 mm** | same |
| Overall size | ~67.8 × 67.8 × 75 mm | ~135 × 68 × 112 mm |

---

## Dewalt DWS779 miter saw

Festool **CT MIDI II 27 mm** twistlock ↔ **Dewalt DWS779** rear dust stub (also fits DWS780 / similar ports).

| Parameter | Value |
| --- | --- |
| Stub OD (shop) | **42.33 mm** |
| Socket ID (confirmed fit ring) | **42.23 mm** (**−0.10 mm** vs OD — snug friction) |
| Socket depth | **25 mm** |
| Lead-in | 1.5 mm flare to **44.23 mm** ID |
| Wall | **2.5 mm** → socket OD **47.23 mm** |
| Transition | 18 mm loft → Festool 36 ID / 40 OD |

Shop note: earlier **42.73 mm** ring was tight / matched the DWE7491 blade guard instead; miter locked at **42.23 mm**. Straight and 90° adapters regenerated to match.

| File | Path |
| --- | --- |
| Straight adapter | `docs/festool-27mm-to-dewalt-dws779-42.33mm-adapter.stl` |
| 90° elbow adapter | `docs/festool-27mm-to-dewalt-dws779-42.33mm-adapter-90deg.stl` |
| Fit-test ring (¼″) | `docs/dewalt-dws779-42.33mm-fit-test-ring.stl` |
| Straight source | `internal/festool-dewalt-dws779-adapter.py` |
| 90° source | `internal/festool-dewalt-dws779-adapter-90deg.py` |
| Ring source | `internal/dewalt-dws779-fit-test-ring.py` |

### DWS779 90° variant

Same **42.23 mm** socket. Mid bore **38 mm** ID through a **36 mm** centerline-radius lofted elbow; Festool sleeve exits sideways. Outer-wall loft (same method as the fixed DW735 90°).

Print: socket on bed, tree supports under the cantilevered Festool arm, PETG. Print the fit ring first.

---

## Dewalt DWE7491 table saw

Rear main stub measured **63.51 mm OD** (~60 mm = bore ID). Socket locked from fit ring at **65.41 mm** ID (+1.90 vs OD). Blade-guard accepts the **42.73 mm** ID ring.

| File | Path |
| --- | --- |
| Straight adapter | `docs/festool-27mm-to-dewalt-dwe7491-63.51mm-adapter.stl` |
| 90° elbow adapter | `docs/festool-27mm-to-dewalt-dwe7491-63.51mm-adapter-90deg.stl` |
| **Dual-port** (rear + guard branch) | `docs/festool-27mm-to-dewalt-dwe7491-dual-port-adapter.stl` |
| Branch cap (close when no guard) | `docs/dewalt-dwe7491-branch-cap.stl` |
| Guard → hose coupler | `docs/dewalt-dwe7491-blade-guard-hose-coupler.stl` |
| Straight / 90° / dual sources | `internal/festool-dewalt-dwe7491-*.py` |

### Dual-port + 1.5″ hose

POWERTEC 1-1/4″ kit is too small for this use. Target hose: **1-1/2″ ID** clear dust hose (e.g. Amazon B0DRVK9PGP), cut to length, hose clamps included with that listing.

| Interface | Size |
| --- | --- |
| Rear socket | **65.41 mm** ID (same as locked fit ring) |
| Festool end | 27 mm twistlock (reference mesh) |
| Guard branch | male stub **37.8 → 38.4 mm** OD (~1.5″) — hose slides **over**, clamp |
| Cap | **38.7 mm** ID friction cup; enlarged flange tab with **4 mm** hole for tether chain |
| Dual-port tether | matching **4 mm** hole on a fin above the branch neck (chain between cap ↔ adapter) |
| Guard coupler | **42.73 mm** ID (proven on guard) → same 1.5″ male stub |

Workflow: coupler on blade guard → short 1.5″ hose → branch stub on dual adapter; Festool hose on top; cap the branch when not using the guard. Print dual adapter socket-down (supports under side branch). Cap and coupler flat on bed.
