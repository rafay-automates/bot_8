from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re
import uvicorn


app = FastAPI(title="Domain Info API")

# Allow frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------- Helper Functions -----------------
def clean_domain(domain: str) -> str:
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = re.sub(r"^www\.", "", domain)
    domain = domain.split("/")[0]
    return domain


def get_csrf_token(session):
    home = session.get("https://linkdetective.pro/")
    soup = BeautifulSoup(home.text, "html.parser")
    token_input = soup.find("input", {"name": "_token"})
    if token_input:
        return token_input["value"]
    return session.cookies.get("XSRF-TOKEN")


def fetch_domain_data(session, csrf_token, domain_name):
    payload = {
        "draw": 5,
        "start": 0,
        "length": 50,
        "_token": csrf_token,
        "domains[]": domain_name,
        "buttons": "true"
    }
    resp = session.post("https://linkdetective.pro/api/domains", data=payload)
    if resp.status_code == 419 or "invalid" in resp.text.lower():
        csrf_token = get_csrf_token(session)
        payload["_token"] = csrf_token
        resp = session.post("https://linkdetective.pro/api/domains", data=payload)
    try:
        return resp.json()
    except ValueError:
        return None


# ----------------- API Route -----------------
@app.get("/fetch")
def fetch_domain(domain: str = Query(..., description="Domain name to fetch")):
    domain = clean_domain(domain)
    session = requests.Session()
    csrf_token = get_csrf_token(session)
    data = fetch_domain_data(session, csrf_token, domain)
    if not data:
        return {"error": "Failed to fetch data."}

    # Format response
    domain_stats = []
    for row in data.get("data", []):
        domain_stats.append({
            "Domain": row.get("Domain"),
            "Price": row.get("Price"),
            "DR": row.get("DR"),
            "RefDomains": row.get("RefDomains"),
            "Backlinks": row.get("Backlinks"),
            "Traffic": row.get("Traffic"),
            "Country": row.get("Country"),
        })

    reseller_list = []
    sellers_by_domain = data.get("sellers", [])
    domain_info = [row.get("Domain") for row in data.get("data", [])]
    for i, sellers in enumerate(sellers_by_domain):
        dom = domain_info[i] if i < len(domain_info) else domain
        for s in sellers:
            reseller_list.append({
                "Domain": dom,
                "Contact": s.get("contacts"),
                "Price": f"${s.get('price')}",
                "Date": s.get("date")
            })

    return {"domain_stats": domain_stats, "resellers": reseller_list}
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re
import uvicorn

app = FastAPI(title="Domain Info API")

# Allow frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------- Helper Functions -----------------
def clean_domain(domain: str) -> str:
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = re.sub(r"^www\.", "", domain)
    domain = domain.split("/")[0]
    return domain


def get_csrf_token(session):
    home = session.get("https://linkdetective.pro/")
    soup = BeautifulSoup(home.text, "html.parser")
    token_input = soup.find("input", {"name": "_token"})
    if token_input:
        return token_input["value"]
    return session.cookies.get("XSRF-TOKEN")


def fetch_domain_data(session, csrf_token, domain_name):
    payload = {
        "draw": 5,
        "start": 0,
        "length": 50,
        "_token": csrf_token,
        "domains[]": domain_name,
        "buttons": "true"
    }
    resp = session.post("https://linkdetective.pro/api/domains", data=payload)
    if resp.status_code == 419 or "invalid" in resp.text.lower():
        csrf_token = get_csrf_token(session)
        payload["_token"] = csrf_token
        resp = session.post("https://linkdetective.pro/api/domains", data=payload)
    try:
        return resp.json()
    except ValueError:
        return None


# ----------------- API Route -----------------
@app.get("/fetch")
def fetch_domain(domain: str = Query(..., description="Domain name to fetch")):
    domain = clean_domain(domain)
    session = requests.Session()
    csrf_token = get_csrf_token(session)
    data = fetch_domain_data(session, csrf_token, domain)
    if not data:
        return {"error": "Failed to fetch data."}

    # Format response
    domain_stats = []
    for row in data.get("data", []):
        domain_stats.append({
            "Domain": row.get("Domain"),
            "Price": row.get("Price"),
            "DR": row.get("DR"),
            "RefDomains": row.get("RefDomains"),
            "Backlinks": row.get("Backlinks"),
            "Traffic": row.get("Traffic"),
            "Country": row.get("Country"),
        })

    reseller_list = []
    sellers_by_domain = data.get("sellers", [])
    domain_info = [row.get("Domain") for row in data.get("data", [])]
    for i, sellers in enumerate(sellers_by_domain):
        dom = domain_info[i] if i < len(domain_info) else domain
        for s in sellers:
            reseller_list.append({
                "Domain": dom,
                "Contact": s.get("contacts"),
                "Price": f"${s.get('price')}",
                "Date": s.get("date")
            })

    return {"domain_stats": domain_stats, "resellers": reseller_list}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
