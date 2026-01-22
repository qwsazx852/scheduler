export interface Stock {
    id: string;
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    high: number;
    low: number;
    volume: number;
    openPrice: number;
    alertHigh?: number;
    alertLow?: number;
    isInitialized?: boolean;
    type: 'STOCK' | 'FOREX' | 'CRYPTO' | 'COMMODITY' | 'INDEX';

    // Key Levels for Smart Alerts
    keyLevels?: {
        yesterdayHigh: number;
        yesterdayLow: number;
        yesterdayClose: number;
        todayOpen: number;
        // Fibonacci Retracement (Down from High)
        fib618?: number; // High - (Range * 0.618)
        fib786?: number; // High - (Range * 0.786)
    };

    // Active Smart Alerts
    alertFlags?: {
        touchHigh: boolean;
        touchLow: boolean;
        touchClose: boolean;
        touchOpen: boolean;
        touchFib618?: boolean;
        touchFib786?: boolean;
    };

    // Interval Alert (Notify on every X move)
    intervalStep?: number;
    lastIntervalPrice?: number;
    intervalAlertEnabled?: boolean;
}
