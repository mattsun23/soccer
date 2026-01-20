"""
Fubo Retention Email Demo API
Simple FastAPI app that uses WatsonX LLM to generate personalized retention emails
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Fubo Retention Email API",
    description="AI-powered retention email system using WatsonX LLM",
    version="1.0.0"
)

# API Configuration (same as your existing tools)
BASE_URL = "https://watsonx-chat.20pttk3h2ear.us-south.codeengine.appdomain.cloud/"
OWNER_USER_ID = "8J5526897"
OWNER_USER_EMAIL = "matt.acosta@ibm.com"

# Load from environment variables
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_izPKbjMp_9aU3pk4LQYJoauQGFDnpgivF")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# Response Models
class EmailResult(BaseModel):
    user_email: str
    user_name: str
    status: str
    email_id: Optional[str] = None
    email_preview: str

class BatchEmailResponse(BaseModel):
    total_users: int
    total_sent: int
    results: List[EmailResult]


def get_users() -> List[dict]:
    """Get all users from same API as get_user.py"""
    try:
        response = requests.get(
            f"{BASE_URL}api/playground/custom-tools/user",
            params={"userId": OWNER_USER_ID, "email": OWNER_USER_EMAIL},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


def get_shows() -> List[dict]:
    """Get all shows from same API as get_shows.py"""
    try:
        response = requests.get(
            f"{BASE_URL}api/playground/custom-tools/shows",
            params={"userId": OWNER_USER_ID, "email": OWNER_USER_EMAIL},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch shows: {str(e)}")


def watsonx_llm(prompt: str) -> str:
    """Generate email content using WatsonX LLM"""
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        raise HTTPException(
            status_code=500,
            detail="WatsonX credentials not configured. Set WATSONX_API_KEY and WATSONX_PROJECT_ID"
        )
    
    try:
        print(f"[DEBUG] Prompt length: {len(prompt)} characters")
        print(f"[DEBUG] Prompt preview: {prompt[:500]}...")
        
        # Try meta-llama/llama-3-1-70b-instruct which is better for content generation
        model = Model(
            model_id="ibm/granite-4-h-small",
            params={
                GenParams.MAX_NEW_TOKENS: 1000,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_P: 0.9,
                GenParams.STOP_SEQUENCES: ["</html>"]
            },
            credentials={
                "apikey": WATSONX_API_KEY,
                "url": WATSONX_URL
            },
            project_id=WATSONX_PROJECT_ID
        )
        
        response = model.generate_text(prompt=prompt)
        print(f"[DEBUG] WatsonX Response Type: {type(response)}")
        print(f"[DEBUG] WatsonX Response Length: {len(response) if response else 0}")
        print(f"[DEBUG] WatsonX Response Preview: {response[:200] if response else 'EMPTY'}")
        
        if not response or not response.strip():
            raise HTTPException(status_code=500, detail="WatsonX returned empty response")
        
        return response
    except Exception as e:
        print(f"[ERROR] WatsonX LLM error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WatsonX LLM error: {str(e)}")


def generate_personalized_email(user: dict, shows: list) -> str:
    """Use WatsonX to generate personalized HTML email"""
    
    # Build context from user data - handle both string and list types
    user_name = user.get('name', 'Valued Customer')
    favorite_teams = user.get('favorite_teams', '')
    favorite_sports = user.get('favorite_sports', '')
    watch_time = user.get('average_daily_watch_time_hours', '0')
    plan = user.get('user_plan', 'Standard')
    
    # Build shows context (top 5 shows) - use correct field names from API
    shows_list = '\n'.join([
        f"- {s.get('show_name', 'Unknown')} on {s.get('channel_name', 'Fubo')}"
        for s in shows[:5]
    ])
    
    # Simplified prompt
    prompt = f"""Write a personalized retention email for Fubo customer {user_name}.

Customer Details:
- Favorite Teams: {favorite_teams}
- Favorite Sports: {favorite_sports}
- Watch Time: {watch_time} hours/day
- Plan: {plan}

Recommended Shows:
{shows_list}

Write an HTML email that:
1. Greets {user_name} personally
2. Mentions their favorite teams: {favorite_teams}
3. Recommends 2-3 shows from the list
4. Uses HTML tags: <html>, <body>, <p>, <h3>, <ul>, <li>
5. Ends with "Best regards, The Fubo Team"

HTML Email:"""

    html_email = watsonx_llm(prompt)
    
    # Ensure HTML wrapper if LLM didn't include it
    if not html_email.strip().startswith('<html>'):
        html_email = f"<html><body>{html_email}</body></html>"
    
    return html_email


def send_email(to_email: str, subject: str, html_message: str) -> dict:
    """Send email using Resend API (same as send_email.py)"""
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            json={
                "from": "noreply@sunheart.tech",
                "to": [to_email],
                "subject": subject,
                "html": html_message
            },
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

#making major changes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fubo Retention Email API",
        "endpoints": {
            "health": "/health",
            "send_batch": "POST /send-retention-emails",
            "send_single": "POST /send-single-email/{user_id}"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "watsonx_configured": bool(WATSONX_API_KEY and WATSONX_PROJECT_ID),
        "resend_configured": bool(RESEND_API_KEY)
    }


@app.post("/send-retention-emails", response_model=BatchEmailResponse)
async def send_retention_emails():
    """
    Main workflow endpoint:
    1. Get all users from API
    2. Get all shows from API
    3. For each user: Generate personalized email with WatsonX LLM
    4. Send email via Resend API
    
    Returns summary of sent emails
    """
    # Step 1: Get users
    users = get_users()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    
    # Step 2: Get shows
    shows = get_shows()
    if not shows:
        raise HTTPException(status_code=404, detail="No shows found")
    
    results = []
    
    # Step 3 & 4: Generate and send emails for each user
    for user in users:
        try:
            # Generate AI-powered personalized email
            email_html = generate_personalized_email(user, shows)
            
            # Create dynamic subject line
            user_name = user.get('name', 'Valued Customer')
            subject = f"New Content Just for You, {user_name}!"
            
            # Send email
            send_result = send_email(user['email'], subject, email_html)
            
            results.append(EmailResult(
                user_email=user['email'],
                user_name=user_name,
                status="sent" if 'id' in send_result else "failed",
                email_id=send_result.get('id'),
                email_preview=email_html[:200] + "..."
            ))
        except Exception as e:
            results.append(EmailResult(
                user_email=user.get('email', 'unknown'),
                user_name=user.get('name', 'unknown'),
                status="error",
                email_preview=f"Error: {str(e)}"
            ))
    
    successful_sends = sum(1 for r in results if r.status == "sent")
    
    return BatchEmailResponse(
        total_users=len(users),
        total_sent=successful_sends,
        results=results
    )


@app.post("/send-single-email/{user_email}")
async def send_single_email(user_email: str):
    """
    Send retention email to a single user by email address
    Useful for testing or manual triggers
    """
    # Get all users and find the specific one by email
    users = get_users()
    user = next((u for u in users if u.get('email') == user_email), None)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_email} not found")
    
    # Get shows
    shows = get_shows()
    
    # Generate and send email
    email_html = generate_personalized_email(user, shows)
    user_name = user.get('name', 'Valued Customer')
    subject = f"New Content Just for You, {user_name}!"
    
    send_result = send_email(user['email'], subject, email_html)
    
    return {
        "user_email": user['email'],
        "user_name": user_name,
        "status": "sent" if 'id' in send_result else "failed",
        "email_id": send_result.get('id'),
        "email_content": email_html
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
