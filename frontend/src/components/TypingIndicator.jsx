import React from 'react';
import './TypingIndicator.css';

function TypingIndicator({ message = "Thinking..." }) {
    return (
        <div className="typing-indicator-container">
            <div className="typing-indicator">
                <span>{message}</span>
                <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    );
}

export default TypingIndicator;