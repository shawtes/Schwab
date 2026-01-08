import { WebSocket, WebSocketServer } from "ws";
import { getQuote, getOrderBook, listSymbols } from "./src/lib/mock-data";

const PORT = 4001;
const wss = new WebSocketServer({ port: PORT });

console.log(`🚀 Mock WebSocket server running on ws://localhost:${PORT}`);

interface Client {
  ws: WebSocket;
  symbols: Set<string>;
}

const clients: Client[] = [];

wss.on("connection", (ws: WebSocket) => {
  console.log("✅ Client connected");

  const client: Client = {
    ws,
    symbols: new Set()
  };
  clients.push(client);

  ws.on("message", (data: Buffer) => {
    try {
      const message = JSON.parse(data.toString());

      if (message.type === "subscribe") {
        const symbols = message.symbols as string[];
        symbols.forEach((sym) => client.symbols.add(sym));
        console.log(`📊 Client subscribed to: ${symbols.join(", ")}`);
      }

      if (message.type === "unsubscribe") {
        const symbols = message.symbols as string[];
        symbols.forEach((sym) => client.symbols.delete(sym));
        console.log(`❌ Client unsubscribed from: ${symbols.join(", ")}`);
      }
    } catch (err) {
      console.error("Error parsing message:", err);
    }
  });

  ws.on("close", () => {
    console.log("👋 Client disconnected");
    const idx = clients.indexOf(client);
    if (idx > -1) {
      clients.splice(idx, 1);
    }
  });

  // Send initial data
  setTimeout(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "connected" }));
    }
  }, 100);
});

// Heartbeat every 10 seconds
setInterval(() => {
  clients.forEach((client) => {
    if (client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(JSON.stringify({ type: "heartbeat", ts: Date.now() }));
    }
  });
}, 10000);

// Send quotes every 1 second
setInterval(() => {
  clients.forEach((client) => {
    if (client.ws.readyState === WebSocket.OPEN) {
      client.symbols.forEach((symbol) => {
        try {
          const quote = getQuote(symbol);
          client.ws.send(
            JSON.stringify({
              type: "quote",
              payload: quote
            })
          );
        } catch (err) {
          console.error(`Error sending quote for ${symbol}:`, err);
        }
      });
    }
  });
}, 1000);

// Send order book updates every 500ms
setInterval(() => {
  clients.forEach((client) => {
    if (client.ws.readyState === WebSocket.OPEN) {
      client.symbols.forEach((symbol) => {
        try {
          const book = getOrderBook(symbol);
          client.ws.send(
            JSON.stringify({
              type: "orderbook",
              payload: book
            })
          );
        } catch (err) {
          console.error(`Error sending orderbook for ${symbol}:`, err);
        }
      });
    }
  });
}, 500);

// Send random trades every 2-5 seconds
function scheduleRandomTrade() {
  const delay = 2000 + Math.random() * 3000;
  setTimeout(() => {
    clients.forEach((client) => {
      if (client.ws.readyState === WebSocket.OPEN && client.symbols.size > 0) {
        const symbols = Array.from(client.symbols);
        const symbol = symbols[Math.floor(Math.random() * symbols.length)];
        const quote = getQuote(symbol);
        const trade = {
          price: quote.last + (Math.random() - 0.5) * 2,
          size: Math.floor(Math.random() * 500 + 50),
          side: Math.random() > 0.5 ? "buy" : "sell",
          ts: Date.now()
        };
        client.ws.send(
          JSON.stringify({
            type: "trade",
            payload: trade
          })
        );
      }
    });
    scheduleRandomTrade();
  }, delay);
}

scheduleRandomTrade();

process.on("SIGINT", () => {
  console.log("\n👋 Shutting down WebSocket server...");
  wss.close(() => {
    console.log("✅ Server closed");
    process.exit(0);
  });
});


