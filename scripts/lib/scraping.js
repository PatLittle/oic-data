import fs from 'fs';
import MD5 from 'crypto-js/md5.js';

const savedOrderTablesPath = 'order-tables/';
const attachmentIdsPath = 'attachment-ids.json';

// Runs in browser context via page.evaluate
async function extractOrderTables() {
  // Reveal all columns if the button exists
  const resetBtn = document.querySelector('#resetColButton');
  if (resetBtn) {
    resetBtn.click();
  }
  // Gather all rows from the results table
  const rows = Array.from(document.querySelectorAll('#results tbody tr'));

  return rows.map(row => {
    const cells = row.querySelectorAll('td');
    return {
      html: row.outerHTML,
      pcNumber:     cells[0]?.innerText.trim(),
      date:         cells[1]?.innerText.trim(),
      chapter:      cells[2]?.innerText.trim(),
      chapterYear:  cells[3]?.innerText.trim(),
      bill:         cells[4]?.innerText.trim(),
      department:   cells[5]?.innerText.trim(),
      act:          cells[6]?.innerText.trim(),
      subject:      cells[7]?.innerText.trim(),
      precis:       cells[8]?.innerText.trim(),
      registration: cells[9]?.innerText.trim(),
      attachments: Array.from(
        row.querySelectorAll('a[href*="attachment.php?attach="]')
      )
        .map(a => new URL(a.href, location.origin).searchParams.get('attach'))
    };
  });
}

export async function scrapeResultPage(page) {
  // Wait for the results table to appear
  await page.waitForSelector('div.table-responsive > table#results', { timeout: 60000 });
  // Run extraction in browser
  let orderTables = await page.evaluate(extractOrderTables);
  // Hash each table's HTML for change detection
  orderTables = orderTables.map(orderTable => ({
    ...orderTable,
    htmlHash: MD5(orderTable.html).toString()
  }));
  return orderTables;
}

export function filenameFromOrderTable(orderTable) {
  return `${orderTable.pcNumber}.json`;
}

export function saveOrderTables(orderTables) {
  let attachmentIds = JSON.parse(fs.readFileSync(attachmentIdsPath));

  orderTables.forEach(orderTable => {
    console.log(`saving ${filenameFromOrderTable(orderTable)}`);
    // Merge new attachments
    attachmentIds = [...new Set([...attachmentIds, ...orderTable.attachments])].sort();
    // Write order JSON
    fs.writeFileSync(
      `${savedOrderTablesPath}${filenameFromOrderTable(orderTable)}`,
      JSON.stringify(orderTable, null, 2)
    );
  });
  // Persist updated attachment list
  fs.writeFileSync(attachmentIdsPath, JSON.stringify(attachmentIds, null, 2));
}
