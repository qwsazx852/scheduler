import { useState, useEffect } from 'react';
import { X, Save, MessageCircle } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  telegramToken: string;
  telegramChatId: string;
  onSave: (token: string, chatId: string) => void;
}

export function SettingsModal({ isOpen, onClose, telegramToken, telegramChatId, onSave }: SettingsModalProps) {
  const [localToken, setLocalToken] = useState(telegramToken);
  const [localChatId, setLocalChatId] = useState(telegramChatId);

  useEffect(() => {
    setLocalToken(telegramToken);
    setLocalChatId(telegramChatId);
  }, [telegramToken, telegramChatId]);

  const handleSave = () => {
    onSave(localToken, localChatId);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold flex items-center space-x-2">
            <MessageCircle className="w-5 h-5 text-blue-400" />
            <span>Telegram 通知設定</span>
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-slate-400">
            請建立 Telegram Bot 並取得 Token 與 Chat ID。
          </p>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Bot Token</label>
            <input
              type="text"
              value={localToken}
              onChange={(e) => setLocalToken(e.target.value)}
              placeholder="123456:ABC-DEF..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 outline-none font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Chat ID</label>
            <input
              type="text"
              value={localChatId}
              onChange={(e) => setLocalChatId(e.target.value)}
              placeholder="12345678"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 outline-none font-mono text-sm"
            />
          </div>

          <div className="flex justify-between pt-4 gap-2">
            <button
              onClick={() => {
                if (Notification.permission === 'granted') {
                  new Notification('StockGuard 測試', { body: '您的瀏覽器通知運作正常！' });
                } else {
                  alert('請先允許瀏覽器通知權限！');
                  Notification.requestPermission();
                }
              }}
              className="text-xs text-slate-400 hover:text-white underline"
            >
              測試瀏覽器通知
            </button>
            <button
              onClick={async () => {
                if (!localToken || !localChatId) {
                  alert('請先輸入 Token 與 Chat ID');
                  return;
                }
                try {
                  const response = await fetch(`/api/telegram/bot${localToken}/sendMessage`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      chat_id: localChatId,
                      text: '🚀 StockGuard Telegram 測試訊息成功！'
                    }),
                  });
                  if (response.ok) {
                    alert('Telegram 測試發送成功！請檢查您的 App。');
                  } else {
                    const err = await response.text();
                    alert(`發送失敗: ${err}`);
                  }
                } catch (e) {
                  alert(`發送錯誤: ${e}`);
                }
              }}
              className="text-xs text-blue-400 hover:text-blue-300 underline"
            >
              測試 Telegram
            </button>
            <button
              onClick={handleSave}
              className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-6 rounded-lg transition-colors"
            >
              <Save className="w-4 h-4 mr-2" />
              儲存設定
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

