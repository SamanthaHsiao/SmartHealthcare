// 候診大廳 — 本機中繼伺服器（不需要安裝任何套件，Node.js 18 以上即可）
// 用法：node server.js   然後主持人開 http://localhost:8000，觀眾掃 QR code 進入。
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const PORT = process.env.PORT || 8000;
const HTML = path.join(__dirname, 'index.html');
const clients = new Set(); // 所有已連線的 SSE 客戶端（主持人與觀眾手機）

// 取得同一個 Wi-Fi 下，手機可以連到的區網 IP
function lanIP() {
  for (const list of Object.values(os.networkInterfaces())) {
    for (const i of list || []) {
      if (i.family === 'IPv4' && !i.internal) return i.address;
    }
  }
  return 'localhost';
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');

  // 遊戲頁面
  if (req.method === 'GET' && url.pathname === '/') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    return fs.createReadStream(HTML).pipe(res);
  }

  // 觀眾要用的網址（給主持人畫面產生 QR code）
  if (req.method === 'GET' && url.pathname === '/info') {
    res.writeHead(200, { 'content-type': 'application/json' });
    return res.end(JSON.stringify({ joinUrl: `http://${lanIP()}:${PORT}/?p=1` }));
  }

  // 即時訊息串流（Server-Sent Events）
  if (req.method === 'GET' && url.pathname === '/events') {
    res.writeHead(200, {
      'content-type': 'text/event-stream',
      'cache-control': 'no-cache',
      connection: 'keep-alive',
    });
    res.write(': connected\n\n');
    clients.add(res);
    req.on('close', () => clients.delete(res));
    return;
  }

  // 收到一則訊息，轉發給所有客戶端
  if (req.method === 'POST' && url.pathname === '/send') {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 100000) req.destroy(); // 避免過大的請求
    });
    req.on('end', () => {
      try {
        const msg = JSON.parse(body);
        const line = `data: ${JSON.stringify(msg)}\n\n`;
        for (const client of clients) client.write(line);
        res.writeHead(204);
        res.end();
      } catch (err) {
        res.writeHead(400);
        res.end();
      }
    });
    return;
  }

  res.writeHead(404);
  res.end();
});

server.listen(PORT, () => {
  console.log('候診大廳已啟動');
  console.log(`主持人畫面：http://localhost:${PORT}`);
  console.log(`觀眾掃碼網址：http://${lanIP()}:${PORT}/?p=1`);
  console.log('（手機與電腦需要連到同一個 Wi-Fi）');
});
