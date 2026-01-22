import { API_CONFIG } from '../config/api';

export const yahooService = {
    // Helper to get dynamic backend URL
    getProxyUrl: () => {
        return API_CONFIG.getProxyUrl();
    },

    getLatestPrice: async (symbol: string): Promise<number | null> => {
        try {
            const baseUrl = yahooService.getProxyUrl();
            // Yahoo Finance Chart API v8
            // Endpoint: /v8/finance/chart/{symbol}?interval=1m&range=1d
            const res = await fetch(`${baseUrl}/yahoo/v8/finance/chart/${symbol}?interval=1m&range=1d`);

            if (!res.ok) return null;

            const data = await res.json();
            if (data.chart && data.chart.result && data.chart.result[0]) {
                const meta = data.chart.result[0].meta;
                return meta.regularMarketPrice;
            }
            return null;
        } catch (e) {
            console.error('Yahoo Fetch Error', e);
            return null;
        }
    },

    getDailyStats: async (symbol: string): Promise<any | null> => {
        try {
            const baseUrl = yahooService.getProxyUrl();
            // Fetch 5 days of data to get yesterday and today
            const res = await fetch(`${baseUrl}/yahoo/v8/finance/chart/${symbol}?interval=1d&range=5d`);
            if (!res.ok) return null;

            const data = await res.json();
            if (data.chart && data.chart.result && data.chart.result[0]) {
                const result = data.chart.result[0];
                const quotes = result.indicators.quote[0];
                const timestamps = result.timestamp;

                if (!timestamps || timestamps.length < 2) return null;

                // Index of yesterday (2nd to last) and today (last)
                // Note: Yahoo sometimes returns nulls in quotes if market is closed or holidays?
                // We should find the last two valid candles.

                let validCandles = [];
                for (let i = 0; i < timestamps.length; i++) {
                    if (quotes.high[i] !== null && quotes.low[i] !== null && quotes.close[i] !== null && quotes.open[i] !== null) {
                        validCandles.push({
                            high: quotes.high[i],
                            low: quotes.low[i],
                            open: quotes.open[i],
                            close: quotes.close[i]
                        });
                    }
                }

                if (validCandles.length < 2) return null;

                const yesterday = validCandles[validCandles.length - 2];
                const today = validCandles[validCandles.length - 1];

                const high = yesterday.high;
                const low = yesterday.low;
                const range = high - low;

                return {
                    yesterdayHigh: high,
                    yesterdayLow: low,
                    yesterdayClose: yesterday.close,
                    todayOpen: today.open,
                    fib618: high - (range * 0.618),
                    fib786: high - (range * 0.786)
                };
            }
            return null;
        } catch (e) {
            console.error('Yahoo Stats Error', e);
            return null;
        }
    }
};
