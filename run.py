from app import app
from app import scrape_4_dead_links

execute_checks = scrape_4_dead_links.run_check() 

app.run( 
        host="0.0.0.0",
        port=int("80")
)
