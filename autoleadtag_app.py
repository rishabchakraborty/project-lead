from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

contacts = []
tagging_rules = {
    "default": [
        {"type": "domain", "match": "gmail.com", "tag": "Personal"},
        {"type": "job_title", "match": "founder", "tag": "Founder"},
        {"type": "job_title", "match": "intern", "tag": "Low Priority"},
    ]
}

@app.post("/webhook/contact_created")
async def webhook_contact_created(request: Request):
    body = await request.json()
    contact = body.get("contact", {})
    email = contact.get("email", "").lower()
    job_title = contact.get("job_title", "").lower()
    
    assigned_tags = []
    for rule in tagging_rules["default"]:
        if rule["type"] == "domain" and rule["match"] in email:
            assigned_tags.append(rule["tag"])
        if rule["type"] == "job_title" and rule["match"] in job_title:
            assigned_tags.append(rule["tag"])
    
    tagged_contact = {
        "email": email,
        "job_title": job_title,
        "tags": list(set(assigned_tags))
    }
    contacts.append(tagged_contact)
    
    return JSONResponse({"status": "success", "tagged": tagged_contact})

@app.get("/dashboard/contacts")
def get_contacts():
    return {"contacts": contacts}

@app.get("/dashboard/rules")
def get_rules():
    return {"rules": tagging_rules["default"]}

@app.post("/dashboard/rules")
async def add_rule(request: Request):
    data = await request.json()
    tagging_rules["default"].append(data)
    return {"status": "rule added", "rule": data}
