import { useEffect, useState } from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface DataPoint {
    time: string;
    value: number;
}

interface TrendChartProps {
    keyword: string;
    color?: string;
}

export function TrendChart({ keyword, color = "#3b82f6" }: TrendChartProps) {
    const [data, setData] = useState<DataPoint[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const res = await fetch(`/api/trends/interest/${encodeURIComponent(keyword)}`);
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                }
            } catch (error) {
                console.error("Failed to fetch chart data", error);
            }
            setLoading(false);
        };

        fetchData();
    }, [keyword]);

    if (loading) {
        return (
            <div className="h-48 w-full flex items-center justify-center bg-slate-900/50 rounded-lg animate-pulse">
                <span className="text-slate-500 text-sm">載入趨勢數據...</span>
            </div>
        );
    }

    return (
        <div className="w-full h-48 bg-slate-900/30 rounded-lg p-2">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id={`color-${keyword}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis
                        dataKey="time"
                        hide={true}
                    />
                    <YAxis
                        hide={true}
                        domain={[0, 100]}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                        itemStyle={{ color: color }}
                        labelStyle={{ display: 'none' }}
                        formatter={(value: number) => [value, '熱度']}
                    />
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        strokeWidth={2}
                        fillOpacity={1}
                        fill={`url(#color-${keyword})`}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
