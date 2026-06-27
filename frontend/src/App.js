import { useState, useRef, useEffect } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const SUGGESTIONS = [
  "Recommend a good Kindle",
  "What's the best Fire tablet?",
  "Check order #12345",
  "Best charger for Kindle",
];

function Message({ role, content }) {
  return (
    <div style={{
      display: "flex",
      justifyContent: role === "user" ? "flex-end" : "flex-start",
      marginBottom: 12,
    }}>
      {role === "assistant" && (
        <div style={{
          width: 32, height: 32, borderRadius: "50%",
          background: "#6366f1", color: "white",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 16, marginRight: 8, flexShrink: 0, alignSelf: "flex-end",
        }}>🛍️</div>
      )}
      <div style={{
        maxWidth: "70%",
        padding: "10px 14px",
        borderRadius: role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
        background: role === "user" ? "#6366f1" : "#f1f5f9",
        color: role === "user" ? "white" : "#1e293b",
        fontSize: 14,
        lineHeight: 1.6,
        whiteSpace: "pre-wrap",
      }}>
        {content}
      </div>
      {role === "user" && (
        <div style={{
          width: 32, height: 32, borderRadius: "50%",
          background: "#e2e8f0", color: "#64748b",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 16, marginLeft: 8, flexShrink: 0, alignSelf: "flex-end",
        }}>👤</div>
      )}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div style={{ display: "flex", alignItems: "center", marginBottom: 12 }}>
      <div style={{
        width: 32, height: 32, borderRadius: "50%",
        background: "#6366f1", color: "white",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 16, marginRight: 8, flexShrink: 0,
      }}>🛍️</div>
      <div style={{
        padding: "10px 16px", borderRadius: "18px 18px 18px 4px",
        background: "#f1f5f9", display: "flex", gap: 4, alignItems: "center",
      }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 8, height: 8, borderRadius: "50%", background: "#94a3b8",
            animation: "bounce 1.2s infinite",
            animationDelay: `${i * 0.2}s`,
          }} />
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    const userMsg = text || input.trim();
    if (!userMsg || loading) return;

    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Connection error. Make sure the backend is running on port 8000.",
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; }
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
        textarea:focus { outline: none; }
        textarea { resize: none; font-family: inherit; }
      `}</style>

      <div style={{ height: "100vh", display: "flex", flexDirection: "column", maxWidth: 720, margin: "0 auto" }}>

        {/* Header */}
        <div style={{
          padding: "16px 20px", borderBottom: "1px solid #e2e8f0",
          background: "white", display: "flex", alignItems: "center", gap: 12,
        }}>
          <div style={{
            width: 40, height: 40, borderRadius: "50%",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20,
          }}>🛍️</div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 16, color: "#1e293b" }}>ShopBot</div>
            <div style={{ fontSize: 12, color: "#22c55e", display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#22c55e" }} />
              Online
            </div>
          </div>
          {messages.length > 0 && (
            <button
              onClick={() => setMessages([])}
              style={{
                marginLeft: "auto", padding: "6px 12px", borderRadius: 8,
                border: "1px solid #e2e8f0", background: "white",
                fontSize: 12, color: "#64748b", cursor: "pointer",
              }}
            >Clear chat</button>
          )}
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 16px", display: "flex", flexDirection: "column" }}>

          {/* Welcome + suggestions */}
          {messages.length === 0 && (
            <div style={{ textAlign: "center", marginTop: 60 }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🛍️</div>
              <h2 style={{ fontSize: 22, fontWeight: 600, color: "#1e293b", marginBottom: 8 }}>
                Hi! I'm ShopBot
              </h2>
              <p style={{ color: "#64748b", fontSize: 14, marginBottom: 32 }}>
                I can help you find products, read reviews, and check order status.
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
                {SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    style={{
                      padding: "8px 16px", borderRadius: 20,
                      border: "1px solid #e2e8f0", background: "white",
                      fontSize: 13, color: "#374151", cursor: "pointer",
                      transition: "all 0.15s",
                    }}
                    onMouseOver={e => e.target.style.borderColor = "#6366f1"}
                    onMouseOut={e => e.target.style.borderColor = "#e2e8f0"}
                  >{s}</button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <Message key={i} role={msg.role} content={msg.content} />
          ))}

          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{
          padding: "12px 16px", borderTop: "1px solid #e2e8f0", background: "white",
        }}>
          <div style={{
            display: "flex", gap: 8, alignItems: "flex-end",
            border: "1px solid #e2e8f0", borderRadius: 12, padding: "8px 12px",
            background: "white", transition: "border-color 0.15s",
          }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything... (Enter to send)"
              rows={1}
              style={{
                flex: 1, border: "none", fontSize: 14, color: "#1e293b",
                background: "transparent", lineHeight: 1.5, maxHeight: 120,
                overflowY: "auto",
              }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              style={{
                width: 36, height: 36, borderRadius: 8, border: "none",
                background: input.trim() && !loading ? "#6366f1" : "#e2e8f0",
                color: input.trim() && !loading ? "white" : "#94a3b8",
                cursor: input.trim() && !loading ? "pointer" : "default",
                fontSize: 16, display: "flex", alignItems: "center", justifyContent: "center",
                transition: "all 0.15s", flexShrink: 0,
              }}
            >↑</button>
          </div>
          <p style={{ fontSize: 11, color: "#94a3b8", textAlign: "center", marginTop: 6 }}>
            ShopBot · Powered by AI · Electronics store assistant
          </p>
        </div>

      </div>
    </>
  );
}