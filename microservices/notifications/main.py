"""
Notifications Microservice for PowerShare Platform
Handles email, push notifications, SMS, and real-time alerts
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pydantic import BaseModel, EmailStr
import uvicorn
import aiohttp
import requests
from jinja2 import Template
import firebase_admin
from firebase_admin import credentials, messaging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PowerShare Notifications Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/powershare")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")

# Redis client
redis_client = redis.from_url(REDIS_URL)

# Initialize Firebase Admin (if credentials available)
firebase_app = None
if FIREBASE_CREDENTIALS_PATH and os.path.exists(FIREBASE_CREDENTIALS_PATH):
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Firebase: {e}")

# Pydantic models
class NotificationRequest(BaseModel):
    user_id: int
    type: str  # email, push, sms, in_app
    title: str
    message: str
    category: str  # trading, alert, system, community
    priority: str = "normal"  # low, normal, high, urgent
    metadata: Optional[Dict[str, Any]] = {}
    scheduled_at: Optional[datetime] = None

class EmailNotification(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    is_html: bool = False
    template: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = {}

class PushNotification(BaseModel):
    user_id: int
    title: str
    body: str
    data: Optional[Dict[str, Any]] = {}
    badge_count: Optional[int] = None

class SMSNotification(BaseModel):
    phone_number: str
    message: str

class NotificationTemplate(BaseModel):
    name: str
    type: str  # email, push, sms
    subject: Optional[str] = None
    content: str
    variables: List[str] = []

# Database helper functions
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def execute_query(query: str, params: tuple = None, fetch: bool = False):
    """Execute database query"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        
        if fetch:
            result = cursor.fetchall()
            conn.close()
            return result
        else:
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")

# Notification handlers
class NotificationHandler:
    def __init__(self):
        self.email_templates = {}
        self.push_templates = {}
        self.sms_templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load notification templates from database"""
        try:
            query = "SELECT * FROM notification_templates WHERE is_active = true"
            templates = execute_query(query, fetch=True)
            
            for template in templates:
                template_obj = {
                    "name": template['name'],
                    "subject": template.get('subject'),
                    "content": template['content'],
                    "variables": template.get('variables', [])
                }
                
                if template['type'] == 'email':
                    self.email_templates[template['name']] = template_obj
                elif template['type'] == 'push':
                    self.push_templates[template['name']] = template_obj
                elif template['type'] == 'sms':
                    self.sms_templates[template['name']] = template_obj
            
            logger.info(f"Loaded {len(templates)} notification templates")
        except Exception as e:
            logger.warning(f"Could not load templates: {e}")
    
    async def send_email(self, notification: EmailNotification) -> bool:
        """Send email notification"""
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = SMTP_USERNAME
            msg['To'] = notification.to_email
            msg['Subject'] = notification.subject
            
            # Process template if specified
            body = notification.body
            if notification.template and notification.template in self.email_templates:
                template_obj = self.email_templates[notification.template]
                template = Template(template_obj['content'])
                body = template.render(**(notification.template_data or {}))
                
                if template_obj['subject']:
                    subject_template = Template(template_obj['subject'])
                    msg['Subject'] = subject_template.render(**(notification.template_data or {}))
            
            # Attach body
            if notification.is_html:
                msg.attach(MimeText(body, 'html'))
            else:
                msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(SMTP_USERNAME, notification.to_email, text)
            server.quit()
            
            logger.info(f"Email sent to {notification.to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def send_push_notification(self, notification: PushNotification) -> bool:
        """Send push notification via Firebase"""
        if not firebase_app:
            logger.warning("Firebase not configured, skipping push notification")
            return False
        
        try:
            # Get user's FCM token from database
            query = "SELECT fcm_token FROM user_devices WHERE user_id = %s AND fcm_token IS NOT NULL"
            tokens = execute_query(query, (notification.user_id,), fetch=True)
            
            if not tokens:
                logger.warning(f"No FCM tokens found for user {notification.user_id}")
                return False
            
            # Send to all user devices
            success_count = 0
            for token_row in tokens:
                try:
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=notification.title,
                            body=notification.body
                        ),
                        data=notification.data or {},
                        token=token_row['fcm_token']
                    )
                    
                    response = messaging.send(message)
                    logger.info(f"Push notification sent: {response}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send push to token {token_row['fcm_token']}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
    
    async def send_sms(self, notification: SMSNotification) -> bool:
        """Send SMS notification via Twilio"""
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            logger.warning("Twilio not configured, skipping SMS")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=notification.message,
                from_='+1234567890',  # Your Twilio phone number
                to=notification.phone_number
            )
            
            logger.info(f"SMS sent: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    async def send_in_app_notification(self, user_id: int, title: str, message: str, category: str, metadata: Dict = None) -> bool:
        """Send in-app notification"""
        try:
            # Store notification in database
            query = """
                INSERT INTO notifications 
                (user_id, title, message, category, metadata, type, status, created_at)
                VALUES (%s, %s, %s, %s, %s, 'in_app', 'unread', %s)
                RETURNING id
            """
            params = (user_id, title, message, category, json.dumps(metadata or {}), datetime.utcnow())
            result = execute_query(query, params, fetch=True)
            
            notification_id = result[0]['id']
            
            # Publish to real-time channel
            channel = f"notifications:{user_id}"
            notification_data = {
                "id": notification_id,
                "title": title,
                "message": message,
                "category": category,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            redis_client.publish(channel, json.dumps(notification_data))
            
            logger.info(f"In-app notification sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send in-app notification: {e}")
            return False
    
    async def process_notification(self, notification: NotificationRequest) -> Dict[str, bool]:
        """Process notification request"""
        results = {}
        
        # Get user details
        query = "SELECT email, phone, notification_preferences FROM users WHERE id = %s"
        user_data = execute_query(query, (notification.user_id,), fetch=True)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_data[0]
        preferences = json.loads(user.get('notification_preferences', '{}'))
        
        # Check if user wants this type of notification
        if notification.type == "email" and preferences.get('email_notifications', True):
            email_notif = EmailNotification(
                to_email=user['email'],
                subject=notification.title,
                body=notification.message
            )
            results['email'] = await self.send_email(email_notif)
        
        if notification.type == "push" and preferences.get('push_notifications', True):
            push_notif = PushNotification(
                user_id=notification.user_id,
                title=notification.title,
                body=notification.message,
                data=notification.metadata
            )
            results['push'] = await self.send_push_notification(push_notif)
        
        if notification.type == "sms" and preferences.get('sms_notifications', False) and user.get('phone'):
            sms_notif = SMSNotification(
                phone_number=user['phone'],
                message=f"{notification.title}: {notification.message}"
            )
            results['sms'] = await self.send_sms(sms_notif)
        
        if notification.type == "in_app":
            results['in_app'] = await self.send_in_app_notification(
                notification.user_id,
                notification.title,
                notification.message,
                notification.category,
                notification.metadata
            )
        
        # Log notification
        await self.log_notification(notification, results)
        
        return results
    
    async def log_notification(self, notification: NotificationRequest, results: Dict[str, bool]):
        """Log notification attempt"""
        try:
            query = """
                INSERT INTO notification_logs 
                (user_id, type, title, message, category, priority, metadata, results, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                notification.user_id,
                notification.type,
                notification.title,
                notification.message,
                notification.category,
                notification.priority,
                json.dumps(notification.metadata),
                json.dumps(results),
                datetime.utcnow()
            )
            execute_query(query, params)
            
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")

# Initialize notification handler
notification_handler = NotificationHandler()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notifications-service", "timestamp": datetime.utcnow()}

@app.post("/send")
async def send_notification(notification: NotificationRequest, background_tasks: BackgroundTasks):
    """Send notification"""
    if notification.scheduled_at and notification.scheduled_at > datetime.utcnow():
        # Schedule for later
        background_tasks.add_task(schedule_notification, notification)
        return {"message": "Notification scheduled", "scheduled_at": notification.scheduled_at}
    else:
        # Send immediately
        results = await notification_handler.process_notification(notification)
        return {"message": "Notification processed", "results": results}

@app.post("/send/email")
async def send_email_notification(notification: EmailNotification):
    """Send email notification directly"""
    success = await notification_handler.send_email(notification)
    return {"success": success, "message": "Email sent" if success else "Email failed"}

@app.post("/send/push")
async def send_push_notification(notification: PushNotification):
    """Send push notification directly"""
    success = await notification_handler.send_push_notification(notification)
    return {"success": success, "message": "Push sent" if success else "Push failed"}

@app.post("/send/sms")
async def send_sms_notification(notification: SMSNotification):
    """Send SMS notification directly"""
    success = await notification_handler.send_sms(notification)
    return {"success": success, "message": "SMS sent" if success else "SMS failed"}

@app.post("/send/batch")
async def send_batch_notifications(notifications: List[NotificationRequest], background_tasks: BackgroundTasks):
    """Send multiple notifications"""
    for notification in notifications:
        background_tasks.add_task(notification_handler.process_notification, notification)
    
    return {"message": f"Batch of {len(notifications)} notifications queued for processing"}

@app.get("/user/{user_id}/notifications")
async def get_user_notifications(
    user_id: int,
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """Get user notifications"""
    query = """
        SELECT * FROM notifications 
        WHERE user_id = %s
    """
    params = [user_id]
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    query += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    notifications = execute_query(query, tuple(params), fetch=True)
    return {"user_id": user_id, "notifications": notifications}

@app.put("/user/{user_id}/notifications/{notification_id}/read")
async def mark_notification_read(user_id: int, notification_id: int):
    """Mark notification as read"""
    query = """
        UPDATE notifications 
        SET status = 'read', read_at = %s 
        WHERE id = %s AND user_id = %s
    """
    execute_query(query, (datetime.utcnow(), notification_id, user_id))
    return {"message": "Notification marked as read"}

@app.delete("/user/{user_id}/notifications/{notification_id}")
async def delete_notification(user_id: int, notification_id: int):
    """Delete notification"""
    query = "DELETE FROM notifications WHERE id = %s AND user_id = %s"
    execute_query(query, (notification_id, user_id))
    return {"message": "Notification deleted"}

@app.get("/templates")
async def get_notification_templates():
    """Get all notification templates"""
    query = "SELECT * FROM notification_templates WHERE is_active = true"
    templates = execute_query(query, fetch=True)
    return {"templates": templates}

@app.post("/templates")
async def create_notification_template(template: NotificationTemplate):
    """Create notification template"""
    query = """
        INSERT INTO notification_templates 
        (name, type, subject, content, variables, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, true, %s)
        RETURNING id
    """
    params = (
        template.name,
        template.type,
        template.subject,
        template.content,
        json.dumps(template.variables),
        datetime.utcnow()
    )
    result = execute_query(query, params, fetch=True)
    
    # Reload templates
    notification_handler.load_templates()
    
    return {"message": "Template created", "template_id": result[0]['id']}

@app.get("/analytics")
async def get_notification_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get notification analytics"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get notification statistics
    query = """
        SELECT 
            type,
            category,
            COUNT(*) as total_sent,
            SUM(CASE WHEN results::json->>'email' = 'true' OR 
                         results::json->>'push' = 'true' OR 
                         results::json->>'sms' = 'true' OR 
                         results::json->>'in_app' = 'true' 
                     THEN 1 ELSE 0 END) as successful_sent,
            DATE(created_at) as date
        FROM notification_logs 
        WHERE created_at BETWEEN %s AND %s
        GROUP BY type, category, DATE(created_at)
        ORDER BY date DESC
    """
    
    analytics = execute_query(query, (start_date, end_date), fetch=True)
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "analytics": analytics
    }

# Background tasks
async def schedule_notification(notification: NotificationRequest):
    """Schedule notification for later delivery"""
    try:
        # Calculate delay
        delay = (notification.scheduled_at - datetime.utcnow()).total_seconds()
        
        if delay > 0:
            await asyncio.sleep(delay)
            await notification_handler.process_notification(notification)
            logger.info(f"Scheduled notification sent to user {notification.user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send scheduled notification: {e}")

# Event listeners
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Notifications Service starting up...")
    
    # Test email configuration
    if SMTP_USERNAME and SMTP_PASSWORD:
        logger.info("Email configuration detected")
    else:
        logger.warning("Email configuration missing")
    
    # Test Firebase configuration
    if firebase_app:
        logger.info("Firebase configuration detected")
    else:
        logger.warning("Firebase configuration missing")

# Real-time notification system
async def listen_for_system_events():
    """Listen for system events that trigger notifications"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('system_events')
    
    while True:
        try:
            message = pubsub.get_message(timeout=1)
            if message and message['type'] == 'message':
                event_data = json.loads(message['data'])
                await process_system_event(event_data)
        except Exception as e:
            logger.error(f"Error processing system event: {e}")
        
        await asyncio.sleep(0.1)

async def process_system_event(event_data: Dict):
    """Process system events and send relevant notifications"""
    event_type = event_data.get('type')
    
    if event_type == 'energy_trade_completed':
        # Notify both buyer and seller
        trade_data = event_data.get('data', {})
        
        # Notify seller
        seller_notification = NotificationRequest(
            user_id=trade_data.get('seller_id'),
            type="push",
            title="Energy Sale Completed",
            message=f"Your energy sale of {trade_data.get('amount')} kWh has been completed!",
            category="trading",
            metadata=trade_data
        )
        await notification_handler.process_notification(seller_notification)
        
        # Notify buyer
        buyer_notification = NotificationRequest(
            user_id=trade_data.get('buyer_id'),
            type="push",
            title="Energy Purchase Completed",
            message=f"Your energy purchase of {trade_data.get('amount')} kWh has been completed!",
            category="trading",
            metadata=trade_data
        )
        await notification_handler.process_notification(buyer_notification)
    
    elif event_type == 'price_alert':
        # Notify users who have price alerts
        alert_data = event_data.get('data', {})
        users_to_notify = alert_data.get('user_ids', [])
        
        for user_id in users_to_notify:
            notification = NotificationRequest(
                user_id=user_id,
                type="push",
                title="Price Alert",
                message=f"Energy price has reached ${alert_data.get('price')}/kWh",
                category="alert",
                metadata=alert_data
            )
            await notification_handler.process_notification(notification)

@app.on_event("startup")
async def start_event_listener():
    """Start system event listener"""
    asyncio.create_task(listen_for_system_events())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
