
import { API_CONFIG } from '../config/api';

export interface NewsItem {
    id: string;
    content: string;
    content_text: string;
    display_time: number;
    score: number;
    title?: string;
}

export const newsService = {
    getLatestNews: async (): Promise<NewsItem[]> => {
        try {
            const baseUrl = API_CONFIG.getProxyUrl();
            const res = await fetch(`${baseUrl}/wscn/news`);
            if (!res.ok) throw new Error('Failed to fetch news');

            const json = await res.json();
            if (json.code === 20000 && json.data && Array.isArray(json.data.items)) {
                return json.data.items.map((item: any) => ({
                    id: String(item.id),
                    content: item.content,
                    content_text: item.content_text,
                    display_time: item.display_time,
                    score: item.score,
                    title: item.title
                }));
            }
            return [];
        } catch (e) {
            console.error('News Service Error:', e);
            return [];
        }
    }
};
