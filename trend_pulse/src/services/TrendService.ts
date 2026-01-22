import type { Trend } from '../types';

export const TrendService = {
    fetchTrends: async (): Promise<Trend[]> => {
        try {
            console.log("Fetching simulated trends from backend...");
            const response = await fetch('/api/trends/daily');

            if (!response.ok) {
                throw new Error(`Backend API Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            // Map backend response to frontend interface
            return data.map((item: any) => ({
                rank: item.rank,
                title: item.title,
                traffic: item.traffic,
                trafficNum: item.trafficNum,
                description: item.description,
                pubDate: item.pubDate,
                pictureUrl: "",
                newsUrl: item.newsUrl,
                source: item.source,
                growthRate: item.growthRate,
                category: item.category,
                status: item.status
            }));

        } catch (error) {
            console.error('Error fetching trends:', error);
            // Fallback for demo/error state
            return [
                {
                    rank: 1,
                    title: "Backend Connection Failed",
                    traffic: "0",
                    description: String(error),
                    growthRate: 0,
                    category: "Error",
                    status: "Normal"
                }
            ];
        }
    }
};
