import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { streamAIMessage } from "../api/api";
import { marked } from "marked";
import ProductCard from "./ProductCard";
import CompatibilityBadge from "./CompatibilityBadge";
import TypingIndicator from "./TypingIndicator";

function ChatWindow() {
    const defaultMessage = [{
        role: "assistant",
        content: "Hi! I'm your PartSelect assistant. I can help you with refrigerator and dishwasher parts."
    }];

    const [messages, setMessages] = useState(defaultMessage);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [thinkingMessage, setThinkingMessage] = useState("");

    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSend = async () => {
        if (input.trim() === "" || isLoading) return;

        const userMessage = input;
        setInput("");
        setIsLoading(true);
        setThinkingMessage("");

        // Add user message
        setMessages(prev => [...prev, {
            role: "user",
            content: userMessage
        }]);

        // Create placeholder for assistant response
        const assistantMessageIndex = messages.length + 1;
        let assistantContent = "";
        let products = [];
        let compatibility = null;

        setMessages(prev => [...prev, {
            role: "assistant",
            content: "",
            products: [],
            compatibility: null,
            isStreaming: true
        }]);

        // Prepare conversation history (last 5 messages)
        const conversationHistory = messages.slice(-5).map(msg => ({
            role: msg.role,
            content: msg.content
        }));

        // Stream response
        await streamAIMessage(userMessage, conversationHistory, (chunk) => {
            if (chunk.type === 'thinking') {
                setThinkingMessage(chunk.content);
            }
            else if (chunk.type === 'text') {
                assistantContent += chunk.content;
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                        ...newMessages[assistantMessageIndex],
                        content: assistantContent
                    };
                    return newMessages;
                });
            }
            else if (chunk.type === 'product') {
                products.push(chunk.content);
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                        ...newMessages[assistantMessageIndex],
                        products: [...products]
                    };
                    return newMessages;
                });
            }
            else if (chunk.type === 'compatibility') {
                compatibility = chunk.content;
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                        ...newMessages[assistantMessageIndex],
                        compatibility: compatibility
                    };
                    return newMessages;
                });
            }
            else if (chunk.type === 'done') {
                setIsLoading(false);
                setThinkingMessage("");
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                        ...newMessages[assistantMessageIndex],
                        isStreaming: false
                    };
                    return newMessages;
                });
            }
            else if (chunk.type === 'error') {
                setIsLoading(false);
                setThinkingMessage("");
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                        role: "assistant",
                        content: "Sorry, I encountered an error. Please try again.",
                        error: true
                    };
                    return newMessages;
                });
            }
        });
    };

    return (
        <div className="chat-container">
            <div className="messages-container">
                {messages.map((message, index) => (
                    <div key={index} className={`${message.role}-message-container`}>
                        {/* Products */}
                        {message.products && message.products.length > 0 && (
                            <div className="products-list">
                                {message.products.map((product, idx) => (
                                    <ProductCard key={idx} product={product} />
                                ))}
                            </div>
                        )}

                        {/* Compatibility */}
                        {message.compatibility && (
                            <CompatibilityBadge compatibility={message.compatibility} />
                        )}

                        {/* Text content */}
                        {message.content && (
                            <div className={`message ${message.role}-message`}>
                                <div dangerouslySetInnerHTML={{
                                    __html: marked(message.content).replace(/<p>|<\/p>/g, "")
                                }} />
                            </div>
                        )}
                    </div>
                ))}

                {/* Typing indicator */}
                {isLoading && (
                    <TypingIndicator message={thinkingMessage || "Thinking..."} />
                )}

                <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about refrigerator or dishwasher parts..."
                    onKeyPress={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            handleSend();
                            e.preventDefault();
                        }
                    }}
                    disabled={isLoading}
                />
                <button
                    className="send-button"
                    onClick={handleSend}
                    disabled={isLoading}
                >
                    {isLoading ? "..." : "Send"}
                </button>
            </div>
        </div>
    );
}

export default ChatWindow;