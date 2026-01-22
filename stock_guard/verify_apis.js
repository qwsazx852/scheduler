
async function checkAPIs() {
    // 1. Check Binance Futures for XAGUSDT (Silver)
    try {
        const binanceRes = await fetch('https://fapi.binance.com/fapi/v1/ticker/price?symbol=XAGUSDT');
        if (binanceRes.ok) {
            const data = await binanceRes.json();
            console.log('✅ Binance XAGUSDT Found:', data);
        } else {
            console.error('❌ Binance XAGUSDT Not Found:', binanceRes.status);
        }
    } catch (e) { console.error('Binance Error', e.message); }

    // 2. Check Yahoo Finance for DX-Y.NYB (DXY)
    try {
        const yahooRes = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?interval=1d&range=1d');
        if (yahooRes.ok) {
            const data = await yahooRes.json();
            if (data.chart && data.chart.result) {
                const meta = data.chart.result[0].meta;
                console.log('✅ Yahoo DXY Found:', { symbol: meta.symbol, price: meta.regularMarketPrice });
            } else {
                console.error('❌ Yahoo DXY Format Unexpected');
            }
        } else {
            console.error('❌ Yahoo DXY Not Found:', yahooRes.status);
        }
    } catch (e) {
        console.error('Yahoo Error', e.message);
        // Sometimes Yahoo blocks requests without user-agent, but fetch in node usually works or fails.
    }
}

checkAPIs();
