
import React, { useEffect, useRef, memo } from 'react';

export const EconomicCalendar: React.FC = memo(() => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // Clear previous content
        containerRef.current.innerHTML = '';

        const script = document.createElement('script');
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-events.js";
        script.type = 'text/javascript';
        script.async = true;
        script.innerHTML = JSON.stringify({
            "colorTheme": "dark",
            "isTransparent": true,
            "width": "100%",
            "height": "100%",
            "locale": "zh",
            "importanceFilter": "-1,0,1", // Show all importance levels
            "currencyFilter": "USD,EUR,GBP,JPY,CNY", // Filter relevant currencies
            "countryFilter": "us,eu,gb,jp,cn"
        });

        containerRef.current.appendChild(script);
    }, []);

    return (
        <div className="bg-gray-800 rounded-lg p-4 h-full flex flex-col">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="mr-2">📅</span> 財經日曆 (TradingView)
            </h2>

            <div className="flex-1 bg-gray-900 rounded overflow-hidden relative">
                <div className="tradingview-widget-container" ref={containerRef} style={{ height: '100%', width: '100%' }}>
                    <div className="tradingview-widget-container__widget" style={{ height: '100%', width: '100%' }}></div>
                </div>
            </div>

            <div className="mt-2 text-xs text-center text-gray-500">
                Source: TradingView
            </div>
        </div>
    );
});
