# Canadian federal Order in Council data

<!-- STATUS:START -->
**Latest OIC date:** 2026-04-30
**Last checked:** 2026-05-08 09:49 UTC
<!-- STATUS:END -->

Orders in Council are a key part of Canada’s legal text. They’re a type of delegated legislation, adding additional detail or exercising a specific power from statute or prerogative.

The [Orders in Council (OIC) database](https://orders-in-council.canada.ca/) is great—but it has no export. This makes it difficult to study OICs at scale. This project mirrors OICs, and their attachments, once a day.


The database’s disclaimer _extra applies_ to this dataset:

> The Orders in Council available through this website are not to be considered to be official versions, and are provided only for information purposes. If you wish to obtain an official version, please [contact the Orders in Council Division](https://www.canada.ca/en/privy-council/services/orders-in-council.html#summary-details3).

### View OIC Data in Flat Data Viewer
#### Orders.csv
>[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/PatLittle/oic-data/blob/main/processed-csvs?filename=processed-csvs%2Forders.csv&sort=date%2Cdesc&stickyColumnName=pcNumber) 

#### Attachments.csv
>[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/PatLittle/oic-data/blob/main/processed-csvs?filename=processed-csvs%2Fattachments.csv)




## Recent orders

<!-- RECENT_ORDERS:START -->
| Date | PC Number | Department | Act | Subject |
| --- | --- | --- | --- | --- |
| 2026-04-30 | 2026-0407 | FIN | Canada Post Corporation Act | Order authorizing the Minister of Finance to provide financial assistance to the Canada Post Corporation for the period beginning April 1, 2026 and ending on March 31, 2027 |
| 2026-04-30 | 2026-0406 | GAC | Other Than Statutory Authority | Canada - French Republic on the Exchange and Mutual Protection of Classified Information ** Agreement ** |
| 2026-04-30 | 2026-0405 | GAC | Other Than Statutory Authority | Canada - Hellenic Republic on the Mutual Protection of Classified Information ** Agreement ** |
| 2026-04-30 | 2026-0404 | GAC | Other Than Statutory Authority | Agreement between the Government of Canada and the Government of the United Arab Emirates for the Promotion and Protection of Investments |
| 2026-04-30 | 2026-0403 | ESDC | Financial Administration Act | Order in Council directing that the annual report of the Canadian Accessibility Standards Development Organization be discontinued |
| 2026-04-29 | 2026-0402 | PMO | Public Service Rearrangement and Transfer of Duties Act | Order Transferring to the Department of Public Works and Government Services the Control and Supervision of Certain Portions of the Federal Public Administration |
| 2026-04-29 | 2026-0401 | PMO | Other Than Statutory Authority | Order directing a Commission do issue empowering the administration of Oaths |
| 2026-04-29 | 2026-0400 | JUS | Other Than Statutory Authority | Appointment of a Judge of the Superior Court of Justice of Ontario, and a Judge ex officio of the Court of Appeal for Ontario |
| 2026-04-29 | 2026-0399 | JUS | Other Than Statutory Authority | Appointment of a Judge of the Superior Court of Justice of Ontario, and a Judge ex officio of the Court of Appeal for Ontario |
| 2026-04-29 | 2026-0398 | JUS | Other Than Statutory Authority | Appointment of a Judge of the Federal Court, and a Judge ex officio of the Federal Court of Appeal |
<!-- RECENT_ORDERS:END -->

## Charts

### Orders by year

<!-- ORDERS_BY_YEAR:START -->
```mermaid
---
config:
  xychart:
    xAxis:
      labelFontSize: 8
---
xychart-beta
    title "Orders in Council by Year"
    x-axis ["90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"]
    y-axis "Orders" 0 --> 2873
    line [2873, 2595, 2748, 2223, 2175, 2258, 2086, 2058, 2360, 2287, 1832, 2426, 2240, 2158, 1602, 2341, 1671, 2023, 1958, 2071, 1632, 1726, 1764, 1506, 1496, 1304, 1207, 1743, 1607, 1419, 1124, 1065, 1386, 1276, 1400, 1017, 384]
```
<!-- ORDERS_BY_YEAR:END -->

### Monthly order counts by act

Mermaid XY charts support multiple line series, so this chart shows one monthly series per act in a GitHub-renderable format.

<!-- MONTHLY_ACT_CHART:START -->
Series order: 1. Other Than Statutory Authority; 2. Financial Administration Act; 3. Department of Employment and Social Development Act; 4. Public Service Employment Act; 5. Immigration and Refugee Protection Act; 6. Customs Tariff; 7. Other

```mermaid
xychart-beta
    title "Monthly Order Counts by Act (Latest 12 Months)"
    x-axis ["2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"]
    y-axis "Orders" 0 --> 71
    line [1, 26, 12, 11, 8, 15, 28, 24, 5, 6, 31, 29]
    line [7, 3, 0, 1, 1, 4, 4, 22, 17, 6, 13, 2]
    line [0, 0, 0, 0, 0, 2, 5, 35, 7, 9, 1, 11]
    line [0, 3, 0, 3, 3, 2, 1, 9, 1, 2, 10, 0]
    line [0, 0, 0, 0, 1, 1, 2, 0, 3, 10, 6, 6]
    line [0, 3, 2, 1, 0, 4, 0, 4, 1, 4, 1, 1]
    line [49, 29, 19, 23, 46, 29, 63, 45, 28, 71, 55, 48]
```
<!-- MONTHLY_ACT_CHART:END -->

## How it works

- `scripts/scrape-order-tables.js` uses a headless browser to submit the search form (with no criteria), downloading new results to `order-tables/`
	- creates one JSON file per OIC, containing the HTML of the OIC summary table as a property (`html`)
	- updates `attachment-ids.json` with any new attachments from the new results
- `scripts/scrape-attachments.js` downloads new attachments to `attachments/`
	- ditto JSON approach from the OICs
- `.github/workflows/update-oics.yaml` runs these scripts once a day via GitHub Actions, automatically updating this repository.


## The data

As of July 2022, there are about 62,000 OICs (60.3 MB) and 32,000 attachments (131.1 MB).

A SQLite database can be generated by the GitHub Actions workflow (`Produce CSV from JSON order tables`). When the generated database is 100 MiB or smaller, the workflow commits `processed-csvs/oic-data.sqlite` directly to the repository; otherwise it uploads the database as the `oic-data-sqlite` workflow artifact. The generated DB contains these tables:

- `orders` (`pc_number` primary key)
- `attachments` (`id` primary key)
- `order_attachments` (junction table from `orders` to referenced attachment IDs; retains all references even if attachment content is missing)
- `order_attachments_resolved` (view showing whether each `order_attachments.attachment_id` currently exists in `attachments`)
- `missing_oic_pc_numbers` (known missing OIC numbers)

To create a smaller SQLite export, the build script supports whitespace normalization for both orders and attachments:

- `--order-whitespace preserve`
- `--order-whitespace strip`
- `--order-whitespace collapse`
- `--order-whitespace remove`
- `--attachment-whitespace preserve` (default, no text changes)
- `--attachment-whitespace strip` (trim leading/trailing whitespace)
- `--attachment-whitespace collapse` (collapse all whitespace runs to single spaces)
- `--attachment-whitespace remove` (remove all whitespace characters)
- `--no-secondary-indexes` (skip non-primary-key indexes to reduce file size)

Example compact build:

```bash
python3 scripts/build-sqlite-db.py \
  --db-path processed-csvs/oic-data-compact.sqlite \
  --order-whitespace collapse \
  --attachment-whitespace collapse \
  --no-secondary-indexes
```


## Quirks

- The database seems to shift the comma associated with the “Dept” column depending on the display order—so files in `order-tables` get overwritten with a new `htmlHash`, despite only a comma having changed. This occurs with maximum four OICs per scrape (because five are displayed on each search result page, and the scraper stops if it recognizes all five).
- The tool doesn’t really handle changes to past OICs. But my (very strong) hunch is that they don’t change. You could adjust this tool to monitor all results regularly, using `htmlHash` to detect a change, but, well, see the comma issue above.


## Where to go from here

Import the data directly and use it as you see fit. Or, use the complementary [`lchski/oic-analysis`](https://github.com/lchski/oic-analysis) project (written in R) to extract meaningful information from these raw data, enabling analysis. Feel free to credit / link to this repository if you can, and make sure to mention that the information is originally from the Order in Council Division’s [Orders in Council database](https://orders-in-council.canada.ca/).
