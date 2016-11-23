import threading, subprocess, os, time
from app import app
from app import scrape_4_dead_links
from subprocess import call

execute_checks = scrape_4_dead_links.run_check() 

app.run( 
        host="0.0.0.0",
        port=int("8000")
)
