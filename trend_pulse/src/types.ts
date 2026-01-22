export interface Trend {
    rank: number;
    title: string;
    traffic: string; // Display string e.g. "50K+"
    trafficNum?: number; // Raw number for sorting
    description: string;
    pubDate?: string;
    pictureUrl?: string; // Optional, might be simulated or empty
    newsUrl?: string;
    source?: string;

    // New Fields for Trend Analysis
    growthRate?: number; // Percentage e.g. 300
    category?: string; // e.g. "Tech", "Entertainment"
    status?: "Normal" | "Rising" | "Breakout"; // For UI badges
}
