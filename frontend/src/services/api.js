const hostname = window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname;
const API_BASE_URL = `http://${hostname}:8001/api`;

export const uploadDocument = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: "POST",
        body: formData,
    });
    if (!response.ok) throw new Error("Upload failed");
    return response.json();
};

export const getDocuments = async () => {
    const response = await fetch(`${API_BASE_URL}/documents`);
    if (!response.ok) throw new Error("Failed to fetch documents");
    return response.json();
};

export const deleteDocument = async (docId) => {
    const response = await fetch(`${API_BASE_URL}/documents/${docId}`, {
        method: "DELETE",
    });
    if (!response.ok) throw new Error("Delete failed");
    return response.json();
};

export const sendChatMessage = async (query, history = [], documentIds = null, responseLanguage = "Auto") => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
            query, 
            history, 
            document_ids: documentIds,
            response_language: responseLanguage
        }),
    });
    if (!response.ok) throw new Error("Chat failed");
    return response.json();
};

export const sendChatMessageStream = async (query, history = [], documentIds = null, responseLanguage = "Auto", onChunk) => {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
            query, 
            history, 
            document_ids: documentIds,
            response_language: responseLanguage
        }),
    });
    
    if (!response.ok) throw new Error("Chat stream failed");
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunkStr = decoder.decode(value, { stream: true });
        
        // SSE lines look like `data: {...}\n\n`
        const lines = chunkStr.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.substring(6));
                    onChunk(data);
                } catch (e) {
                    console.error("Error parsing stream chunk:", e, line);
                }
            }
        }
    }
};
