
// Native fetch is available in Node 18+

async function checkBinance() {
    try {
        // Check Gold (Futures)
        console.log("--- Checking Gold (XAUUSDT) via Futures API ---");
        const fRes = await fetch('https://fapi.binance.com/fapi/v1/klines?symbol=XAUUSDT&interval=1d&limit=5');
        const fData = await fRes.json();
        if (Array.isArray(fData)) {
            fData.forEach((d, i) => {
                const date = new Date(d[0]).toISOString();
                console.log(`[${i}] Date: ${date}, Open: ${d[1]}, High: ${d[2]}, Low: ${d[3]}, Close: ${d[4]}`);
            });
            // Analyze "Yesterday" vs "Today"
            const yesterday = fData[fData.length - 2];
            const today = fData[fData.length - 1];
            console.log("Yesterday High:", yesterday[2]);
            console.log("Yesterday Low:", yesterday[3]);
            console.log("Today Open:", today[1]);
        } else {
            console.log("Error fetching Futures:", fData);
        }

        // Check Crypto (Spot)
        console.log("\n--- Checking BTC (BTCUSDT) via Spot API ---");
        const sRes = await fetch('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=5');
        const sData = await sRes.json();
        if (Array.isArray(sData)) {
            sData.forEach((d, i) => {
                const date = new Date(d[0]).toISOString();
                console.log(`[${i}] Date: ${date}, Open: ${d[1]}, High: ${d[2]}, Low: ${d[3]}, Close: ${d[4]}`);
            });
        }
    } catch (e) {
        console.error(e);
    }
}

checkBinance();
