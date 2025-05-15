/*

1. [browser scraping stuff, ref https://www.smashingmagazine.com/2021/03/ethical-scraping-dynamic-websites-nodejs-puppeteer/]
    - see how many pages
    - for loop n pages
2. Save all `table` within `main[role=main] > form`
3. Hash contents of each `table`
4. Save contents if (! exists: PC number + #3 hash as filename)
5. [go to next page, continue]

*/

import fs from 'fs';
import puppeteer from 'puppeteer';
import { scrapeResultPage, saveOrderTables, filenameFromOrderTable } from './lib/scraping.js';

const savedOrderTablesPath = 'order-tables/';

(async function scrape() {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    // Navigate to the main search page
    await page.goto('https://orders-in-council.canada.ca/index.php?lang=en');

    // Wait for the search button to be available
    await page.waitForSelector('#btnSearch', { timeout: 60000 });
    await page.click('#btnSearch');

    // Get the list of stored tables from the disk for comparison
    const savedOrderTables = fs.readdirSync(savedOrderTablesPath).filter(filename => filename.endsWith("json"));

    // Wait for the main content area to appear
    await page.waitForSelector('main#wb-cont', { timeout: 60000 });

    let currentPage = 1;

    // Try to extract the number of total pages
    const totalPages = await page.evaluate(() => {
        const paginationElement = document.querySelector('.pagebutton');
        return paginationElement ? parseInt(paginationElement.innerText) : 1;
    });

    while (currentPage <= totalPages) {
        console.log(`Scraping page ${currentPage}`);
        
        // Scrape the current page
        const orderTables = await scrapeResultPage(page);

        // If all scraped order tables have already been saved, quit
        if (orderTables.map(filenameFromOrderTable).every((filename) => savedOrderTables.includes(filename))) {
            console.log('Scraped orders already saved, quitting');
            break;
        }

        console.log('New tables found, saving');
        saveOrderTables(orderTables);

        currentPage++;
        await page.goto(`https://orders-in-council.canada.ca/results.php?pageNum=${currentPage}&lang=en`);
    }

    await browser.close();
})();

