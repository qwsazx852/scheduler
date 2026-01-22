import { useState, useEffect, useRef } from 'react';
import type { Stock } from '../types';
import { mockStockService } from '../services/mockStockService';
import { notificationService } from '../services/notificationService';
import { binanceService } from '../services/binanceService';
import { yahooService } from '../services/yahooService';

export function useStocks() {
    // Initialize stocks from localStorage or Mock Service
    // Initialize stocks from localStorage or Mock Service
    const [stocks, setStocks] = useState<Stock[]>(() => {
        const initial = mockStockService.getStocks();
        // New Load Logic: Try to load 'stock_guard_user_stocks' first
        const savedFull = localStorage.getItem('stock_guard_user_stocks');

        if (savedFull) {
            try {
                const parsedFull = JSON.parse(savedFull);
                if (Array.isArray(parsedFull) && parsedFull.length > 0) {
                    // Re-hydrate saved stocks
                    const hydrate = (s: any) => ({
                        id: s.id,
                        symbol: s.symbol,
                        name: s.name,
                        type: s.type || 'CRYPTO',
                        price: 0, // Reset price on load to avoid stale data
                        openPrice: 0,
                        change: 0,
                        changePercent: 0,
                        high: 0,
                        low: 0,
                        volume: 0,
                        isInitialized: false,
                        alertHigh: s.alertHigh,
                        alertLow: s.alertLow,
                        alertFlags: s.alertFlags
                    });

                    // Remove deprecated types or IDs
                    const loadedStocks = parsedFull.map(hydrate).filter((s: Stock) =>
                        s.type !== 'STOCK' && s.id !== 'gold_kraken'
                    );

                    // MERGE STEP: Check if any "Initial" stocks are missing from "Saved" (e.g. New Feature Stocks)
                    const missingDefaults = initial.filter(def => !loadedStocks.find((s: Stock) => s.id === def.id));

                    if (missingDefaults.length > 0) {
                        console.log('Merging new default stocks:', missingDefaults);
                        return [...loadedStocks, ...missingDefaults];
                    }

                    return loadedStocks;
                }
            } catch (e) { console.error('Failed to load user stocks', e); }
        }

        // Fallback for very first load
        return initial;
    });

    // Save alerts to localStorage whenever they change
    useEffect(() => {
        // Persist logic updated to include custom stocks
        // To properly save added stocks, we need to save the list itself, not just alerts.
        // But for simplicity, we will save the *entire* stocks array state to localStorage
        // However, we must merge with "INITIAL" on load if we want updates to the hardcoded list to propagate?
        // Let's stick to saving the whole structure for this "Add Stock" feature to be robust. 
        const dataToSave = stocks.map(s => ({
            id: s.id,
            symbol: s.symbol, // Save symbol to restore custom ones
            name: s.name,     // Save name
            type: s.type,     // Save type
            alertHigh: s.alertHigh,
            alertLow: s.alertLow,
            alertFlags: s.alertFlags
        }));
        localStorage.setItem('stock_guard_user_stocks', JSON.stringify(dataToSave));
    }, [stocks]);

    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

    // Store Telegram credentials
    const [telegramToken, setTelegramToken] = useState(() => localStorage.getItem('stock_guard_tg_token') || '');
    const [telegramChatId, setTelegramChatId] = useState(() => localStorage.getItem('stock_guard_tg_chatid') || '');

    const saveTelegramSettings = (token: string, chatId: string) => {
        setTelegramToken(token);
        setTelegramChatId(chatId);
        localStorage.setItem('stock_guard_tg_token', token);
        localStorage.setItem('stock_guard_tg_chatid', chatId);
    };

    const stocksRef = useRef(stocks);
    stocksRef.current = stocks;

    const tgTokenRef = useRef(telegramToken);
    tgTokenRef.current = telegramToken;

    const tgChatIdRef = useRef(telegramChatId);
    tgChatIdRef.current = telegramChatId;

    // Helper to check alerts
    const checkAlerts = (stock: Stock, prevStock: Stock) => {
        // Prevent triggering alerts on initial load (0 -> Real Price)
        if (!prevStock.isInitialized || prevStock.price <= 0) return;

        // 1. Traditional Price Alerts
        // High Alert
        if (stock.alertHigh && stock.price >= stock.alertHigh && prevStock.price < stock.alertHigh) {
            const msg = `🚀 ${stock.name} 暴漲！目前 ${stock.price} (設定: > ${stock.alertHigh})`;
            notificationService.sendBrowserNotification('StockGuard 警示', msg);
            if (tgTokenRef.current && tgChatIdRef.current) {
                notificationService.sendTelegramNotification(tgTokenRef.current, tgChatIdRef.current, msg);
            }
        }

        // Low Alert
        if (stock.alertLow && stock.price <= stock.alertLow && prevStock.price > stock.alertLow) {
            const msg = `🔻 ${stock.name} 暴跌！目前 ${stock.price} (設定: < ${stock.alertLow})`;
            notificationService.sendBrowserNotification('StockGuard 警示', msg);
            if (tgTokenRef.current && tgChatIdRef.current) {
                notificationService.sendTelegramNotification(tgTokenRef.current, tgChatIdRef.current, msg);
            }
        }

        // 2. Smart Alerts (Key Levels & Fibonacci)
        // Logic: Check if price crossed the line between prev and current tick.
        if (stock.alertFlags && stock.keyLevels) {
            const { keyLevels } = stock;
            const newAlertFlags = { ...stock.alertFlags };
            const messages: string[] = [];
            let flagsChanged = false;

            const current = stock.price;
            const prev = prevStock.price;

            // Helper to check if crossed a specific level
            const crossed = (level: number) => {
                return (prev < level && current >= level) || (prev > level && current <= level);
            };

            // Touch High (Yesterday High)
            if (newAlertFlags.touchHigh && crossed(keyLevels.yesterdayHigh)) {
                messages.push(`🚀 ${stock.name} 突破昨日最高價 ${keyLevels.yesterdayHigh}`);
                newAlertFlags.touchHigh = false;
                flagsChanged = true;
            }
            // Touch Low (Yesterday Low)
            if (newAlertFlags.touchLow && crossed(keyLevels.yesterdayLow)) {
                messages.push(`🔻 ${stock.name} 跌破昨日最低價 ${keyLevels.yesterdayLow}`);
                newAlertFlags.touchLow = false;
                flagsChanged = true;
            }
            // Touch Close (Yesterday Close)
            if (newAlertFlags.touchClose && crossed(keyLevels.yesterdayClose)) {
                messages.push(`🔵 ${stock.name} 穿越昨日收盤價 ${keyLevels.yesterdayClose}`);
                newAlertFlags.touchClose = false;
                flagsChanged = true;
            }
            // Touch Open (Today Open)
            if (newAlertFlags.touchOpen && crossed(keyLevels.todayOpen)) {
                messages.push(`🟡 ${stock.name} 回到今日開盤價 ${keyLevels.todayOpen}`);
                newAlertFlags.touchOpen = false;
                flagsChanged = true;
            }
            // Fibonacci Alerts
            if (newAlertFlags.touchFib618 && keyLevels.fib618 && crossed(keyLevels.fib618)) {
                messages.push(`📉 ${stock.name} 抵達 0.618 黃金分割位 ${Math.round(keyLevels.fib618)}`);
                newAlertFlags.touchFib618 = false;
                flagsChanged = true;
            }
            if (newAlertFlags.touchFib786 && keyLevels.fib786 && crossed(keyLevels.fib786)) {
                messages.push(`📉 ${stock.name} 抵達 0.786 關鍵支撐 ${Math.round(keyLevels.fib786)}`);
                newAlertFlags.touchFib786 = false;
                flagsChanged = true;
            }

            if (messages.length > 0) {
                const title = "StockGuard 觸價通知";
                // Append debug info to the last message or summary
                const debugInfo = `(Prev: ${prev} -> Curr: ${current})`;
                // Join all messages
                const fullMessage = `${messages.join('\n')}\n${debugInfo}`;

                notificationService.sendBrowserNotification(title, fullMessage);
                if (tgTokenRef.current && tgChatIdRef.current) {
                    notificationService.sendTelegramNotification(tgTokenRef.current, tgChatIdRef.current, `${title}\n${fullMessage}`);
                }
            }

            if (flagsChanged) {
                stock.alertFlags = newAlertFlags;
            }
        }
    };

    // 1. No Simulation needed for Real-time only app
    // We strictly rely on the WebSocket below to push updates.

    // 2. Real-time Binance Integration
    useEffect(() => {
        // A. Initial Fetch via REST (to populate data immediately)
        const fetchInitialPrices = async () => {
            // 1. Get Binance Prices
            const latestPrices = await binanceService.getLatestPrices();

            // 2. Get Yahoo Prices (DXY & Silver & Gold & Indices)
            const dxyPrice = await yahooService.getLatestPrice('DX-Y.NYB');
            const goldPrice = await yahooService.getLatestPrice('GC=F');
            const silverPrice = await yahooService.getLatestPrice('SI=F');
            const sp500Price = await yahooService.getLatestPrice('ES=F');
            const djiPrice = await yahooService.getLatestPrice('YM=F');
            const nasdaqPrice = await yahooService.getLatestPrice('NQ=F');
            const vixPrice = await yahooService.getLatestPrice('^VIX');

            setStocks(prev => prev.map(s => {
                let currentPrice = s.price;

                // Binance Prices
                if (latestPrices[s.symbol]) {
                    currentPrice = latestPrices[s.symbol];
                }
                // Special mapping for Binance Gold (XAU/USD -> XAU/USD Key in latestPrices)
                else if (s.id === 'gold_binance' && latestPrices['XAU/USD']) {
                    currentPrice = latestPrices['XAU/USD'];
                }
                // Yahoo Prices
                else if (s.id === 'dxy' && dxyPrice !== null) {
                    currentPrice = dxyPrice;
                }
                else if (s.id === 'gold' && goldPrice !== null) {
                    currentPrice = goldPrice;
                }
                else if (s.id === 'silver' && silverPrice !== null) {
                    currentPrice = silverPrice;
                }
                else if (s.id === 'sp500' && sp500Price !== null) {
                    currentPrice = sp500Price;
                }
                else if (s.id === 'dji' && djiPrice !== null) {
                    currentPrice = djiPrice;
                }
                else if (s.id === 'ixic' && nasdaqPrice !== null) {
                    currentPrice = nasdaqPrice;
                }
                else if (s.id === 'vix' && vixPrice !== null) {
                    currentPrice = vixPrice;
                }

                // Calculate change
                if (currentPrice !== s.price) {
                    const openPrice = s.openPrice || currentPrice;
                    const change = Number((currentPrice - openPrice).toFixed(2));
                    const changePercent = openPrice !== 0 ? Number(((change / openPrice) * 100).toFixed(2)) : 0;

                    return {
                        ...s,
                        price: currentPrice, // Use currentPrice here
                        openPrice: s.openPrice === 0 ? currentPrice : s.openPrice, // Use currentPrice here
                        change,
                        changePercent,
                        isInitialized: true // Mark as initialized
                    };
                }
                return s;
            }));
        };
        fetchInitialPrices();

        // Yahoo Polling (every 10s)
        const fetchYahooUpdates = async () => {
            // Fetch all Yahoo assets
            const dxyPrice = await yahooService.getLatestPrice('DX-Y.NYB');
            const goldPrice = await yahooService.getLatestPrice('GC=F');
            const silverPrice = await yahooService.getLatestPrice('SI=F');
            const sp500Price = await yahooService.getLatestPrice('ES=F');
            const djiPrice = await yahooService.getLatestPrice('YM=F');
            const nasdaqPrice = await yahooService.getLatestPrice('NQ=F');
            const vixPrice = await yahooService.getLatestPrice('^VIX');

            setStocks(prev => prev.map(s => {
                let newPrice = null;
                if (s.id === 'dxy') newPrice = dxyPrice;
                if (s.id === 'gold') newPrice = goldPrice;
                if (s.id === 'silver') newPrice = silverPrice;
                if (s.id === 'sp500') newPrice = sp500Price;
                if (s.id === 'dji') newPrice = djiPrice;
                if (s.id === 'ixic') newPrice = nasdaqPrice;
                if (s.id === 'vix') newPrice = vixPrice;

                if (newPrice !== null && newPrice !== s.price) {
                    const openPrice = s.openPrice || newPrice;
                    const change = Number((newPrice - openPrice).toFixed(2));
                    const changePercent = openPrice !== 0 ? Number(((change / openPrice) * 100).toFixed(2)) : 0;

                    const updatedStock = { ...s, price: newPrice, change, changePercent, isInitialized: true };
                    // checkAlerts(updatedStock, s); // Can optionally check alerts here
                    return updatedStock;
                }
                return s;
            }));
            setLastUpdated(new Date());
        };
        const yahooInterval = setInterval(fetchYahooUpdates, 10000);

        // B. WebSocket Subscription
        const updatePrices = (symbol: string, newPrice: number) => {
            setStocks(prev => prev.map(s => {
                let isMatch = false;
                if (s.symbol === symbol) isMatch = true;
                if (symbol === 'XAU/USD' && s.id === 'gold_binance') isMatch = true;

                if (!isMatch) return s;

                const openPrice = s.openPrice || newPrice;
                const change = Number((newPrice - openPrice).toFixed(2));
                const changePercent = openPrice !== 0 ? Number(((change / openPrice) * 100).toFixed(2)) : 0;

                // Interval Alert Logic
                let nextLastIntervalPrice = s.lastIntervalPrice;
                if (s.intervalAlertEnabled && s.intervalStep && s.intervalStep > 0) {
                    const baseline = s.lastIntervalPrice ?? newPrice; // Init if null
                    const diff = newPrice - baseline;

                    if (Math.abs(diff) >= s.intervalStep) {
                        const direction = diff > 0 ? '📈 上漲' : '📉 下跌';
                        const msg = `🔔 ${s.name} ${direction} $${Math.abs(diff).toFixed(2)} (目前: ${newPrice})`;

                        notificationService.sendBrowserNotification('StockGuard 波動警示', msg);
                        if (tgTokenRef.current && tgChatIdRef.current) {
                            notificationService.sendTelegramNotification(tgTokenRef.current, tgChatIdRef.current, msg);
                        }

                        // Update baseline to current price to reset interval
                        nextLastIntervalPrice = newPrice;
                    } else if (s.lastIntervalPrice === undefined) {
                        // Initialize if undefined
                        nextLastIntervalPrice = newPrice;
                    }
                }

                const updatedStock = {
                    ...s,
                    price: newPrice,
                    change,
                    changePercent,
                    lastIntervalPrice: nextLastIntervalPrice, // Update state
                    isInitialized: true
                };

                checkAlerts(updatedStock, s);
                return updatedStock;
            }));
            setLastUpdated(new Date());
        };

        // Connect to Binance
        const cleanupBinance = binanceService.connect(updatePrices);

        return () => {
            cleanupBinance();
            clearInterval(yahooInterval);
        };
    }, []);

    const toggleAlert = (id: string, high?: number, low?: number) => {
        setStocks(prev => prev.map(s => {
            if (s.id === id) {
                return { ...s, alertHigh: high, alertLow: low };
            }
            return s;
        }));
    };

    const updateSmartAlerts = (id: string, flags: any) => {
        setStocks(prev => prev.map(s => {
            if (s.id === id) {
                return { ...s, alertFlags: flags };
            }
            return s;
        }));
    };

    const updateIntervalAlert = (id: string, step: number, enabled: boolean) => {
        setStocks(prev => prev.map(s => {
            if (s.id === id) {
                // When enabling, set current price as baseline to avoid immediate trigger?
                // Or just set params. Logic in updatePrices handles initialization.
                return {
                    ...s,
                    intervalStep: step,
                    intervalAlertEnabled: enabled,
                    // Reset last price on change/enable to current price to start fresh?
                    lastIntervalPrice: enabled ? s.price : undefined
                };
            }
            return s;
        }));
    };

    const addStock = async (symbol: string) => {
        // 1. Check if already exists
        if (stocks.find(s => s.symbol === symbol)) return false;

        // 2. Validate existance via Binance API (Check Price)
        // We'll reuse getLatestPrices (fetching all) or just fetch specific ticker?
        // Let's use getKlines for a quick check or just fetch ticker price
        try {
            // Quick Hack: Try fetching klines for 1 day - if valid, returns array
            const klines = await binanceService.getKlines(symbol);
            if (!klines || klines.length === 0) return false;

            // 3. Create Stock Object
            const newStock: Stock = {
                id: symbol.toLowerCase(),
                symbol: symbol,
                name: symbol, // Use Symbol as name
                type: 'CRYPTO', // Force Crypto for now as we use Binance
                price: 0,
                openPrice: 0,
                change: 0,
                changePercent: 0,
                high: 0,
                low: 0,
                volume: 0,
                isInitialized: false
            };

            setStocks(prev => [...prev, newStock]);

            // 4. Trigger a refresh to get prices immediately if possible
            // The websocket loop relies on restart? 
            // Ideally we should restart connection or update subscriptions if we were filtering streams.
            // Currently binanceService.connect "All Spot" implies hardcoded list?
            // WAIT: binanceService.connectSpot uses a HARDCODED array of streams.
            // We need to update that to be dynamic or subscribe dynamically.
            // For now, let's just Refresh Page prompt or Reload? 
            // Better: Update binanceService to accept list?

            // ACTUALLY: The current binanceService.connectSpot has HARDCODED spot streams.
            // We need to fix binanceService to support dynamic list or restart it.
            // For this step, simply adding to state.
            // *Re-connection is needed.*

            return true;
        } catch (e) {
            console.error(e);
            return false;
        }
    };

    // 1. Fetch Daily Stats on Init
    // 3. Fetch Daily Stats (with retry logic)
    // We fetch on init, and then refresh every 10 minutes to keep 'Today Open' somewhat fresh (though it doesn't change intraday usually)
    // Importantly, if it fails (null), we want to retry or at least have the chance to fetch again.
    useEffect(() => {
        let isMounted = true;

        const fetchStats = async () => {
            if (!isMounted) return;

            // We only need to fetch for items that don't have keyLevels yet, or refresh all.
            // For simplicity, refresh all.
            const updatedStocks = await Promise.all(stocksRef.current.map(async (s) => {
                if (s.type === 'CRYPTO' || s.type === 'COMMODITY' || s.type === 'FOREX' || s.type === 'INDEX') {
                    // If we already have levels, maybe we don't need to spam API?
                    // But let's fetch to ensure we have latest.
                    try {
                        let stats;
                        if (s.id === 'dxy' || s.id === 'silver' || s.id === 'gold' || s.id === 'vix' || s.type === 'INDEX') {
                            stats = await yahooService.getDailyStats(s.symbol);
                        } else {
                            stats = await binanceService.getDailyStats(s.symbol);
                        }

                        if (stats) {
                            return { ...s, keyLevels: stats };
                        }
                    } catch (e) {
                        console.error(`Error fetching stats for ${s.symbol}`, e);
                    }
                }
                return s;
            }));

            if (isMounted) {
                setStocks(prev => {
                    return prev.map(p => {
                        const newStats = updatedStocks.find(u => u.id === p.id)?.keyLevels;
                        // Only update if we got new valid stats, otherwise keep old (or null)
                        return newStats ? { ...p, keyLevels: newStats } : p;
                    });
                });
            }
        };

        fetchStats();
        // Poll every 60 seconds to retry failures and keep connection alive
        const intervalId = setInterval(fetchStats, 60000);

        return () => {
            isMounted = false;
            clearInterval(intervalId);
        };
    }, []); // Run on mount and keep interval

    // Request permission on load
    useEffect(() => {
        notificationService.requestPermission();
    }, []);

    // Expose refresh function
    const refreshStats = async () => {
        // Force refresh all
        const updatedStocks = await Promise.all(stocksRef.current.map(async (s) => {
            if (s.type === 'CRYPTO' || s.type === 'COMMODITY' || s.type === 'FOREX' || s.type === 'INDEX') {
                try {
                    let stats;
                    if (s.id === 'dxy' || s.id === 'silver' || s.id === 'gold' || s.id === 'vix' || s.type === 'INDEX') {
                        stats = await yahooService.getDailyStats(s.symbol);
                    } else {
                        stats = await binanceService.getDailyStats(s.symbol);
                    }

                    if (stats) {
                        return { ...s, keyLevels: stats };
                    }
                } catch (e) {
                    console.error(`Error fetching stats for ${s.symbol}`, e);
                }
            }
            return s;
        }));

        setStocks(prev => {
            return prev.map(p => {
                const newStats = updatedStocks.find(u => u.id === p.id)?.keyLevels;
                return newStats ? { ...p, keyLevels: newStats } : p;
            });
        });
    };

    return {
        stocks,
        lastUpdated,
        toggleAlert,
        updateSmartAlerts,
        telegramToken,
        telegramChatId,
        saveTelegramSettings,
        refreshStats,
        addStock,
        updateIntervalAlert
    };
}
