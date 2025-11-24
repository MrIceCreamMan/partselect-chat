const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Send message and get complete response (non-streaming)
 */
export const getAIMessage = async (userQuery, conversationHistory = []) => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userQuery,
                conversation_history: conversationHistory,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Format response
        return {
            role: 'assistant',
            content: data.message,
            products: data.products || [],
            compatibility: data.compatibility || null,
            metadata: data.metadata || {},
        };
    } catch (error) {
        console.error('Error getting AI message:', error);
        return {
            role: 'assistant',
            content: 'Sorry, I encountered an error. Please try again.',
            error: true,
        };
    }
};

/**
 * Stream message with Server-Sent Events
 */
export const streamAIMessage = async (userQuery, conversationHistory = [], onChunk) => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userQuery,
                conversation_history: conversationHistory,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Split by newlines to handle multiple SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6); // Remove 'data: ' prefix

                    try {
                        const chunk = JSON.parse(data);
                        onChunk(chunk); // Call callback with parsed chunk

                        if (chunk.type === 'done') {
                            return;
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error streaming message:', error);
        onChunk({
            type: 'error',
            content: { error: 'Failed to stream response' },
        });
    }
};

/**
 * Get conversation history
 */
export const getConversationHistory = async (conversationId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/history/${conversationId}`);

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error getting conversation history:', error);
        return null;
    }
};