// import { ApifyClient } from 'apify-client';
// import fs from 'fs'; // Import the file system module

// // Initialize the ApifyClient with API token
// const client = new ApifyClient({
//     token: 'apify_api_ZZqSyqydUiZDayWdRVHQQ8n25kJJKR0w6EcF',
// });
// // import { ApifyClient } from 'apify-client';

// // // Initialize the ApifyClient with API token
// // const client = new ApifyClient({
// //     token: '<YOUR_API_TOKEN>',
// // });

// // Prepare Actor input
// const input = {
//     "startUrls": [
//         {
//             "url": "https://www.bestbuy.com/site/promo/tv-deals"
//         }
//     ],
//     "proxyConfig": {
//         "useApifyProxy": true
//     },
//     "maxProductsCnt": 100,
//     "addImages": true,
//     "addTopReviews": true,
//     "maxRequestRetries": 10,
//     "minConcurrency": 10,
//     "maxConcurrency": 20,
//     "handleRequestTimeoutSecs": 30
// };

// (async () => {
//     // Run the Actor and wait for it to finish
//     const run = await client.actor("oHm3eFc5kBKaFD45o").call(input);

//     // Fetch and print Actor results from the run's dataset (if any)
//     console.log('Results from dataset');
//     const { items } = await client.dataset(run.defaultDatasetId).listItems();
//     items.forEach((item) => {
//         console.dir(item);
//     });
// })();

import { ApifyClient } from 'apify-client'; // Import Apify client library
import axios from 'axios'; // Import axios for HTTP requests
import fs from 'fs'; 
// Initialize the ApifyClient with your API token
const client = new ApifyClient({
    token: 'apify_api_ZZqSyqydUiZDayWdRVHQQ8n25kJJKR0w6EcF',
});

// ScrapingBee API key
const SCRAPING_BEE_API_KEY = '7O8HAEHB2O3YQ8O5ZJOQQ3PUU2GKTWGJSKU8AB5IXJJ85PQH2PBNXBE3V32R1NDNTWHXI5HWLBPG4HNB'; // Replace with your ScrapingBee API key

// Function to fetch page content using ScrapingBee
const fetchWithScrapingBee = async (url) => {
    try {
        console.log(`Fetching page content for URL: ${url}`);
        const response = await axios.get('https://app.scrapingbee.com/api/v1/', {
            params: {
                api_key: SCRAPING_BEE_API_KEY,
                url: url,
                render_js: true, // Enable JavaScript rendering
            },
        });
        return response.data; // Return the HTML content
    } catch (error) {
        console.error(`Error fetching URL with ScrapingBee: ${url}`, error.message);
        return null; // Return null if there's an error
    }
};

// Define the input for the actor
const input = {
    startUrls: [
        {
            url: "https://www.bestbuy.com/site/insignia-32-class-f20-series-led-hd-smart-fire-tv/6482022.p?skuId=6482022", // The starting URL
        },
    ],
    proxyConfig: {
        useApifyProxy: true, // Use Apify's proxy service for other requests
    },
    maxProductsCnt: 100, // Limit on the number of items
    addImages: true, // Include images in the output
    addTopReviews: true, // Include top reviews
    maxRequestRetries: 10, // Retry limit for failed requests
    minConcurrency: 10, // Minimum concurrency
    maxConcurrency: 20, // Maximum concurrency
    handleRequestTimeoutSecs: 30, // Timeout for requests
};

(async () => {
    try {
        console.log("Starting the actor...");

        // Fetch the first page content using ScrapingBee
        const firstPageContent = await fetchWithScrapingBee(input.startUrls[0].url);

        if (!firstPageContent) {
            throw new Error('Failed to fetch the first page content with ScrapingBee.');
        }

        // Optionally, save the first page content to a file for debugging
        fs.writeFileSync('first_page.html', firstPageContent);
        console.log('Saved the first page content to first_page.html');

        // Start the actor with the input and wait for it to finish
        const run = await client.actor('oHm3eFc5kBKaFD45o').call(input);

        console.log(`Actor started with Run ID: ${run.id}`);

        // Wait for the actor to finish and get its status
        const status = run.status;
        console.log(`Actor finished with status: ${status}`);

        if (status !== 'SUCCEEDED') {
            throw new Error(`Actor run failed with status: ${status}`);
        }

        // Fetch the results from the actor's default dataset
        console.log('Fetching results from the dataset...');
        const { items } = await client.dataset(run.defaultDatasetId).listItems();

        console.log(`Fetched ${items.length} items.`);

        // Process and save the results
        const outputFileName = 'apify_scraped_data_with_scrapingbee.json';
        fs.writeFileSync(outputFileName, JSON.stringify(items, null, 2));
        console.log(`Results saved to ${outputFileName}`);
    } catch (err) {
        console.error('Error occurred:', err.message);
    }
})();
