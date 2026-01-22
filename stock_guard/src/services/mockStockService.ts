import type { Stock } from '../types';


const INITIAL_STOCKS: Stock[] = [
    // Crypto (Top Market Cap)
    { id: 'btc', symbol: 'BTC', name: 'Bitcoin', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'CRYPTO' },
    { id: 'eth', symbol: 'ETH', name: 'Ethereum', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'CRYPTO' },
    { id: 'bnb', symbol: 'BNB', name: 'Binance Coin', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'CRYPTO' },
    { id: 'sol', symbol: 'SOL', name: 'Solana', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'CRYPTO' },
    { id: 'xrp', symbol: 'XRP', name: 'Ripple', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'CRYPTO' },
    { id: 'doge', symbol: 'DOGE', name: 'Dogecoin', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'CRYPTO' },
    { id: 'ada', symbol: 'ADA', name: 'Cardano', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'CRYPTO' },

    // Commodities
    // Commodities (Yahoo Futures & Binance)
    { id: 'gold', symbol: 'GC=F', name: '黃金 (Yahoo)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'COMMODITY' },
    { id: 'gold_binance', symbol: 'XAU/USD', name: '黃金 (Binance)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'COMMODITY' },
    { id: 'silver', symbol: 'SI=F', name: '白銀 (Yahoo)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'COMMODITY' },
    { id: 'dxy', symbol: 'DX-Y.NYB', name: '美元指數 (DXY)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'FOREX' },

    // US Indices (Yahoo Finance Futures for 24/7)
    { id: 'sp500', symbol: 'ES=F', name: 'S&P 500 (Fut)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'INDEX' },
    { id: 'dji', symbol: 'YM=F', name: 'Dow Jones (Fut)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'INDEX' },
    { id: 'ixic', symbol: 'NQ=F', name: 'Nasdaq (Fut)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'INDEX' },
    { id: 'vix', symbol: '^VIX', name: '恐慌指數 (VIX)', price: 0, openPrice: 0, change: 0, changePercent: 0, high: 0, low: 0, volume: 0, type: 'INDEX' },
];

export const mockStockService = {
    getStocks: (): Stock[] => {
        return INITIAL_STOCKS;
    },

    // No more simulation needed for real-time app
    updatePrice: (stocks: Stock[]): Stock[] => {
        return stocks;
    }
};
