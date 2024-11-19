JOBS = [
    {
        "id": "scrape_pcss",
        "func": "jobs.call_scrape_endpoint:call_scrape_endpoint",
        "args": (["https://www.pcss.pl/"]),
        "trigger": "cron",
        "minute": 0,
        "second": 0,
        "replace_existing": True,
    },
]
