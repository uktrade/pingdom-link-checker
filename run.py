import os
from app import app
from app import scrape_4_dead_links

execute_checks = scrape_4_dead_links.run_check()
port = int(os.environ.get("PORT", 5000))
app.run(
        host="0.0.0.0",
        port=port
)
