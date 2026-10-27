REALMAX GetKey Free Fire (demo)

Files:
- app.py
- templates/index.html
- requirements.txt
- Procfile
- render.yaml

Deploy to Render:
1. Upload these files to a GitHub repository, keeping templates/index.html in the templates folder.
2. Create a new Web Service in Render connected to that repository.
3. Build Command: pip install -r requirements.txt
4. Start Command: gunicorn app:app
5. Deploy.

Endpoints:
- GET  /            Web page
- GET  /health       Health check
- POST /api/getkey   Create a key (24 hours by default)
- POST /api/verify   Verify a key; JSON body: {"key":"REAL-XXXX-XXXX-XXXX"}

IMPORTANT:
This demo uses SQLite. On Render, the local filesystem may be ephemeral and the database may reset on redeploy/restart. For persistent production use, migrate to PostgreSQL and use a persistent database connection.
This is a standalone license-key demo and is not affiliated with Garena or Free Fire.
