# Aktualizacja danych — Insights @ RetentionQ (Foodify)

**Zasada:** cała logika dashboardu jest zakodowana w `refresh/build.py`. LLM przy aktualizacji niczego nie liczy ani nie interpretuje. Pobiera tylko surowe wyniki z Customer.io (według listy z `plan.py`), zapisuje je do `raw.json` przez `put.py` i uruchamia `build.py`.

```
plan.py ──▶ (wywołania MCP Customer.io) ──put.py──▶ raw.json ──build.py──▶ snapshot.json + dashboard/foodify-retencja.html
```

| Plik | Rola |
|---|---|
| `refresh/queries.json` | 486 liczników `[klucz, filtr]`. Nie edytować. |
| `refresh/plan.py` | Wypisuje **dokładnie** wywołania potrzebne na dziś (pomija to, co już jest w `raw.json`). |
| `refresh/put.py` | Jedyny sposób zapisu do `raw.json`. Serie dzienne i metryki kampanii scala po datach, więc historia zostaje. |
| `refresh/raw.json` | Tylko surowe dane z API plus skumulowana historia (członkostwo segmentów, cele kampanii, próbki zamówień). |
| `refresh/sample.jq` | jq: jedna strona logów zakupów → jeden wiersz próbki. |
| `refresh/build.py` | Przelicza **wszystko**: snapshot oraz stałe w HTML (`APP`, `EMR`, `APPR`, `NK`, `NCSEC`, `CHURNP`, `WT`, `NCR`, `DMAP`, `FLOWS`, `renderNC t0`, osadzony `try{applyData({…})`). Przy brakach przerywa i wypisuje, czego brakuje. |
| `refresh/snapshot.json` | Wynik. Jest też szablonem dla nielicznych pól statycznych (sekcja 5). |
| `dashboard/foodify-retencja.html` | Źródło artefaktu. |

Artefakt: `https://claude.ai/artifact/B25KPWGfbtcg3LzJjiyY2B`. Baza: `snapshot/current` (zapis z `if_version`). Workspace Customer.io: `190673`. Narzędzie: `mcp__Customer_io_Pstryk__cio_read_api`.

## 1. Procedura codzienna

```
python3 refresh/plan.py --reset      # nowy dzień: czyści liczniki i strony klientów, ustawia asof = dziś
python3 refresh/plan.py              # lista wywołań (uruchamiaj ponownie, pokazuje tylko braki)
...wykonaj wywołania, każdy wynik zapisz:  python3 refresh/put.py <ścieżka> '<wynik>'
python3 refresh/build.py             # OK albo lista braków
```

Potem:
1. `ArtifactData set snapshot/current file_path=refresh/snapshot.json if_version=<ostatnia>`.
2. Skopiuj `dashboard/foodify-retencja.html` do scratchpada i zrób test Playwright (0 błędów `pageerror`).
3. `Artifact publish` z `url` artefaktu.
4. Commit i push.

Typy linii w `plan.py`:

| Linia | Co | Zapis |
|---|---|---|
| `C klucz b64` | `GET /customers`, `filters=b64`, `limit=1`, `jq=.meta.pagination.total` | Zbieraj w paczki: `put.py counts '{"klucz":n,...}'` |
| `M seg start ts_start ts_end jq=…` | `segment_membership`, `resolution=days` (domyślnie ostatnie 8 dni) | `put.py membership/<seg> '{"start":"<start>","v":<wynik>}'` |
| `W 531` | `segment_membership`, `resolution=weeks` od 2026-07-09 | `put.py membership_weeks/531 '{"start":"2026-07-09","e":[…],"l":[…]}'` |
| `S dzień` | logi zakupów z dnia (1 strona, `jq=sample.jq`) | `put.py sample/<dzień> '<wynik + "day">'` |
| `P active_pages / sec_pages` | wszystkie strony klientów (649 oraz 643∧820), jq podany w planie | `put.py active_pages/<p> '<wynik>'` |
| `K kampania okres` | `/campaigns/<id>/metrics` (dni: 8, tygodnie: 12, miesiące: 13) | dni: `put.py flows/metrics/<id>/d '{"end":"<dziś>","v":<wynik>}'`, w/m: `put.py flows/metrics/<id>/w '<wynik>'` |
| `G dzień` | `goal_refresh` dla celów 2, 7, 10, 11, suma per kampania (`p:true` = ponów) | `put.py flows/goals/<dzień> '{"<cid>":[liczba,przychód]}'` |
| `X` | push miesięcznie (`all_deliveries`), `channel_metrics` kampanii 157/158 | `push_monthly`, `camp` |
| `purchases_yesterday` | wszystkie strony logów z wczoraj, licz po `timestamp` | `put.py purchases_yesterday N` |

Jak oszczędzać tokeny:
- Wywołania MCP puszczaj równolegle, po 25–40 naraz.
- Wyniki zapisuj od razu, w paczkach.
- Nie przepisuj ręcznie filtrów: kopiuj je z `plan.py`.
- Jeśli kilka kluczy ma identyczny filtr, wystarczy jedno wywołanie. Przykład: `lb.buy1` = `lb.ev1`, `buy2` = `pg2`, `buy3` = `pg1`, `buy4` = `pg8`, `buy5` = `ev8`.
- Gdy `appr.R5.0` = 0, pozostałe `appr.R5.*` też są 0.

## 2. Co skąd (słownik)

Segmenty:
- 157: aplikacja
- 551: leady
- 642..648: klienci według liczby zamówień (642 = 1, 648 = 10+)
- 649/650/651: jedzą teraz (650 = koniec za 0–3 dni, 651 = za 4–7 dni)
- 652–657: dni od końca dostaw (0–7, 8–14, 15–30, 31–60, 61–90, 90+)
- 814–818: koniec dostawy za 8–14, 15–21, 22–30, 31–60, 61–90 dni
- 143/145/146/147/149: RFM R1..R5
- 685: flaga churn
- 531: nieaktywni (seria)
- 636/689/688/687/686/690/639: program 800+
- 720–732: cashback
- 701–719: zdarzenia i strony leadów (30 dni)
- 692–696: majętność 1–5
- 698/700: zakup z rabatem (kiedykolwiek / 3+ razy)
- 781–830: zakup w k dni
- 822–829: 2+ zakupy w k dni
- 831–836: churn per okres

| Element dashboardu | Źródło w raw | Logika w build.py |
|---|---|---|
| Karty segmentów (`RAW.rfm/loy`: tot, r[0..8], ltv, hist/e/l) | `raw.G.*`, `ltv.G.*`, membership 143–149 | r[9..12] przeskalowane proporcją tot; hist/e/l = ostatnie 30 dni |
| Churn (`CHURN`) | `churn.*`, membership 531/655, weeks 531 | `lost30` = suma wejść do 655 przez 30 dni; `wk` = pełne tygodnie od czwartku |
| Serie (`ACTIVE_T`, `CONS`, `SER`) | membership 528, 28/51/71/75/523, 488, 551, 636/639 | od stałych dat startu do dziś |
| Leady (`LEAD`, `LB`) | `lead.*`, `lb.*`, membership 551 | e/l/hist = ostatnie 31 dni |
| 800+ (`P8`) | `p8.*`, membership 636/639, `camp` | `day` od 28 wrz |
| Cashback (`CB`) | `cb.*`, próbka | n/nu = ostatnie 6 dni próbki; `days` = [naliczony, wydany, n] na dzień |
| Rabaty (`RB`) | `rb.w*`, próbka | 14 dni próbki; `days` = [% z kodem, % top-up] na dzień; top10 kodów |
| Status bazy, drabina, produkty (`STATIC`) | `lad.*`, `seg.*`, `app.buy30`, próbka | pay = udział wartości; AOV = v/n; mediana długości diety |
| Aplikacja (`APP`, `APPR`) | `app.*`, `appr.*`, próbka (źródło), `push_monthly` | |
| Zasięg e-mail (`EMR`) | `emr.*` | |
| Nowi klienci (`NK`, `NCR`, `NCSEC`, `WT`) | `nk.*`, `active_pages`, `sec_pages` | NK = P1(642) + P2(643) w oknach; NCSEC = drugie zamówienie w trakcie diety |
| Dni dostaw (`DMAP`) | `dmap.*`, `raw.G.0/1` | |
| Churn rate (`CHURNP`) | `churnp.*` | [odpłynęli, aktywni na początku] dla 1/7/90 dni |
| Kampanie (`FLOWS`) | `flows.metrics`, `flows.goals`, `flows.meta` | od 2026-09-01; konwersje i przychód z celów 2/7/10/11 |

## 3. Kontrole po build.py

- `WT` ≈ poprzedni dzień (±kilka), `NCR` ma kilkaset wierszy.
- `CHURN.wk` ma tylko pełne tygodnie. Ostatni tydzień zaczyna się w czwartek ≥ 7 dni temu.
- `RAW.rfm[*].hist[-1]` = `raw.R*.tot`.
- Playwright: brak `pageerror`.

## 4. Pułapki

- Logi: `continuation` ignoruje okno from/to, więc dzień wybieraj po `timestamp`. `event_names.daily_count` to dzień bieżący.
- `channel_metrics` ignoruje `steps` i zwraca 45 dni.
- `segment_membership` w resolution `weeks`: pierwszy kubełek bywa niepełny (dlatego start od 2026-07-09, a build go pomija).
- W HTML jest `try{applyData(d)` przed `try{applyData({`. build.py podmienia właściwe miejsce.
- Routines nie mogą mieć connectorów w tej organizacji, więc przycisk „Zaktualizuj” nie odświeży danych sam.

## 5. Poza build.py (świadomie)

| Element | Dlaczego | Kiedy |
|---|---|---|
| `MOM` (porównanie miesięcy) | Liczony raz na miesiąc z pełnego miesiąca kalendarzowego. Definicje w `docs/SZCZEGOLY_ZRODEL.md`. | 1. dnia miesiąca (następnie 1 listopada) |
| `INC` | Inkrementalność liczona na żywo w przeglądarce (connector). | — |
| Etykiety, kolory, `STATIC.gapC` | Stałe opisowe. | — |
