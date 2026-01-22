
async function findGold() {
    try {
        const res = await fetch('http://localhost:3001/api/proxy/kraken/0/public/AssetPairs');
        const data = await res.json();
        if (data.error && data.error.length > 0) {
            console.log('Error:', data.error);
            return;
        }

        const pairs = Object.keys(data.result);
        console.log('Total Pairs:', pairs.length);

        const goldPairs = pairs.filter(p => p.includes('XAU') || p.includes('GOLD') || p.includes('PAXG'));
        console.log('Gold Pairs found:', goldPairs);
    } catch (e) {
        console.error(e);
    }
}

findGold();
