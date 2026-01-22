import { API_CONFIG } from '../config/api';

type PriceCallback = (symbol: string, price: number) => void;

export const binanceService = {
    // Store active connections to allow cleanup
    activeConnections: [] as (() => void)[],

    // Status tracking
    lastSpotUpdate: 0,
    lastGoldUpdate: 0,
    isConnected: false,

    // Helper to get dynamic backend URL (handles localhost vs 127.0.0.1)
    getProxyUrl: () => {
        return API_CONFIG.getProxyUrl();
    },

    connect: (callback: PriceCallback) => {
        // 1. Connection A: Spot Market (Crypto)
        // Reconnection logic for Spot
        let wsSpot: WebSocket | null = null;
        let spotReconnectTimer: any = null;
        let isSpotClosedIntentionally = false;

        const connectSpot = () => {
            const spotStreams = [
                'btcusdt@trade', 'ethusdt@trade',
                'bnbusdt@trade', 'solusdt@trade',
                'xrpusdt@trade', 'dogeusdt@trade',
                'adausdt@trade'
            ].join('/');

            wsSpot = new WebSocket(`wss://stream.binance.com:9443/stream?streams=${spotStreams}`);

            wsSpot.onopen = () => console.log('✅ Spot WS Connected');

            wsSpot.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.data) {
                        binanceService.lastSpotUpdate = Date.now();
                        binanceService.isConnected = true;

                        const stream = data.data.s;
                        let symbol = '';
                        switch (stream) {
                            case 'BTCUSDT': symbol = 'BTC'; break;
                            case 'ETHUSDT': symbol = 'ETH'; break;
                            case 'BNBUSDT': symbol = 'BNB'; break;
                            case 'SOLUSDT': symbol = 'SOL'; break;
                            case 'XRPUSDT': symbol = 'XRP'; break;
                            case 'DOGEUSDT': symbol = 'DOGE'; break;
                            case 'ADAUSDT': symbol = 'ADA'; break;
                        }
                        if (symbol) callback(symbol, parseFloat(data.data.p));
                    }
                } catch (e) { console.error('Spot WS Parse Error', e); }
            };

            wsSpot.onclose = () => {
                if (!isSpotClosedIntentionally) {
                    console.log('⚠️ Spot WS Closed. Reconnecting...');
                    spotReconnectTimer = setTimeout(connectSpot, 3000);
                }
            };

            wsSpot.onerror = (err) => {
                console.error('❌ Spot WS Error', err);
                wsSpot?.close(); // Force close to trigger reconnect
            };
        };

        connectSpot();

        // 2. Connection B: Futures Market (Gold / XAUUSDT)
        // Reconnection logic for Futures
        let wsFutures: WebSocket | null = null;
        let futuresReconnectTimer: any = null;
        let isFuturesClosedIntentionally = false;

        const connectFutures = () => {
            // Updated endpoint to fstream.binance.com
            wsFutures = new WebSocket('wss://fstream.binance.com/ws/xauusdt@aggTrade');

            wsFutures.onopen = () => console.log('✅ Futures (Gold) WS Connected');

            wsFutures.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    // Futures AggTrade Format
                    // Futures AggTrade Format
                    if (data.s === 'XAUUSDT' && data.p) {
                        binanceService.lastGoldUpdate = Date.now();
                        binanceService.isConnected = true;
                        callback('XAU/USD', parseFloat(data.p));
                    }
                } catch (e) {
                    console.error('Futures WS Parse Error', e);
                }
            };

            wsFutures.onclose = () => {
                if (!isFuturesClosedIntentionally) {
                    console.log('⚠️ Futures WS Closed. Reconnecting...');
                    futuresReconnectTimer = setTimeout(connectFutures, 3000);
                }
            };

            wsFutures.onerror = (err) => {
                console.error('❌ Futures WS Error', err);
                wsFutures?.close(); // Force close to trigger reconnect
            };
        };

        connectFutures();

        // 3. Fallback Polling (Every 3 seconds)
        // Check Spot and Gold separately
        const pollInterval = setInterval(async () => {
            const now = Date.now();
            const pricesToFetch: string[] = [];

            // Check Spot
            if (now - binanceService.lastSpotUpdate > 5000) {
                // console.log('⚠️ Spot WS silent, polling...');
                pricesToFetch.push('SPOT');
            }

            // Check Gold
            if (now - binanceService.lastGoldUpdate > 5000) {
                // console.log('⚠️ Gold WS silent, polling...');
                pricesToFetch.push('GOLD');
            }

            if (pricesToFetch.length > 0) {
                try {
                    const prices = await binanceService.getLatestPrices();
                    // Only dispatch what we aimed to fetch, or just dispatch all found?
                    // Dispatching all found is safer to ensure sync.
                    Object.entries(prices).forEach(([symbol, price]) => {
                        // If it's Gold and we wanted Gold OR it's Crypto and we wanted Crypto
                        if (symbol === 'XAU/USD' && pricesToFetch.includes('GOLD')) callback(symbol, price);
                        else if (symbol !== 'XAU/USD' && pricesToFetch.includes('SPOT')) callback(symbol, price);
                    });
                } catch (e) {
                    console.error('Polling Error', e);
                }
            }
        }, 3000);

        // Cleanup function
        return () => {
            isSpotClosedIntentionally = true;
            isFuturesClosedIntentionally = true;
            clearTimeout(spotReconnectTimer);
            clearTimeout(futuresReconnectTimer);
            clearInterval(pollInterval);
            wsSpot?.close();
            wsFutures?.close();
        };
    },

    getKlines: async (symbol: string) => {
        // If Gold, use Futures API
        if (symbol === 'XAU/USD') {
            try {
                // Futures API (fapi) via Local Proxy
                const baseUrl = binanceService.getProxyUrl();
                const res = await fetch(`${baseUrl}/binance-futures/fapi/v1/klines?symbol=XAUUSDT&interval=1m&limit=100`);
                if (!res.ok) throw new Error(`Status ${res.status}`);
                const data = await res.json();
                if (!Array.isArray(data)) return [];

                return data.map((d: any) => ({
                    time: d[0] / 1000,
                    open: parseFloat(d[1]),
                    high: parseFloat(d[2]),
                    low: parseFloat(d[3]),
                    close: parseFloat(d[4]),
                }));
            } catch (e) {
                console.error('Failed to fetch Gold klines', e);
                return [];
            }
        }

        // Existing Spot Logic for Crypto
        let pair = '';
        if (symbol === 'BTC') pair = 'BTCUSDT';
        else if (symbol === 'ETH') pair = 'ETHUSDT';
        else if (symbol === 'BNB') pair = 'BNBUSDT';
        else if (symbol === 'SOL') pair = 'SOLUSDT';
        else if (symbol === 'XRP') pair = 'XRPUSDT';
        else if (symbol === 'DOGE') pair = 'DOGEUSDT';
        else if (symbol === 'ADA') pair = 'ADAUSDT';

        if (!pair) return [];

        try {
            const baseUrl = binanceService.getProxyUrl();
            const res = await fetch(`${baseUrl}/binance-spot/api/v3/klines?symbol=${pair}&interval=1m&limit=100`);
            if (!res.ok) return [];
            const data = await res.json();
            if (!Array.isArray(data)) return [];
            return data.map((d: any) => ({
                time: d[0] / 1000,
                open: parseFloat(d[1]),
                high: parseFloat(d[2]),
                low: parseFloat(d[3]),
                close: parseFloat(d[4]),
            }));
        } catch (e) {
            console.error('Failed to fetch klines', e);
            return [];
        }
    },

    getDailyStats: async (symbol: string) => {
        // If Gold, use Futures API
        if (symbol === 'XAU/USD') {
            try {
                // Fetch more than 2 to be safe
                const baseUrl = binanceService.getProxyUrl();
                const res = await fetch(`${baseUrl}/binance-futures/fapi/v1/klines?symbol=XAUUSDT&interval=1d&limit=5`);

                if (!res.ok) {
                    console.error('Gold Stats Error: Response not OK', res.status);
                    return null;
                }
                const data = await res.json();
                console.log('[Gold Stats Debug] Raw Data:', data);


                if (Array.isArray(data) && data.length >= 2) {
                    // Last closed candle is length-2 (yesterday)
                    // Current open candle is length-1 (today)
                    const yesterday = data[data.length - 2];
                    const today = data[data.length - 1];

                    const high = parseFloat(yesterday[2]);
                    const low = parseFloat(yesterday[3]);
                    const close = parseFloat(yesterday[4]);
                    const open = parseFloat(today[1]);

                    const range = high - low;
                    return {
                        yesterdayHigh: high,
                        yesterdayLow: low,
                        yesterdayClose: close,
                        todayOpen: open,
                        fib618: high - (range * 0.618),
                        fib786: high - (range * 0.786)
                    };
                } else {
                    console.warn('Gold Stats: Insufficient Data', data);
                }
            } catch (e) { console.error('Gold Stats Exception', e); }
            return null;
        }

        // Crypto Spot Logic
        let pair = '';
        if (symbol === 'BTC') pair = 'BTCUSDT';
        else if (symbol === 'ETH') pair = 'ETHUSDT';
        else if (symbol === 'BNB') pair = 'BNBUSDT';
        else if (symbol === 'SOL') pair = 'SOLUSDT';
        else if (symbol === 'XRP') pair = 'XRPUSDT';
        else if (symbol === 'DOGE') pair = 'DOGEUSDT';
        else if (symbol === 'ADA') pair = 'ADAUSDT';

        if (!pair) {
            // Fallback for custom added stocks (e.g. LTC -> LTCUSDT)
            // We assume if it's not one of the known ones, we append USDT
            pair = `${symbol.toUpperCase()}USDT`;
        }

        try {
            const baseUrl = binanceService.getProxyUrl();
            const res = await fetch(`${baseUrl}/binance-spot/api/v3/klines?symbol=${pair}&interval=1m&limit=100`);
            if (!res.ok) return null;
            const data = await res.json();

            if (Array.isArray(data) && data.length >= 2) {
                const yesterday = data[data.length - 2];
                const today = data[data.length - 1];

                return {
                    yesterdayHigh: parseFloat(yesterday[2]),
                    yesterdayLow: parseFloat(yesterday[3]),
                    yesterdayClose: parseFloat(yesterday[4]),
                    todayOpen: parseFloat(today[1])
                };
            }
        } catch (e) {
            console.error('Failed to fetch daily stats', e);
        }
        return null;
    },

    getLatestPrices: async () => {
        const prices: Record<string, number> = {};
        try {
            // 1. Get Crypto Prices (Spot)
            const baseUrl = binanceService.getProxyUrl();
            const spotRes = await fetch(`${baseUrl}/binance-spot/api/v3/ticker/price`);
            if (spotRes.ok) {
                const data = await spotRes.json();
                if (Array.isArray(data)) {
                    data.forEach((item: any) => {
                        if (item.symbol === 'BTCUSDT') prices['BTC'] = parseFloat(item.price);
                        if (item.symbol === 'ETHUSDT') prices['ETH'] = parseFloat(item.price);
                        if (item.symbol === 'BNBUSDT') prices['BNB'] = parseFloat(item.price);
                        if (item.symbol === 'SOLUSDT') prices['SOL'] = parseFloat(item.price);
                        if (item.symbol === 'XRPUSDT') prices['XRP'] = parseFloat(item.price);
                        if (item.symbol === 'DOGEUSDT') prices['DOGE'] = parseFloat(item.price);
                        if (item.symbol === 'ADAUSDT') prices['ADA'] = parseFloat(item.price);
                    });
                }
            } else {
                console.error('Proxy Polling Failed:', spotRes.status, spotRes.statusText);
            }

            // 2. Get Gold Price (Futures)
            const goldRes = await fetch(`${baseUrl}/binance-futures/fapi/v1/ticker/price?symbol=XAUUSDT`);
            if (goldRes.ok) {
                const goldData = await goldRes.json();
                if (goldData && goldData.price) {
                    prices['XAU/USD'] = parseFloat(goldData.price);
                }
            }

        } catch (e) { console.error('Price Fetch Error', e); }
        return prices;
    }
};
