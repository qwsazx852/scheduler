export const API_CONFIG = {
    // Detect if running in Electron (via user agent or file protocol)
    // or just assume localhost:3001 for dev/prod if not on a remote server.
    // Since this is a local desktop app, the backend is ALWAYS localhost:3001.
    BASE_URL: (function () {
        if (typeof window === 'undefined') return 'http://localhost:3001';

        // In Electron, protocol is 'file:'
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3001';
        }

        // In Vite Dev, protocol is 'http:', hostname is 'localhost'
        // We can use relative path or localhost.
        // To be consistent, let's use localhost:3001 for everything if we are local.
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3001';
        }

        // In case deployed to Vercel/Netlify for some reason (not this case)
        return '';
    })(),

    getProxyUrl: () => {
        // Return full URL: http://localhost:3001/api/proxy
        // This avoids relative path issues in Electron
        const base = API_CONFIG.BASE_URL;
        return `${base}/api/proxy`;
    }
};
