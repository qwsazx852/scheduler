
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3001;

app.use(cors());

// Logging middleware
app.use((req, res, next) => {
    console.log(`[Proxy] ${req.method} ${req.url}`);
    next();
});

// Proxy for Binance Spot
// Target: https://api.binance.com
// Route: /api/proxy/binance-spot/*
app.use('/api/proxy/binance-spot', async (req, res) => {
    // Remove the prefix
    const path = req.url.replace(/^\/?/, ''); // ensure clean path
    const url = `https://api.binance.com${req.url}`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            const text = await response.text();
            res.status(response.status).send(text);
            return;
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Spot Proxy Error:', error);
        res.status(500).json({ error: 'Proxy Request Failed', details: error.message });
    }
});

// Proxy for Binance Futures (Gold)
// Target: https://fapi.binance.com
// Route: /api/proxy/binance-futures/*
app.use('/api/proxy/binance-futures', async (req, res) => {
    const url = `https://fapi.binance.com${req.url}`;
    try {
        const response = await fetch(url);
        // Check for non-200 from Binance
        if (!response.ok) {
            console.error(`Binance Futures Error ${response.status}: ${response.statusText}`);
            // Attempt to read error body
            const errText = await response.text();
            res.status(response.status).send(errText);
            return;
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Futures Proxy Error:', error);
        res.status(500).json({ error: 'Proxy Request Failed', details: error.message });
    }
});

// Proxy for Kraken (Spot Gold)
// Target: https://api.kraken.com
// Route: /api/proxy/kraken/*
app.use('/api/proxy/kraken', async (req, res) => {
    // Note: req.url includes query string e.g. /0/public/Ticker?pair=XAUUSD
    const url = `https://api.kraken.com${req.url}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errText = await response.text();
            res.status(response.status).send(errText);
            return;
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Kraken Proxy Error:', error);
        res.status(500).json({ error: 'Proxy Request Failed' });
    }
});

// Proxy for Yahoo Finance
// Target: https://query1.finance.yahoo.com
// Route: /api/proxy/yahoo/*
app.use('/api/proxy/yahoo', async (req, res) => {
    // Note: req.url includes query string
    const url = `https://query1.finance.yahoo.com${req.url}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errText = await response.text();
            res.status(response.status).send(errText);
            return;
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Yahoo Proxy Error:', error);
        res.status(500).json({ error: 'Proxy Request Failed', details: error.message });
    }
});

// Proxy for WallstreetCN News
// Target: https://api-one-wscn.awtmt.com
// Route: /api/proxy/wscn/news
app.use('/api/proxy/wscn/news', async (req, res) => {
    const url = `https://api-one-wscn.awtmt.com/apiv1/content/lives?channel=global-channel&client=pc&limit=20`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errText = await response.text();
            res.status(response.status).send(errText);
            return;
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('WSCN News Proxy Error:', error);
        res.status(500).json({ error: 'Proxy Request Failed', details: error.message });
    }
});


// Proxy for MyMemory Translation API
// Target: https://api.mymemory.translated.net/get
// Route: /api/proxy/translate
app.use('/api/proxy/translate', async (req, res) => {
    // Forward the query string (contains q, langpair)
    const url = `https://api.mymemory.translated.net/get${req.url.replace(/^\/?/, '')}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const text = await response.text();
            res.status(response.status).send(text);
            return;
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Translation Proxy Error:', error);
        res.status(500).json({ error: 'Proxy Request Failed', details: error.message });
    }
});

// Proxy for Telegram API
// Target: https://api.telegram.org
// Route: /api/telegram/*
app.use('/api/telegram', async (req, res) => {
    // req.url includes /bot<token>/sendMessage
    const url = `https://api.telegram.org${req.url}`;

    // Telegram is usually POST with body
    // We need to support body forwarding.
    // Since we didn't use body-parser, we might need to rely on stream piping or manually read body?
    // Wait, express body-parser is not configured above.
    // BUT 'fetch' in frontend sends JSON string body.
    // If we use 'express.json()', it consumes the stream.
    // Let's see if we can just pipe the request?
    // OR: Just use 'express.json()' at top level?
    // The current server setup is super simple.

    // Actually, for a simple proxy, piping req to fetch is tricky with native fetch.
    // Let's add express.json() middleware at the top to parse body, then re-stringify?
    // OR simpler: use 'body-parser' if available or just read stream.
    // The snippet shows 'app.use(cors())' but no body parser.

    // Let's try to add express.json() globally first? 
    // Wait, modifying the top of file is another edit.
    // Let's try to do it inside here if we can.
    // Note: If we don't parse body, req.body is undefined.
    // If we pipe, native fetch init body accepts ...? 
    // Native node fetch body can be a stream?
    // Yes, 'req' is a stream. 
    // But 'fetch' (from Node 18+) 'body' option: "ReadableStream, Blob, BufferSource, FormData, URLSearchParams, USVString".
    // 'req' is an IncomingMessage (ReadableStream).
    // So we can pass 'body: req' IF 'duplex: "half"' is set (Node 18 fetch requirement for streams).

    try {
        const options = {
            method: req.method,
            headers: {
                'Content-Type': 'application/json' // We know frontend sends JSON
            }
        };

        if (req.method === 'POST') {
            // We need to read the body because we aren't using body-parser globally yet
            // and mixing streams with express can be finicky if we don't know environment.
            // Safest way without adding deps: buffer the stream.
            const buffers = [];
            for await (const chunk of req) {
                buffers.push(chunk);
            }
            const data = Buffer.concat(buffers).toString();
            options.body = data;
        }

        const response = await fetch(url, options);

        if (!response.ok) {
            const text = await response.text();
            res.status(response.status).send(text);
            return;
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Telegram Proxy Error:', error);
        res.status(500).json({ error: 'Proxy Request Failed', details: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`✅ Backend Proxy Server running on http://localhost:${PORT}`);
});
