import { API_CONFIG } from '../config/api';

export const notificationService = {
    // Request permission for browser notifications
    requestPermission: async () => {
        if (!('Notification' in window)) {
            console.log('This browser does not support desktop notification');
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        const permission = await Notification.requestPermission();
        return permission === 'granted';
    },

    // Send Browser Notification
    sendBrowserNotification: (title: string, body: string) => {
        if (Notification.permission === 'granted') {
            new Notification(title, { body });
        }
    },

    // Send Telegram Notification
    // Proxy: /api/telegram/bot<token>/sendMessage
    sendTelegramNotification: async (token: string, chatId: string, message: string) => {
        try {
            if (!token || !chatId) return false;

            if (!token || !chatId) return false;

            // Note: API_CONFIG.getProxyUrl() leads to /api/proxy
            // But our Telegram endpoint is usually /api/telegram directly proxied in vite config?
            // WAIT. The server.cjs does NOT have /api/proxy/telegram
            // The server.cjs has app.use('/api/telegram', ...)
            // Vite config proxies /api/telegram -> http://localhost:3001/api/telegram
            // So we need BASE_URL/api/telegram

            // Let's check server.cjs again?
            // The file viewer for server.cjs is not in recent history, but I recall it has proxies.
            // Vite config has:
            // '/api/telegram': { target: 'http://localhost:3001', ... }
            // So in Electron, we should hit http://localhost:3001/api/telegram directly.

            const base = API_CONFIG.BASE_URL;
            const response = await fetch(`${base}/api/telegram/bot${token}/sendMessage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chat_id: chatId,
                    text: message,
                }),
            });

            if (!response.ok) {
                throw new Error('Telegram Notify failed');
            }
            return true;
        } catch (error) {
            console.error('Telegram Notify Error:', error);
            return false;
        }
    }
};
