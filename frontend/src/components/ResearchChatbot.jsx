import { useState } from "react";
import "./ResearchChatbot.css";

function ResearchChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    const question = message.trim();

    if (!question || isLoading) {
      return;
    }

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        role: "user",
        content: question,
      },
    ]);

    setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || "Something went wrong."
        );
      }

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content: data.answer || "Not Available",
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the research assistant. Please make sure the backend is running.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          className="research-chatbot-button"
          onClick={() => setIsOpen(true)}
          aria-label="Open Research Assistant"
        >
          ✦
        </button>
      )}

      {isOpen && (
        <div className="research-chatbot-window">

          {/* Header */}
          <div className="research-chatbot-header">

            <div className="research-chatbot-title">

              <div className="research-chatbot-avatar">
                ✦
              </div>

              <div>
                <h3>Research Assistant</h3>
                <p>AI Research Support</p>
              </div>

            </div>

            <button
              className="research-chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>

          </div>

          {/* Messages */}
          <div className="research-chatbot-messages">

            {/* Welcome message */}
            <div className="research-chatbot-message assistant">

              <div className="message-avatar">
                ✦
              </div>

              <div className="message-bubble">
                Hi! 👋
                <br />
                Ask me anything about your uploaded
                research papers and their research domain.
              </div>

            </div>

            {/* Chat messages */}
            {messages.map((chatMessage, index) => (
              <div
                key={index}
                className={`research-chatbot-message ${chatMessage.role}`}
              >

                {chatMessage.role === "assistant" && (
                  <div className="message-avatar">
                    ✦
                  </div>
                )}

                <div className="message-bubble">
                  {chatMessage.content}
                </div>

              </div>
            ))}

            {/* Loading */}
            {isLoading && (
              <div className="research-chatbot-message assistant">

                <div className="message-avatar">
                  ✦
                </div>

                <div className="message-bubble loading-message">
                  Thinking...
                </div>

              </div>
            )}

          </div>

          {/* Input */}
          <div className="research-chatbot-input-area">

            <input
              type="text"
              placeholder="Ask about your research papers..."
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSend();
                }
              }}
              disabled={isLoading}
            />

            <button
              className="research-chatbot-send"
              onClick={handleSend}
              disabled={isLoading || !message.trim()}
              aria-label="Send message"
            >
              ➤
            </button>

          </div>

        </div>
      )}
    </>
  );
}

export default ResearchChatbot;