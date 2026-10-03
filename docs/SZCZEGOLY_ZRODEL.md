# Foodify Insights: pełna aktualizacja danych (runbook dla LLM)

Ten dokument opisuje krok po kroku, jak odświeżyć **wszystkie** dane w dashboardzie „Insights @ RetentionQ” dla klienta Foodify. Jest napisany dla agenta LLM z dostępem do narzędzi opisanych niżej. Wykonuj kroki w podanej kolejności i nie pomijaj żadnego, chyba że dany krok jest wprost oznaczony jako opcjonalny.

---

## 0. Założenia i narzędzia

| Element | Wartość |
|---|---|
| Dashboard (artefakt) | `https://claude.ai/artifact/B25KPWGfbtcg3LzJjiyY2B` |
| Źródło danych | Customer.io, connector **Customer.io Pstryk**, narzędzie `cio_read_api` |
| Workspace / environment | `190673` (region EU) |
| Baza artefaktu | narzędzie `ArtifactData`, dokument `snapshot/current` |
| Publikacja strony | narzędzie `Artifact` (publish z `url` artefaktu) |

Potrzebne uprawnienia: odczyt Customer.io, zapis do bazy artefaktu, publikacja artefaktu. **Nie zmieniaj** segmentów, kampanii ani danych klientów w Customer.io. Ten proces tylko czyta.

### 0.1 Skąd strona bierze dane

Strona ma dwa źródła danych i oba trzeba zaktualizować:

1. **Snapshot** (`snapshot/current` w bazie artefaktu). Ten sam obiekt jest też **wklejony w kod strony** w linii zaczynającej się od `try{applyData({`. Strona najpierw pokazuje wersję wklejoną, a potem nadpisuje ją wersją z bazy. Zaktualizuj **obie**: zapisz dokument w bazie i podmień obiekt w HTML.
2. **Stałe w kodzie HTML**: `FLOWS`, `NCR`, `NK`, `NCSEC`, `WT`, `DMAP`, `CHURNP`, `EMR`, `APPR`, `INC`. Nie ma ich w snapshocie, więc edytujesz je bezpośrednio w pliku strony.

### 0.2 Pobranie kodu strony

1. `Artifact` → `action: "read"`, `url` jak wyżej. Wynik podaje ścieżkę do zapisanego pliku HTML. Pracuj na tej kopii.
2. Na koniec publikujesz ten plik z tym samym `url` (krok 9).

### 0.3 Konwencje dat

- **D0** = dzisiejsza data w strefie Europe/Warsaw (format `YYYY-MM-DD`).
- **Timestampy** w Customer.io są w sekundach UTC. Północ dnia D w UTC: `int(datetime(D, tzinfo=UTC).timestamp())`.
- **Serie dzienne** w snapshocie mają datę startu i jeden element na dzień, bez przerw. Ostatni element to zawsze **D0** (dzień w trakcie, wartość niepełna). Przy każdej aktualizacji:
  - **nadpisz** element dnia, który przy poprzedniej aktualizacji był „dziś” (był wtedy niepełny);
  - **dopisz** brakujące dni aż do D0.

### 0.4 Jak liczyć liczność filtra (podstawowa operacja)

```
cio_read_api
  path:   /v1/environments/190673/customers
  params: { "filters": "<base64(JSON filtra)>", "limit": 1 }
  jq:     .meta.pagination.total
```

Składnia filtra:
- segment: `{"segment":{"id":N}}`
- przecięcie: `{"and":[A,B,...]}`
- suma: `{"or":[A,B,...]}`
- negacja: `{"not":A}`

W filtrach klientów **wolno używać tylko warunków segmentowych**. Warunki atrybutowe i zdarzeniowe muszą być zapisane w segmencie. JSON koduj bez spacji (`separators=(',',':')`), potem base64.

Dalej w dokumencie zapis `count(X)` oznacza tę operację, a `∧` przecięcie (`and`).

### 0.5 Jak pobrać dzienne członkostwo segmentu

```
path:   /v1/environments/{environment_id}/metrics/segment_membership
params: { "environment_id":190673, "segment_id":N, "resolution":"days", "start":<ts>, "end":<ts> }
jq:     .membership_metric|[.entered,.left,.total]|tojson
```

Tablice zawierają po jednym elemencie na dzień od `start`. `entered` i `left` to wejścia i wyjścia w danym dniu, `total` to stan na koniec dnia.

### 0.6 Paginacja listy klientów

`limit` wynosi maksymalnie 50. Kolejne strony pobierasz parametrem `page: 1, 2, ...`. Liczba stron = `ceil(.meta.pagination.total / 50)`.

### 0.7 Wydajność

Wywołania są niezależne, więc wysyłaj je równolegle, w paczkach po 12–20. Wyniki zapisuj od razu do pliku roboczego (np. JSON), żeby nie zgubić ich przy długiej pracy.

---

## 1. Słownik segmentów

### 1.1 Grupy klientów

| Kod | Nazwa na dashboardzie | Filtr |
|---|---|---|
| R1 | Czempioni (RFM 14–15) | 143 |
| R2 | Lojalni (RFM 11–13) | 145 |
| R3 | Obiecujący (RFM 8–10) | 146 |
| R4 | Okazjonalni (RFM 5–7) | 147 |
| R5 | Utraceni (RFM 3–4) | 149 |
| CHA | Champion (10+ zamówień) | 648 |
| LOY | Lojalni (etap) | or[645,646,647] |
| POT | Potencjał | or[643,644] |
| NEW | 1 zamówienie | 642 |
| O4 | 4+ zamówień | or[645,646,647,648] |

### 1.2 Statusy dostaw

| Segment | Znaczenie |
|---|---|
| 649 | aktywni |
| 650 | kończy się w 0–3 dni |
| 651 | kończy się w 4–7 dni |
| ACT | jedzą teraz = or[649,650,651] |
| 652 | 1–7 dni bez dostawy |
| 653 | 8–14 dni bez dostawy |
| 654 | 15–30 dni bez dostawy |
| 655 | 31–60 dni bez dostawy |
| 656 | 61–90 dni bez dostawy |
| 657 | 90+ dni bez dostawy |
| 814 | koniec dostawy za 8–14 dni |
| 815 | koniec dostawy za 15–21 dni |
| 816 | koniec dostawy za 22–30 dni |
| 817 | koniec dostawy za 31–60 dni |
| 818 | koniec dostawy za 61+ dni |

### 1.3 Pozostałe segmenty

| Obszar | Segmenty |
|---|---|
| Jedzący, seria dzienna | 528 |
| Churn, seria dzienna | 531 |
| Flaga churn | 685 |
| 800+ | 636 członkowie, 689 zapisani, 688 zawieszeni, 687 kupili, 686 kupili 2×, 690 kupili 3×, 639 klienci (pierwszy zakup ze środków) |
| Cashback | 720–725 progi salda, 726–728 poziomy 10/12/15%, 729 użyli, 730 nigdy nie użyli, 731 wydali w 30 dni, 732 wydali w 7 dni |
| Leady | 551 wszystkie leady; zdarzenia 701–709; strony 710–719 |
| Zgody, seria dzienna | 28 newsletter, 51 oferty e-mail, 71 SMS, 75 nowości, 523 push |
| Aplikacja | 157 (`[App] Application User`) |
| Nowi klienci | 488 (`[Client] Newcomer`) |
| Rabaty | 692–696 przedziały majętności, 698, 700 |
| Churn per okres | 831–836 (pkt 3.5) |
| Zakup w k dni | 781 (1d), 782 (2d), 785 (7d), 787 (14d), 789 (30d), 790 (60d), 791 (90d), 830 (180d) |
| 2+ zakupy w k dni | 822 (1d), 823 (2d), 824 (7d), 825 (14d), 826 (30d), 827 (60d), 828 (90d), 829 (180d) |
| Base health | 616 sunsetted, 425 kandydaci do sunsetu |
| Inkrementalność | 774 grupa z wiadomościami, 629 holdout (stała `INC`) |
| Segmenty „jedzą teraz” w grupach (linki z kafelków) | 839 (R1), 840 (R2), 841 (R3), 842 (R4) |

---

## 2. Krok 1: pobierz bieżący snapshot

1. `ArtifactData` z parametrami:
   - `action: "get"`;
   - `collection: "snapshot"`;
   - `doc_id: "current"`;
   - `out_dir`: katalog roboczy.
2. Zapamiętaj `version`, bo będzie potrzebne do zapisu (`if_version`).
3. Wczytaj JSON. Pola najwyższego poziomu:
   - `ACTIVE_T`, `CB`, `CHURN`, `CONS`, `LB`, `LEAD`, `MOM`, `P8`, `RAW`, `RB`, `SER`, `STATIC`;
   - `asOf`, `updatedAt`, `v`.

Zmieniasz tylko pola opisane niżej. Resztę zostawiasz bez zmian.

---

## 3. Krok 2: liczności (snapshot)

### 3.1 RAW: segmenty i statusy

`RAW.rfm` zawiera grupy R1–R5, a `RAW.loy` grupy CHA, LOY, POT, NEW. Każda grupa ma pola `k`, `tot`, `r[13]`, `ltv[6]`, a grupy RFM dodatkowo `hist`, `e`, `l`.

Dla każdej grupy G:
1. `tot = count(G)`.
2. `r[0..8] = count(G ∧ X)`, gdzie X to kolejno: 650, 651, ACT, 652, 653, 654, 655, 656, 657.
3. `r[9..12]`: przeskaluj stare wartości proporcją `nowe_tot / stare_tot` i zaokrąglij.
4. `ltv[i] = count(G ∧ Y)` dla Y w [662, 663, 664, 682, 683, 684]. Ten krok jest opcjonalny; jeśli go pomijasz, zostaw stare wartości.

To 90 zapytań (9 grup × 10). R5 ma zwykle zera w statusach aktywnych.

### 3.2 RAW.rfm: seria historyczna

Dla R1–R5 pobierz `segment_membership` (segmenty 143, 145, 146, 147, 149) od dnia ostatniej aktualizacji do D0+1, a następnie:
- `hist`: nadpisz ostatni element wartością `total` dnia, który był ostatni, i dopisz `total` kolejnych dni;
- `e`: to samo z wartościami `entered`;
- `l`: to samo z wartościami `left`;
- przytnij każdą z tych trzech tablic do ostatnich 30 elementów.

### 3.3 CHURN

| Pole | Wzór |
|---|---|
| `base` | count(O4) |
| `flag` | count(O4 ∧ 685) |
| `st.act` | count(O4 ∧ 685 ∧ ACT) |
| `st.d030` | count(O4 ∧ 685 ∧ or[652,653,654]) |
| `st.d3190` | count(O4 ∧ 685 ∧ or[655,656]) |
| `st.d90` | count(O4 ∧ 685 ∧ 657) |
| `grp.CHA` | count(648 ∧ 685) |
| `grp.LOY` | count(or[645,646,647] ∧ 685) |
| `grp.R1..R5` | count(G ∧ 685 ∧ O4) |
| `grp.POT`, `grp.NEW` | 0 |
| `lost30` | suma `entered` segmentu 655 z ostatnich 30 dni |
| `day` | seria dzienna: `total` segmentu 531 (start 2026-08-07) |
| `wk` | tygodniowe odpływy i powroty; aktualizuj raz w tygodniu, gdy minie pełny tydzień (patrz pkt 11) |

### 3.4 P8 (Jedzeniowe 800+)

| Pole | Wzór |
|---|---|
| `members` | count(636) |
| `enr` | count(689) |
| `susp` | count(688) |
| `buy` | count(636 ∧ 687) |
| `buy2` | count(636 ∧ 686) |
| `buy3` | count(636 ∧ 690) |
| `who.lead` | count(636 ∧ not(or[642..648])) |
| `who.o1` | count(636 ∧ 642) |
| `who.o23` | count(636 ∧ or[643,644]) |
| `who.o4` | count(636 ∧ O4) |
| `whoBuy.*` | te same filtry co `who.*` ∧ 687 |
| `st.eat` | count(636 ∧ ACT) |
| `st.r030` | count(636 ∧ or[652,653,654]) |
| `st.l30` | count(636 ∧ or[655,656,657]) |
| `eatNoBuy` | count(636 ∧ not(687) ∧ ACT) |
| `rfm` | `{tot: count(689), r: [count(689∧143), count(689∧145), count(689∧146), count(689∧147), count(689∧149)]}` |
| `day` | `e` = `entered` segmentu 636, `b` = `entered` segmentu 639, `lab` = etykiety dni w formacie „2 paź” (start 2026-09-28) |

### 3.5 CB (cashback)

| Pole | Wzór |
|---|---|
| `buckets[i][1]` | count(720+i), i = 0..5 |
| `never[j]` | count((721+j) ∧ 730), j = 0..4 |
| `inact[j]` | count((721+j) ∧ or[655,656,657]), j = 0..4 |
| `lvl[0..2][1]` | count(726), count(727), count(728) |
| `used` | count(729) |
| `neverUsed` | count(730) |
| `sp30` | count(731) |
| `sp7` | count(732) |
| `days` | patrz pkt 8 |

### 3.6 LB i LEAD (leady)

| Pole | Wzór |
|---|---|
| `LB.tot` i `LEAD.tot` | count(551) |
| `LB.ev[k][1]` | count(551 ∧ X), X kolejno: 709, 705, 707, 706, 708, 701, 702, 703, 704 |
| `LB.pg[k][1]` | count(551 ∧ X), X kolejno: 710, 713, 712, 711, 718, 719, 717, 716, 714, 715 |

Pozostałe pola `LEAD` zostaw bez zmian albo uzupełnij z segmentów opisanych w kodzie (`renderLeads`).

### 3.7 RB (rabaty), liczności

`w[k]` dla k = 1..5 (segmenty Wk = 692..696):
- `[1] = count(Wk ∧ or[642..648])`;
- `[2] = count(Wk ∧ 698)`;
- `[3] = count(Wk ∧ 700)`;
- pola `[4..7]` (próbka zamówień) opisuje pkt 8.

---

## 4. Krok 3: serie dzienne (snapshot)

Dla każdej serii pobierz `segment_membership` od dnia ostatniego elementu do D0+1. Potem nadpisz ostatni stary element i dopisz nowe dni.

| Pole snapshotu | Segment | Co brać | Data startu serii |
|---|---|---|---|
| `ACTIVE_T` | 528 | `total` | 2026-07-06 |
| `CONS.c28` | 28 | `total` | `CONS.start` (2025-10-01) |
| `CONS.c51` | 51 | `total` | `CONS.start` |
| `CONS.c71` | 71 | `total` | `CONS.start` |
| `CONS.c75` | 75 | `total` | `CONS.start` |
| `CONS.c523` | 523 | `total` | `CONS.start` |
| `SER.newc` | 488 | `entered` | `SER.newc_start` |
| `SER.lead_e` | 551 | `entered` | `SER.lead_start` |
| `SER.lead_l` | 551 | `left` | `SER.lead_start` |
| `SER.lead_t` | 551 | `total` | `SER.lead_start` |
| `SER.p800_e` | 636 | `entered` | `SER.p800_start` |
| `SER.p800_buy` | 639 | `entered` | `SER.p800_start` |
| `CHURN.day` | 531 | `total` | 2026-08-07 |
| `P8.day.e` i `P8.day.b` | 636 i 639 | `entered` | 2026-09-28 (dopisz też etykiety do `lab`) |

Kontrola: długość serii = (D0 − data startu) w dniach + 1.

---

## 5. Krok 4: zapisz snapshot

1. Ustaw pola:
   - `asOf` = D0;
   - `updatedAt` = bieżący czas w **milisekundach** (liczba);
   - `v` = 1.
2. Wszystkie liczby zapisuj jako liczby, nie jako stringi.
3. `ArtifactData` z parametrami:
   - `action: "set"`;
   - `collection: "snapshot"`;
   - `doc_id: "current"`;
   - `file_path`: plik JSON;
   - `if_version`: wersja z kroku 1.

   Przy konflikcie wersji pobierz dokument ponownie, nanieś zmiany i zapisz jeszcze raz.
4. W pliku HTML podmień obiekt w `try{applyData({...})` na nowy snapshot. Szukaj dokładnie ciągu `try{applyData({`, bo wcześniej w kodzie jest też `try{applyData(d)`. Zrób to parserem JSON (`json.JSONDecoder().raw_decode` od pozycji `{`), nie regexem.

---

## 6. Krok 5: kampanie (stała `FLOWS` w HTML)

Struktura stałej:

```js
FLOWS = {
  start: "2026-09-01",
  days: N,
  c: {
    "<id_kampanii>": {
      n, t, st,
      m: [6 tablic dziennych],
      c: [konwersje dziennie],
      r: [przychód dziennie],
      mw: [...],
      mm: [...]
    }
  }
}
```

Kolejność 6 tablic w `m`: `sent`, `delivered`, `human_opened`, `human_clicked`, `unsubscribed`, `converted`. Indeks dnia i = (data − start) w dniach. Ostatni dzień tablicy to D0.

1. **Metryki maili** (dla kampanii, które mają `m`). Wynik obejmuje k ostatnich dni, przy czym ostatni element to D0. Nadpisz ostatni stary dzień i dopisz nowe.
   ```
   path:   /v1/environments/190673/campaigns/<id>/metrics
   params: { "period":"days", "steps":k }
   jq:     .campaign_metrics.email as $e|[["sent","delivered","human_opened","human_clicked","unsubscribed","converted"][]|($e[.]//[])[-k:]]|tojson
   ```
2. **Konwersje i przychód z celów.** Dla każdego dnia D (okno `[D 00:00, D 23:59:59]` UTC) pobierz cztery cele: **2, 7, 10, 11**.
   ```
   path:   /v1/environments/190673/goals/<goal>/goal_refresh
   params: { "start":<ts>, "end":<ts> }
   jq:     {p:.refresh_in_progress,g:[.goal_refresh[]|{campaign_id,goal_count,revenue}]}|tojson
   ```
   - Jeśli `p` = true, przelicza się. Wywołaj ponownie po chwili i bierz dane dopiero, gdy `p` = false.
   - Zsumuj `goal_count` i `revenue` per `campaign_id` ze wszystkich czterech celów. Wiersze z `campaign_id: null` pomiń.
   - Wpisz sumy do `c[i]` i `r[i]`. Kampanie bez wyniku dostają 0.
   - Dla bieżącego dnia (D0) cele zwykle są puste, wtedy wpisz 0. Wykres kampanii i tak kończy się na D0−1.
3. **Agregaty.** `mw` (tygodnie) i `mm` (miesiące): dodaj różnicę do ostatniego elementu albo przelicz je od nowa z `m`.
4. Ustaw `days` = liczba dni od `start` do D0 włącznie.

---

## 7. Krok 6: stałe wyliczane z listy klientów (HTML)

### 7.1 Przejście po aktywnych klientach

Przejdź wszystkie strony `count(649)` z `limit: 50`; zwykle to ok. 36–37 stron. Stała `B` w poniższym jq to bieżący unix ts (do sprawdzenia, czy start dostawy jest w przyszłości), a 1790985600 zastąp północą D0 w UTC.

```
jq:
def d(x): ((x-<północ D0 UTC>)/86400|floor);
[.customers[]|.attributes|((.active_diets|fromjson|map(.start_date|tonumber)|min)//0) as $s|
 {g:(((.rfm_total_score|tonumber?)//0)|if .>=14 then 0 elif .>=11 then 1 elif .>=8 then 2 elif .>=5 then 3 elif .>=3 then 4 else 5 end),
  w:($s> B),
  o:((.lifetime_orders|tonumber?)//0),
  n:[d((.first_order_at|tonumber?)//0), d(if $s>0 then $s else <północ D0> end), ((.total_days_count|tonumber?)//0)]}] as $a|
{w:([$a[]|select(.w)|.g]|group_by(.)|map([.[0],length])),n:[$a[]|select(.o==1)|.n]}|tojson
```

Z wyników:
- **`WT`** (kafelek „Czekają” w kartach segmentów). Zsumuj `w` po grupach 0..4 i zapisz w kodzie jako `const WT={R1:..,R2:..,R3:..,R4:..,R5:..}`. Grupa 5 to klienci bez wyniku RFM; nie wchodzi do `WT`.
- **`NCR`** (sekcja Nowi klienci). Połącz wszystkie tablice `n` w jedną listę wierszy `[dzień_pierwszego_zamówienia, dzień_startu, dni_diety]`, z dniami liczonymi względem D0, i zapisz jako `const NCR=[...]`.
- W funkcji `renderNC` zmień `t0=D0('YYYY-MM-DD')` na D0. Zmień też `"asof"` w obiekcie `NC`.

### 7.2 `NK`: pierwsze zamówienia w okresach

Najpierw policz N(k) dla okien k w [1, 2, 7, 14, 30, 60, 90, 180]:

N(k) = count(P1_k ∧ 642) + count(P2_k ∧ 643)

- **P1_k** (zakup w ostatnich k dniach): 781 (1d), 782 (2d), 785 (7d), 787 (14d), 789 (30d), 790 (60d), 791 (90d), 830 (180d).
- **P2_k** (2+ zakupy w ostatnich k dniach): 822, 823, 824, 825, 826, 827, 828, 829 (te same okna).

Potem zapisz w kodzie:

```js
NK={1:[N1, N2-N1], 7:[N7, N14-N7], 14:[N14, null], 30:[N30, N60-N30], 60:[N60, null], 90:[N90, null]}
```

Drugi element to poprzedni okres tej samej długości. Dla 90 dni zostaw `null`, bo okno 180 dni jest zawyżone przez początek historii zdarzeń.

### 7.3 `NCSEC`: drugie zamówienie w trakcie pierwszego

Format: `NCSEC=[ile_w_trakcie, mianownik]`. Obecnie [27, 72].

1. Pobierz klientów z 2 zamówieniami (643) z pierwszym zamówieniem w ostatnich 30 dniach.
2. Dla każdego sprawdź, czy drugie zamówienie zostało złożone, zanim skończyła się dieta z pierwszego zamówienia.

Metoda heurystyczna: jakakolwiek dieta z `start_date < last_order ≤ end_date + 1 dzień`. Jeśli nie aktualizujesz tej stałej, zaznacz to w raporcie.

### 7.4 `DMAP` (wykres „Ilość dni dostaw”)

Dla G w [wszyscy, R1, R2, R3, R4] policz wektor:

`[count(G∧650), count(G∧651), count(G∧814), count(G∧815), count(G∧816), count(G∧817), count(G∧818)]`

- Dla „wszyscy” G nie dodaje się do filtra, liczysz sam segment.
- Wartości 650 i 651 dla R1–R4 są już w `RAW` (`r[0]`, `r[1]`).
- R5 zwykle same zera.

Zapisz w `const DMAP={asof:'D0', b:[...bez zmian...], g:{all:['Wszyscy',[...]], R1:['Czempioni',[...]], R2:['Lojalni',[...]], R3:['Obiecujący',[...]], R4:['Okazjonalni',[...]], R5:['Utraceni',[...]]}}`.

### 7.5 `CHURNP` (churn rate w kartach segmentów dla 1, 7 i 90 dni)

Dla G w [R1, R2, R3, R4] (143, 145, 146, 147):

| Okres | Odpłynęli | Aktywni na początku okresu |
|---|---|---|
| 1 dzień | count(G∧831) | count(G∧832) |
| 7 dni | count(G∧833) | count(G∧834) |
| 90 dni | count(G∧835) | count(G∧836) |

Zapisz w kodzie:

```js
const CHURNP={1:{R1:[odpłynęli,aktywni],R2:...,R3:...,R4:...},7:{...},90:{...}}
```

Okno 30 dni strona liczy sama z `RAW` (d3160 / suma statusów).

### 7.6 `APPR` (podział App/Web, filtr „Urządzenie”)

Dla każdej grupy (CHA, LOY, POT, NEW, R1–R5) policz 10 liczb w kolejności: tot, 650, 651, ACT, 652, 653, 654, 655, 656, 657. Każda to count(G ∧ 157 ∧ X), a tot = count(G ∧ 157).

Jest to opcjonalne przy codziennej aktualizacji, ale aktualizuj co najmniej raz w tygodniu.

### 7.7 `EMR` (zasięg e-mail bez sunsetted)

Dla R1–R5: count(G ∧ 51 ∧ not(616)). Zapisz w kodzie `const EMR={R1:..,...}`. Aktualizuj co najmniej raz w tygodniu.

---

## 8. Krok 7: próbka zamówień (Rabaty, Cashback)

Dla każdego nowego dnia D pobierz pierwszą stronę logów zakupów (do 50 zamówień):

```
path:   /v1/environments/190673/logs
params: { "type":"event", "name":"purchase", "from":"D T00:00:00Z", "to":"D T23:59:59Z" }
```

Atrybuty zamówienia (`attrs`):
- `value`;
- `discount_code`, `discount_percent`;
- `spent_top_up`;
- `received_cashback`, `spent_cashback`, `spent_wallet_cashback`.

Atrybuty `wealth_index` i `lifetime_orders` są w tablicy `customers` odpowiedzi.

Z próbki aktualizujesz:
- `RB.days`: wiersz `[etykieta "D mies", % zamówień z kodem, % zamówień z top-up]`.
- `RB.codes`: top 10 kodów w formacie `[KOD, liczba, '15%'|'30%'|'40%']`. Procent wynika z sufiksu kodu.
- `RB.loy`: `[['1 zamówienie',n,z_kodem],['2–3 zamówienia',..],['4+ zamówień',..]]`.
- `RB.w[k][4..7]`: liczba zamówień, z kodem, suma `value`, suma rabatu. Rabat = `value*p/(100-p)` dla 0 < p < 100.
- `CB.days`: wiersz `[etykieta, naliczony cashback, wydany cashback, n]`.

**Definicje kolumn (zweryfikowane 3.10.2026 na danych z 26.09 i 29.09):**
- `RB.days` = `[etykieta, round(100 * zamówienia z niepustym discount_code / n), round(100 * zamówienia ze spent_top_up > 0 / n)]`;
- `CB.days` = `[etykieta, floor(suma received_cashback), floor(suma spent_wallet_cashback), n]`;
- `n` = liczba zamówień na pierwszej stronie logów danego dnia (zwykle 50).

Gotowy jq dla jednego dnia:
```
[.logs[]|.attrs|{rc:(.received_cashback//0|tonumber),sw:(.spent_wallet_cashback//0|tonumber),c:((.discount_code//"")|length>0),t:((.spent_top_up//0|tonumber)>0)}] as $r|[($r|length),([$r[]|select(.c)]|length),([$r[]|select(.t)]|length),(([$r[].rc]|add)//0|floor),(([$r[].sw]|add)//0|floor)]|tojson
```
Wynik to `[n, z_kodem, z_top_up, rc, sw]`.

Ostatni dzień w seriach był zwykle pobrany w trakcie dnia, więc przy każdej aktualizacji **przelicz go ponownie** i nadpisz, a potem dopisz nowe pełne dni. Wiersz za bieżący dzień D0 dopisuj tylko, gdy logi nie są puste.

Za bieżący dzień logi bywają jeszcze puste.

---

## 9. Krok 8: publikacja

1. W HTML sprawdź, czy kod się parsuje. Najlepiej otwórz plik w przeglądarce headless (Playwright) i upewnij się, że nie ma `pageerror`.
2. Sprawdź kontrolnie:
   - nagłówek strony pokazuje „Dane z D0 …”;
   - przy okresie 7 dni wykresy dzienne kończą się na D0 (wykres kampanii na D0−1);
   - kafelki Status bazy pokazują nowe liczby.
3. `Artifact` → publish z `file_path` = plik HTML i `url` = `https://claude.ai/artifact/B25KPWGfbtcg3LzJjiyY2B`. Nie zmieniaj `capabilities` (pomiń to pole).

---

## 10. Krok 9: raport dla użytkownika

Krótko, po polsku:
- co zaktualizowano i na jaki dzień;
- które liczby za D0 są niepełne (dzień w trakcie);
- co **nie** zostało zaktualizowane i dlaczego (np. `NCSEC`, `RB.days` przy niespójności, cele kampanii w trakcie przeliczania).

---

## 11. Harmonogram i rzeczy okresowe

| Częstotliwość | Co aktualizować |
|---|---|
| Codziennie | Kroki 1–8 (bez pozycji oznaczonych jako tygodniowe) |
| Co tydzień (poniedziałek) | `CHURN.wk` (`lab`, `out`, `back`: odpływ i powroty w zamkniętym tygodniu), `APPR`, `EMR`, `RAW.*.ltv`, `LEAD` (pozostałe pola), `INC` (inkrementalność: punkty dzienne zapisuje sama strona w kolekcji `inkr`) |
| Co miesiąc (1. dzień miesiąca) | `MOM` (porównania miesiąc do miesiąca: pary [poprzedni, bieżący] dla każdego wskaźnika) oraz `STATIC` (drabina zamówień, struktury dni, płatności, produkty). Przelicz z tych samych segmentów co liczności, dla dwóch kolejnych pełnych miesięcy. |

---

## 12. Automatyzacja (przycisk „Zaktualizuj”)

Przycisk w nagłówku dashboardu uruchamia przez connector **Claude Code Remote** zadanie w tle (Routine) zapisane w kodzie jako `REFRESH_TRIGGER`. To zadanie musiałoby wykonać kroki z tego dokumentu.

Stan na 3.10.2026:
- poprzednie zadanie (`trig_01QPrbW2DPMNBFrmsMNoWMSH`) nie istnieje;
- organizacja nie pozwala zadaniom w tle korzystać z connectorów, więc zadanie nie ma dostępu do Customer.io.

Gdy administrator organizacji włączy connectory dla Routines:
1. Utwórz Routine z `create_new_session_on_fire: true`, connectorem `Customer.io Pstryk` i promptem: „Wykonaj pełną aktualizację zgodnie z docs/AKTUALIZACJA_DANYCH.md”, z pełną treścią tego pliku wklejoną w prompt.
2. Wpisz jego ID do stałej `REFRESH_TRIGGER` w HTML i opublikuj.

Strona po kliknięciu pokazuje pasek postępu. Pasek kończy się, gdy w bazie zmieni się `snapshot/current.updatedAt`.

Do tego czasu aktualizację wykonuje agent ręcznie, według tego dokumentu.

---

## 13. Najczęstsze błędy

- **Nowe dane nie pojawiają się na stronie.** Snapshot zapisano tylko w bazie albo tylko w HTML. Zaktualizuj oba miejsca.
- **Wykres nie ma ostatnich dni.** Seria nie została przedłużona albo zmieniono `asOf` bez dopisania elementów. Długość serii musi pasować do daty startu i D0.
- **`floor cannot be applied to null` w jq.** Dzień nie ma jeszcze logów. Potraktuj go jako pusty.
- **Filtr zwraca błąd „Put it in a segment”.** Użyto warunku atrybutowego w filtrze klientów. Użyj istniejącego segmentu.
- **`goal_refresh` zwraca `p: true`.** Cel się przelicza. Ponów wywołanie po chwili.
- **Dziwne skoki 1.10 w seriach 655 i 531.** Segmenty były wtedy budowane od zera i wpisały całą zawartość jako wejścia jednego dnia. To artefakt, a nie realny odpływ.
