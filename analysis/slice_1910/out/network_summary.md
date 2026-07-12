# 1910 printer-publisher network — build summary

Source: punjab.db, full year 1910 (Q1-Q4, 1408 entries). Normalized layer.
Method: bipartite printer<->publisher edges weighted by entries and copies;
self-publication excluded from edges, reported below. See script docstring.

## Headline structure

- Printer nodes: 121; publisher nodes: 520; edges: 570
- **Self-published entries: 480 of 1408 (34%)** — author = publisher;
  the modal "firm" in this economy is a person paying a press.
- Entries with no publisher recorded: 11
- Multi-partner printers (degree >= 5): 28
- Single-partner publishers: 482 of 520
  (most publishers use exactly one press; presses are the hubs)

## Top printers
| Name | entries | copies | partners (degree) |
|---|---|---|---|
| Wazir-i-Hind Press | 107 | 178,150 | 40 |
| Sri Gurmat Press | 95 | 106,425 | 40 |
| Mufid-i-Am Press | 94 | 164,187 | 23 |
| Arya Steam Press | 74 | 84,490 | 29 |
| Bombay Press | 61 | 157,950 | 34 |
| Rafah-i-Am Steam Press | 61 | 61,500 | 22 |
| Newal Kishore Press | 60 | 234,450 | 21 |
| Hamidiya Steam Press | 55 | 66,375 | 18 |
| Dipak Rajput Printing Works | 55 | 73,000 | 31 |
| Qaumi Press | 52 | 24,300 | 10 |
| Civil and Military Gazette Press | 48 | 46,225 | 2 |
| Hindustan Steam Press | 42 | 90,009 | 23 |
| Mujaddidi Press | 40 | 33,225 | 20 |
| Khadim-ut-Talim Press | 38 | 42,000 | 4 |
| Anand Prakash Press | 28 | 20,520 | 10 |

## Top publishers (non-self)
| Name | entries | copies | partners (degree) |
|---|---|---|---|
| Civil and Military Gazette Press | 47 | 45,925 | 1 |
| Khalsa Tract Society | 26 | 57,600 | 2 |
| Nand Lal, B. A., & Co., Co-operative Works | 24 | 9,600 | 1 |
| Karkhana 'Paisa Akhbar' | 22 | 25,000 | 1 |
| The Secretary of the Fund named | 20 | 34,950 | 1 |
| The Vakil Trading Company, Limited | 20 | 31,000 | 3 |
| Gulab Singh and Sons | 19 | 26,350 | 1 |
| B. Daya Singh and Sons | 16 | 22,500 | 5 |
| Bharat Literature Company, Limited | 15 | 16,000 | 4 |
| Lala Pokhar Das | 14 | 14,000 | 2 |
| B. Hardit Singh | 9 | 9,000 | 3 |
| B. Atar Singh | 7 | 5,850 | 4 |
| Balak Ram Anand | 6 | 4,200 | 1 |
| M. Pokhar Das | 6 | 6,000 | 1 |
| Saghir Hasan, Proprietor, Yusufi Press | 6 | 4,625 | 1 |

Files: network_nodes.csv, network_edges.csv (Gephi-importable), authors_top.csv.
