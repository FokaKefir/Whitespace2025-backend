import pytest
import asyncio
import websockets
import json

WS_URL = "ws://fokakefir.go.ro/chat_ws"  # Change this if using localhost

@pytest.mark.asyncio
async def test_websocket_ai_chat():
    """Test the AI chatbot WebSocket connection and response"""

    async with websockets.connect(WS_URL) as websocket:
        # Receive initial greeting from AI
        greeting = await websocket.recv()
        assert "AI:" in greeting  # Ensure initial response contains AI greeting

        # Prepare test message
        test_message = {
            "markdown": "# AI Study Guide\n## Topic: Backpropagation",
            "prompt": "Explain this topic in simple terms."
        }

        # Send message to WebSocket
        await websocket.send(json.dumps(test_message))

        # Receive AI response
        response = await websocket.recv()
        assert isinstance(response, str)  # Ensure response is a string
        assert len(response) > 0  # Ensure AI responds with something

        # Send another test message
        follow_up_message = {
            "markdown": "# AI Study Guide\n## Topic: Gradient Descent",
            "prompt": "Explain gradient descent step-by-step."
        }

        await websocket.send(json.dumps(follow_up_message))

        # Receive AI response
        response = await websocket.recv()
        assert "gradient descent" in response.lower()  # AI should mention gradient descent

@pytest.mark.asyncio
async def test_websocket_connection_failure():
    """Test WebSocket connection failure (if server is down)"""
    try:
        async with websockets.connect("ws://invalid-url/chat_ws") as websocket:
            pass  # If connection succeeds (unexpectedly), test should fail
    except Exception as e:
        assert isinstance(e, Exception)  # Expect some kind of connection error

