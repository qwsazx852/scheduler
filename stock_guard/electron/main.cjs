const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;
let serverProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        backgroundColor: '#111827', // dark bg
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    // Remove menu bar
    mainWindow.setMenuBarVisibility(false);

    // Load app
    if (process.env.NODE_ENV === 'development') {
        // In dev, wait for localhost:5173
        setTimeout(() => {
            mainWindow.loadURL('http://localhost:5173');
        }, 3000);
    } else {
        // In prod, load index.html
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startServer() {
    try {
        const serverPath = path.join(__dirname, '../server.cjs');
        require(serverPath);
        console.log('Backend server started via require');
    } catch (err) {
        console.error('Failed to start server:', err);
    }
}


app.on('ready', () => {
    startServer();
    createWindow();
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', function () {
    if (mainWindow === null) createWindow();
});

app.on('before-quit', () => {
    if (serverProcess) {
        serverProcess.kill();
    }
});
