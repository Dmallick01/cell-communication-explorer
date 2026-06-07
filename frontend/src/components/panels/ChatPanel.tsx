"use client";

import { useState } from "react";
import { sendChatMessage } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export default function ChatPanel({ jobId }: { jobId: string }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: 'Ask about cell types, top interactions, QC, methods, or literature. Example: "top interactions"',
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const { reply } = await sendChatMessage(jobId, text);
      setMessages((m) => [...m, { role: "assistant", text: reply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: err instanceof Error ? err.message : "Chat failed" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="group-header">
        <span>Research chat</span>
        <span className="group-count">results-grounded</span>
      </div>

      <div className="chat-log">
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>
            <strong>{m.role === "user" ? "You" : "CCE"}:</strong>
            <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", marginTop: 4 }}>
              {m.text}
            </pre>
          </div>
        ))}
        {loading && <div className="chat-msg assistant">Thinking…</div>}
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          className="control-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your analysis…"
          disabled={loading}
        />
        <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
