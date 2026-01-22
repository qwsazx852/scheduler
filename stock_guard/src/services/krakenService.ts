
import { API_CONFIG } from '../config/api';

export const krakenService = {
    // Helper to get dynamic backend URL
    getProxyUrl: () => {
        return API_CONFIG.getProxyUrl();
    },

    getGoldPrice: async (): Promise<number | null> => {
        try {
            const baseUrl = krakenService.getProxyUrl();
            // Kraken API: XAUUSD not available, using PAXG/USD (Paxos Gold) as proxy
            // Endpoint: /0/public/Ticker?pair=PAXGUSD
            const res = await fetch(`${baseUrl}/kraken/0/public/Ticker?pair=PAXGUSD`);

            if (!res.ok) return null;

            const data = await res.json();
            // Kraken Response Format:
            // { error: [], result: { PAXGUSD: { c: ["2250.00", "1.0"] } } }

            if (data.result && data.result.PAXGUSD) {
                const price = parseFloat(data.result.PAXGUSD.c[0]);
                return price;
            }
            return null;
        } catch (e) {
            console.error('Kraken Fetch Error', e);
            return null;
        }
    },

    getDailyStats: async (): Promise<any | null> => {
        try {
            const baseUrl = krakenService.getProxyUrl();
            // Fetch OHLC (Daily = 1440)
            const res = await fetch(`${baseUrl}/kraken/0/public/OHLC?pair=PAXGUSD&interval=1440`);
            if (!res.ok) return null;

            const data = await res.json();
            // Result format: { error: [], result: { PAXGUSD: [[time, open, high, low, close...], ...], last: ... } }

            if (data.result && data.result.PAXGUSD) {
                const candles = data.result.PAXGUSD;
                if (candles.length < 2) return null;

                // Last candle is usually "current/forming" (today)
                // Second to last is "yesterday" (closed)
                // Kraken candles: [time, open, high, low, close, vwap, volume, count]
                // All strings/numbers
                const today = candles[candles.length - 1];
                const yesterday = candles[candles.length - 2];

                const high = parseFloat(yesterday[2]);
                const low = parseFloat(yesterday[3]);
                const close = parseFloat(yesterday[4]);
                const todayOpen = parseFloat(today[1]);

                const range = high - low;

                return {
                    yesterdayHigh: high,
                    yesterdayLow: low,
                    yesterdayClose: close,
                    todayOpen: todayOpen,
                    fib618: high - (range * 0.618),
                    fib786: high - (range * 0.786)
                };
            }
            return null;
        } catch (e) {
            console.error('Kraken Stats Error', e);
            return null;
        }
    },

    connect: (onPriceUpdate: (price: number) => void) => {
        let ws: WebSocket | null = null;
        let reconnectTimer: any = null;
        let isClosedIntentionally = false;

        const connect = () => {
            if (isClosedIntentionally) return;

            // Direct WS connection (CORS is usually fine for WS)
            ws = new WebSocket('wss://ws.kraken.com');

            ws.onopen = () => {
                console.log('Kraken WS Connected');
                const msg = {
                    event: "subscribe",
                    pair: ["PAXG/USD"],
                    subscription: { name: "ticker" }
                };
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify(msg));
                }
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    // Format: [channelID, { c: [price, wholeLotVolume] }, channelName, pair]
                    if (Array.isArray(data) && data.length >= 4) {
                        const payload = data[1]; // The object containing ticker info
                        // Check if we have 'c' (Close price)
                        // Note: Payload can be just { v: ... } updates sometimes? 
                        // Ticker usually sends full snapshot or specific fields. 
                        // Kraken documentation says ticker updates contain fields that changed.
                        // However, 'c' (Close) typically comes often.

                        if (payload && payload.c && Array.isArray(payload.c)) {
                            const price = parseFloat(payload.c[0]);
                            if (!isNaN(price)) {
                                onPriceUpdate(price);
                            }
                        }
                    } else if (data.event === 'heartbeat') {
                        // Keep alive
                    }
                } catch (e) {
                    console.error('Kraken WS Parse Error', e);
                }
            };

            ws.onclose = () => {
                console.log('Kraken WS Closed');
                if (!isClosedIntentionally) {
                    reconnectTimer = setTimeout(connect, 5000);
                }
            };

            ws.onerror = (err) => {
                console.error('Kraken WS Error', err);
                ws?.close();
            };
        };

        connect();

        return () => {
            isClosedIntentionally = true;
            clearTimeout(reconnectTimer);
            ws?.close();
        };
    }
};
