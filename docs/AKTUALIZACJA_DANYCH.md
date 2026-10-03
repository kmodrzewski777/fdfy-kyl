# Aktualizacja danych — Insights @ RetentionQ (Foodify)

**Rule: all of the dashboard's logic is coded in. When refreshing, the LLM does not interpret or calculate anything by hand.**
A refresh is three steps:
1. Fetch raw data from Customer.io into `refresh/raw.json`.
2. Run `python3 refresh/build.py`.
3. Save the snapshot to the DB and publish.

```
queries.json ──(MCP Customer.io)──▶ raw.json ──build.py──▶ snapshot.json + dashboard/foodify-retencja.html
```

| File | Role |
|---|---|
| `refresh/queries.json` | `[key, filter]` list of every count (about 224). Do not edit during a refresh. |
| `refresh/raw.json` | ONLY raw API results. The only file the LLM fills in. |
| `refresh/sample.jq` | jq that collapses one page of purchase logs into one `sample` row. |
| `refresh/build.py` | All the logic: raw → every number, chart and table. Checks completeness: on `Brak liczników…`, fetch the missing ones. |
| `refresh/snapshot.json` | The output, which is also the template: fields build.py does not compute pass through unchanged. |
| `dashboard/foodify-retencja.html` | Artifact source. build.py replaces `let APP=`, `EMR=`, `APPR=` and the embedded `try{applyData({…})`. |

Artifact: `https://claude.ai/artifact/B25KPWGfbtcg3LzJjiyY2B`
DB doc: `snapshot/current`. Always write it with `if_version`.
Customer.io workspace: `190673`
Tool: `mcp__Customer_io_Pstryk__cio_read_api`

---

## 1. Procedure (minimum tokens)

1. **Counts.** For each `[k, f]` in `queries.json`:
   - Call `GET /v1/environments/190673/customers` with `params={"filters": base64(compact_json(f)), "limit":1}` and `jq=".meta.pagination.total"`.
   - Generate the base64 with a script: `python3 -c "import json,base64;[print(k,base64.b64encode(json.dumps(f,separators=(',',':')).encode()).decode()) for k,f in json.load(open('refresh/queries.json'))]"`.
   - Make the calls **in parallel, about 25–40 at a time**. Append results to the file straight away as `counts[k]=n`. Never copy filters by hand.
   - Filters support only `and`/`or`/`not` + `segment`, so everything is built on segments.
   - Shortcut: if `appr.R5.0 == 0`, then `appr.R5.1..9 = 0` too.
2. **Purchase sample** (`raw.sample`): 14 rows, one per day, covering the last 14 full days.
   - Call `GET /v1/environments/190673/logs` with `type=event`, `name=purchase`, `limit=50`, `jq=refresh/sample.jq`. One page per day is enough.
   - **`continuation` ignores the from/to window**, so pick the day by `timestamp`.
   - Row fields: `{day,n,d,v,dv,t,ex,cb,tu,nu,codes,w,o,src,dd}`.
3. **`purchases_yesterday`**: the full count of yesterday's purchases. Page through yesterday's logs and add the pages up (example: 50+50+50+50+45 = 245).
   - Do not use `event_names/purchase.daily_count`: it counts today, which is incomplete.
4. **`lead_series`**: `GET /metrics/segment_membership` for segment **551**, `resolution=days`, last 31 days. `e` = entered, `l` = left, `hist` = segment size.
5. **`push_monthly`**: `/metrics/all_deliveries?version=2&res=months`, filtered to `type=="push"`.
   - Full months only (drop the current one).
   - Fields: `lab`, `s` (sent), `d` (delivered), `o` (opened), `cv` (converted).
6. **`camp`**: `/campaigns/{157,158}/channel_metrics?period=days`. `steps` is ignored and 45 days come back; sum the days since the 800+ program started (28 Sep).
   - `157.email = [delivered, opened, clicked, converted]`
   - `158.push = [delivered, opened, null, converted]`
7. Set `raw.asof` to today's date and run `python3 refresh/build.py`.
8. Save the DB: `ArtifactData set snapshot/current file_path=refresh/snapshot.json if_version=<latest>`.
9. Copy `dashboard/foodify-retencja.html` to the scratchpad. Run a Playwright test (expect 0 `pageerror`). Then `Artifact publish` with `url`.
10. Commit and push.

## 2. Count dictionary (queries.json)

Segments:
- `157`: app users
- `551`: leads
- `642..648`: order ladder (`642` = 1 order … `648` = 10+)
- `649/650/651`: eating now (650+651 = ends within 7 days)
- `655–657`: inactive
- `143/145/146/147/149`: RFM R1..R5
- `616`: sunset
- `51`: email OK
- `662–664, 682–684`: LTV buckets (LTV)
- `636`: 800+ members

| Key | Filter | Where in the dashboard |
|---|---|---|
| `app.users/ios/android/op30/op7/pushCons/pushReach/buyApp30/buyWeb30/buyAppEver/buy30` | seg 157/737/738/709/736/523/198/733/734/735/676 | APP tiles |
| `app.clients` / `app.clNo` | 157∧CL / ¬157∧CL (CL = or 642..648) | APP.cmp.cl |
| `app.eat` / `app.eatNoApp` / `app.inact` / `app.o4` | 157∧ACT / ¬157∧ACT / 157∧or655–657 / 157∧O4 | APP |
| `app.ltvA.X` / `app.ltvN.X` | 157∧X / ¬157∧X, X∈LTV | APP.cmp.ltvB |
| `app.ordA.X` / `app.ordN.X` | 157∧X / ¬157∧X, X∈642..648 | APP.cmp.ordB; A+N for 648 = ladder 10+ |
| `lead.*` | 551∧{537 open30, 552 click30, 549 atrisk, 425 sunCand, 616 sunsetted, 429 remove, 71 sms, 523 push, 157 app, 54 cart, 59 checkout, 100 engaged} | LEAD |
| `lad.2..6`, `lad.ge6` | or(642..648), or(643..648), …, or(647,648) | STATIC.ladder ≥1…≥6 and STATIC.life[0..1] |
| `seg.658..661` | time between orders | STATIC.gap |
| `seg.671,672,675,673,674` | JJC, Wybór z Menu, Gotowe Diety, Kids, Foodpack | STATIC.prod |
| `seg.act`, `seg.end7` | or649–651, or650–651 | STATIC.life[3..4] |
| `p8.disc/w13/w45` | 636∧698, 636∧or692–694, 636∧or695–696 | P8 |
| `emr.G` | G∧51∧¬616 | EMR |
| `appr.G.j` | G∧157∧[—,650,651,ACT,652,653,654,655,656,657][j] | APPR (CHA=648, LOY=or645–647, POT=or643–644, NEW=642, R1..R5) |
| `ltv.G.X` | G∧X | RAW.rfm/loy[].ltv |

## 3. What build.py computes from the sample

**RB:**
- `n, d, v, dv`: sums over the 14 days.
- `codes`: top 10 codes; the percentage comes from the code's suffix.
- `loy`: [n, d] by how many orders the customer has (1 / 2–3 / 4+).
- `w[k][4..7]`: [n, d, v, dv] per `wealth_index`.
- `perDay`: `purchases_yesterday`.

**CB:**
- `n`, `nu` over the last 6 days. `nu` = orders with `spent_wallet_cashback > 0`.
- `perDay`: `purchases_yesterday`.

**STATIC:**
- `days`: diet length (end − start + 1) in buckets 1 / 2–4 / 5–9 / 10–19 / 20+. `daysC` is the median.
- `pay`: share of value paid externally (`spent_external`), with cashback+FoodiKarta, and with 800+ top-up (`spent_top_up`).
- `payC`: AOV = `v/n`.

**APP.cmp.ord/val/code:** order count, value and orders with a code, app (ios|android) vs web, over the last 6 days.

## 4. Not yet covered by build.py

These are updated by hand, following `docs/SZCZEGOLY_ZRODEL.md`.

| Element | When |
|---|---|
| `FLOWS`, `NCR`, `NK`, `WT`, `DMAP`, `CHURNP`, `SER`, `CHURN.d`, `RB.days`, `CB.days` | daily. **TODO: move into build.py** (raw: `membership[seg]`, daily logs) |
| `CHURN.wk`: seg 531, weekly resolution (weeks start Thursday), full weeks only | weekly |
| `MOM`: calendar-month comparison | on the 1st of the month |
| `NCSEC`: paging over 643 customers with a first order in the last 30 days | monthly |

## 5. Gotchas

- In the HTML, search for `try{applyData({` (`try{applyData(d)` appears earlier). build.py does this itself.
- `attribute_change … within` in segments is ignored, so RFM transitions cannot be counted with segments.
- This org does not allow connectors on Routines, so the "Zaktualizuj" button cannot run anything automatically. An LLM refreshes using this guide.
- `goal_refresh` that returns `p:true`: poll again.
