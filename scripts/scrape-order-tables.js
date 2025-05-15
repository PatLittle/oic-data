// scripts/scrape-order-tables.js
import fs from 'fs';
import puppeteer from 'puppeteer';
import { scrapeResultPage, saveOrderTables, filenameFromOrderTable } from './lib/scraping.js';

const savedOrderTablesPath = 'order-tables/';

(async function scrape() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Navigate to the main search page
  await page.goto('https://orders-in-council.canada.ca/index.php?lang=en');

  // Wait for the search button and submit
  await page.waitForSelector('#btnSearch', { timeout: 60000 });
  await page.click('#btnSearch');

  // Reveal all columns on the first results page
  await page.waitForSelector('div.table-responsive > table#results', { timeout: 60000 });
  await page.click('#resetColButton');
  await page.waitForTimeout(500);

  // Get the list of already-saved tables
  const savedOrderTables = fs.readdirSync(savedOrderTablesPath).filter(f => f.endsWith('.json'));

  // Ensure the main content has loaded
  await page.waitForSelector('main#wb-cont', { timeout: 60000 });

  // Determine total pages
  const totalPages = await page.evaluate(() => {
    const pagination = document.querySelector('ul.pagination');
    if (!pagination) return 1;
    const links = Array.from(pagination.querySelectorAll('li > a[href*="pageNum="]'));
    const nums = links.map(a => parseInt(new URL(a.href, location.origin).searchParams.get('pageNum')));
    return Math.max(...nums);
  });

  let currentPage = 1;
  while (currentPage <= totalPages) {
    console.log(`Scraping page ${currentPage}`);
    try {
      const orderTables = await scrapeResultPage(page);

      // Stop if all tables already saved
      if (orderTables.map(filenameFromOrderTable).every(fn => savedOrderTables.includes(fn))) {
        console.log('Scraped orders already saved, quitting');
        break;
      }

      console.log('New tables found, saving');
      saveOrderTables(orderTables);

      currentPage++;
      await page.goto(
        `https://orders-in-council.canada.ca/results.php?pageNum=${currentPage}&lang=en`,
        { waitUntil: 'domcontentloaded' }
      );
      await page.waitForSelector('div.table-responsive > table#results', { timeout: 60000 });

      // Reveal all columns on subsequent pages
      await page.click('#resetColButton');
      await page.waitForTimeout(500);
    } catch (error) {
      console.error(`Error scraping page ${currentPage}:`, error);
      console.log('Retrying...');
      await page.goto(
        `https://orders-in-council.canada.ca/results.php?pageNum=${currentPage}&lang=en`,
        { waitUntil: 'domcontentloaded' }
      );
    }
  }

  await browser.close();
})();
