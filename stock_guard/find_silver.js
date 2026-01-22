
async function findSilver() {
    // Check Binance Spot
    try {
        const res = await fetch('https://api.binance.com/api/v3/exchangeInfo');
        const data = await res.json();
        const silver = data.symbols.filter(s => s.symbol.includes('XAG') || s.symbol.includes('SILVER'));
        console.log('Binance Spot Silver Candidates:', silver.map(s => s.symbol));
    } catch (e) { console.log('Binance Error', e.message); }

    // Check Kraken
    try {
        const res = await fetch('https://api.kraken.com/0/public/AssetPairs');
        const data = await res.json();
        if (data.result) {
            const keys = Object.keys(data.result);
            const silver = keys.filter(k => k.includes('XAG') || k.includes('SILVER'));
            console.log('Kraken Silver Candidates:', silver);
        }
    } catch (e) { console.log('Kraken Error', e.message); }
}

findSilver();
