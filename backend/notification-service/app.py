from fastapi import FastAPI, WebSocket, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from typing import List, Dict, Any
from .notification_manager import NotificationManager, Notification, NotificationType

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
notification_manager = NotificationManager()

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await notification_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Process any client messages if needed
    except:
        await notification_manager.disconnect(websocket, user_id)

@app.get("/notifications/unread", response_model=List[Notification])
async def get_unread_notifications(token: str = Security(oauth2_scheme)):
    user_id = await get_user_id_from_token(token)  # Implement this function
    return await notification_manager.get_unread_notifications(user_id)

@app.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, token: str = Security(oauth2_scheme)):
    user_id = await get_user_id_from_token(token)  # Implement this function
    await notification_manager.mark_as_read(user_id, notification_id)
    return {"status": "success"}

@app.post("/notifications/send")
async def send_notification(
    notification_data: Dict[str, Any],
    token: str = Security(oauth2_scheme)
):
    # Verify admin/system permissions here
    await notification_manager.send_notification(
        notification_data["user_id"],
        NotificationType(notification_data["type"]),
        notification_data["severity"],
        notification_data["message"],
        notification_data["details"]
    )
    return {"status": "success"}

@app.post("/notifications/broadcast")
async def broadcast_notification(
    notification_data: Dict[str, Any],
    token: str = Security(oauth2_scheme)
):
    # Verify admin/system permissions here
    await notification_manager.broadcast_notification(
        NotificationType(notification_data["type"]),
        notification_data["severity"],
        notification_data["message"],
        notification_data["details"]
    )
    return {"status": "success"} 