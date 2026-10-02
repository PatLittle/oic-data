# Canadian federal Order in Council data

<!-- STATUS:START -->
**Latest OIC date:** 2026-10-01
**Last checked:** 2026-10-02 14:42 UTC
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
| 2026-10-01 | 2026-0925 | PPC | Building Canada Act | Order Amending Schedule 1 to the Building Canada Act |
| 2026-09-25 | 2026-0875 | FA | Other Than Statutory Authority | Appointment of the Ambassador Extraordinary and Plenipotentiary of Canada to the United Arab Emirates |
| 2026-09-25 | 2026-0874 | PMO | Parliament of Canada Act | Appointment of two Parliamentary Secretaries |
| 2026-09-25 | 2026-0873 | HC, PHAC | Quarantine Act | Minimizing the Risk of Exposure to Ebola Disease in Canada Order, 2026, No. 3 |
| 2026-09-25 | 2026-0872 | JUS | Yukon Act | Order Appointing the Hon. Keith D. Yamauchi, to be deputy judge of the Supreme Court of Yukon |
| 2026-09-25 | 2026-0871 | PSPC | National Capital Act | Order Authorizing the National Capital Commission to Grant an Easement to the City of Ottawa (the City) ***NCC*** |
| 2026-09-25 | 2026-0870 | PS, RCMP | Firearms Act | Authority to Enter into Contribution Agreements |
| 2026-09-25 | 2026-0869 | ISED, NRC | National Research Council Act Canada Business Corporations Act | Order Authorizing the Incorporation of a Corporation under the Canada Business Corporations Act |
| 2026-09-25 | 2026-0868 | GAC | Other Than Statutory Authority | Agreement between the Government of Canada and the Government of Romania on the Protection of Classified Information ** Agreement ** |
| 2026-09-25 | 2026-0867 | NRCAN | Financial Administration Act | Order in Council Directing that the Annual Report of the Canadian Nuclear Safety Commission and the Annual Report of the Canada Energy Regulator Board of Directors Be Discontinued |
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
    line [2873, 2595, 2748, 2223, 2175, 2258, 2086, 2058, 2360, 2287, 1832, 2426, 2240, 2158, 1602, 2341, 1671, 2023, 1958, 2071, 1632, 1726, 1764, 1506, 1496, 1304, 1207, 1743, 1607, 1419, 1124, 1065, 1386, 1276, 1400, 1017, 778]
```
<!-- ORDERS_BY_YEAR:END -->

### Monthly order counts by act

Mermaid XY charts support multiple line series, so this chart shows one monthly series per act in a GitHub-renderable format.

<!-- MONTHLY_ACT_CHART:START -->
Series order: 1. Other Than Statutory Authority; 2. Department of Employment and Social Development Act; 3. Financial Administration Act; 4. Public Service Employment Act; 5. Immigration and Refugee Protection Act; 6. Canada Marine Act; 7. Other

```mermaid
xychart-beta
    title "Monthly Order Counts by Act (Latest 12 Months)"
    x-axis ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
    y-axis "Orders" 0 --> 81
    line [28, 24, 5, 6, 31, 29, 10, 36, 18, 17, 9, 0]
    line [5, 35, 7, 9, 1, 11, 16, 3, 0, 1, 0, 0]
    line [4, 22, 17, 6, 13, 2, 4, 6, 0, 0, 5, 0]
    line [1, 9, 1, 2, 10, 0, 8, 4, 9, 6, 2, 0]
    line [2, 0, 3, 10, 6, 6, 2, 4, 0, 0, 0, 0]
    line [1, 1, 0, 3, 3, 0, 3, 12, 0, 0, 6, 0]
    line [62, 48, 29, 72, 53, 49, 51, 81, 11, 26, 43, 1]
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
