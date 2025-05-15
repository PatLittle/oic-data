// scripts/scrape-missing-order-tables.js
import fs from 'fs';
import puppeteer from 'puppeteer';
import { parse } from 'csv-parse';
import { scrapeResultPage, saveOrderTables } from './lib/scraping.js';

const missingOrdersPath = 'processed-csvs/missing-oic-pc-numbers.csv';

(async function scrape() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Navigate to the main search page
  await page.goto('https://orders-in-council.canada.ca/index.php?lang=en', { waitUntil: 'domcontentloaded' });

  const missingOrdersParser = fs.createReadStream(missingOrdersPath)
    .pipe(
      parse({
        delimiter: ',',
        columns: true,
        ltrim: true
      })
    );

  for await (const missingOrder of missingOrdersParser) {
    // Wait for search button and prepare form
    await page.waitForSelector('#btnSearch', { timeout: 60000 });
    // Clear previous input if any
    await page.evaluate(() => { document.querySelector('#pcNumber').value = ''; });

    // Enter PC number and search
    await page.type('#pcNumber', missingOrder.pc_number);
    await page.click('#btnSearch');

    // Wait for results to load
    await page.waitForNavigation({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('div.table-responsive > table#results', { timeout: 60000 });

    // Reveal all columns
    await page.click('#resetColButton');
    await page.waitForTimeout(500);

    console.log(`attempting to scrape unpublished OIC ${missingOrder.pc_number}`);
    const orderTables = await scrapeResultPage(page);

    console.log('scraped', orderTables);
    saveOrderTables(orderTables);

    // Be polite before next iteration
    await page.waitForTimeout(5000);

    // Return to search page for next PC number
    await page.goto('https://orders-in-council.canada.ca/index.php?lang=en', { waitUntil: 'domcontentloaded' });
  }

  await browser.close();
})();
