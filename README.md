# Lab Results & Diagnostic Report IVR — Modernization Framework

A conversational IVR framework to deliver lab results and diagnostic reports via voice and messaging. This repository contains the backend components, documentation, and example configuration used in the Lab Results & Diagnostic Report IVR project.

## Quick summary
- Natural-language phone interaction to authenticate callers and summarize lab results.
- Optional delivery of full reports via SMS/WhatsApp or email.
- Built with Python, FastAPI, Twilio (voice/SMS), and Postgres-compatible storage (Supabase).

## Quickstart
1. Clone the repository:

```powershell
git clone git@github.com:1209nikhil/Lab-Results-Diagnostic-Report-IVR--G1-Modernization-IVR-Framework-.git
cd Lab-IVR
```

2. Install backend dependencies:

```powershell
pip install -r "Backend IVR/requirements.txt"
```

3. Configure environment variables:
- Copy `Lab-IVR/Backend IVR/.env.example` → `Lab-IVR/Backend IVR/.env` and set your Twilio and Supabase credentials.

4. Run the backend (example):

```powershell
cd "Lab-IVR/Backend IVR"
uvicorn backend_ivr:app --reload --port 8000
# or use your preferred method (docker/ngrok/etc.)
```

5. Expose the webhook to Twilio (ngrok) and configure your Twilio phone number to use the `/voice` webhook.

## Structure
- `Lab-IVR/Backend IVR/` — backend code, requirements, and configuration examples.
- `Lab-IVR/` — documentation and assets, including the license.

## Contributing
Feel free to open issues or PRs. If you plan to modify the IVR flow or add integrations, include tests or a short runbook explaining the changes.

## License
This project is provided under the MIT License — see `LICENSE` for details.

---

Built with ❤️ to make healthcare better.
