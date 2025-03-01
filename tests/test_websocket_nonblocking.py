import pytest
import asyncio
import websockets
import json
import time
import httpx

WS_URL = "ws://localhost:8000/chat_ws"  # Change if using a different port
API_URL = "http://localhost:8000/get_post/1"  # Example API endpoint to test non-blocking behavior

@pytest.mark.asyncio
async def test_websocket_nonblocking():
    """Test that WebSocket AI generation does NOT block HTTP requests"""

    async with websockets.connect(WS_URL) as websocket:
        welcome_message = await websocket.recv()
        assert "AI: Welcome!" in welcome_message  # Ensure initial connection works

        test_message = {
            "markdown": "# AI Study Guide\n## Topic: Backpropagation",
            "prompt": "Explain this topic in simple terms."
        }

        start_time = time.time()  # Start timer

        # Send WebSocket request (AI processing will take time)
        await websocket.send(json.dumps(test_message))

        # While waiting for AI response, make an HTTP request to see if it's blocked
        async with httpx.AsyncClient() as client:
            http_start = time.time()
            response = await client.get(API_URL, headers={"User-ID": "testuser", 'csrf-token': "lofasz"})  # Simulate an API request
            http_end = time.time()

        end_time = time.time()  # Stop timer

        # WebSocket should still be waiting, while HTTP request finishes fast
        assert response.status_code in [200, 404]  # Ensure the HTTP request did NOT get blocked

        # Check if HTTP request finished before WebSocket response
        assert http_end - http_start < 2, "HTTP request was blocked by WebSocket AI processing!"

        # Now receive AI response (this should come later)
        ai_response = await websocket.recv()

        # Expanded list of expected keywords
        expected_keywords = [
            "AI", "backpropagation", "machine learning", "deep learning", "neural network",
            "gradient descent", "activation function", "loss function", "weight update",
            "bias", "optimization", "learning rate", "dropout", "convolutional", "LSTM",
            "transformer", "self-attention", "feedforward", "reinforcement learning",
            "supervised learning", "unsupervised learning", "classification", "regression"
        ]

        assert any(word in ai_response.lower() for word in expected_keywords), \
            f"Expected one of {expected_keywords} in response, but got: {ai_response}"

        print(f"Total Test Time: {end_time - start_time:.2f}s")
        print(f"HTTP Request Time: {http_end - http_start:.2f}s")
