# WebScraper-W2A

## Overview
WebScraper-W2A is a web scraping tool for efficiently extracting data from websites. It is built with Python and uses libraries such as Scrapy and BeautifulSoup for data extraction. The tool also includes a Flask-based frontend for managing scraping tasks and viewing results.

WebScraper-W2A starts with an initial URL and recursively follows links within the website. The initial page serves as context for comparing subsequent pages, allowing the tool to filter out common elements and focus on relevant content. The scraped data, including attachments, is stored in a PostgreSQL database. The scraper also runs scheduled jobs to keep data up to date by updating previously scraped pages if changes are detected.

The application is containerized with Docker and orchestrated using Docker Compose for easy deployment and scalability.

## Features
- Recursively extracts data from websites
- Context-based data comparison to filter out common and irrelevant parts
- Stores scraped content, including attachments, in a PostgreSQL database
- Scheduled scraping jobs ensuring that data is up-to-date
- Interactive frontend for managing scraping tasks and browsing database.

## Installation and Usage
The tool runs in Docker using Docker Compose.

### Development

Ensure Docker Engine is up and running. To launch the tool in development mode:

1) Clone the repository:
```
git clone https://github.com/Web2AI/WebScraper-W2A.git
```
2) Enter the repository:
```
cd WebScraper-W2A
```
3) Build the Docker images:
```
docker compose -f docker-compose.dev.yml build
```
4) Run the application:
```
docker compose -f docker-compose.dev.yml up
```
\
To access the database run (ensure the container is running):
```
docker exec -it webscraper-w2a-db-1 psql -U postgres -d scraperdb
```

### Production
Use the `docker-compose.yml` file instead of `docker-compose.dev.yml`. 

Make sure to adjust the `.env` variables locally as required.

## CI checks
The project uses GitHub Actions for continuous integration to ensure code quality. The following checks are run automatically on each push:
- Black: Checks Python code formatting.
- Mypy: Runs type checks on the codebase.
- isort: Verifies that imports are sorted.
- Bandit: Scans for security vulnerabilities.

To run those checks locally run: (`python -m`)

- `black --check .` 
- `isort --check-only --profile black .` 
- `mypy .`
- `bandit -r .` 

To format files locally run: (`python -m`)
- `black .`
- `isort --profile black .`

Make sure that corresponding libraries are installed (use `python -m pip install [lib]`, see *requirements.txt*).

## Repository structure
The repository is organized as follows:
```
WebScraper-W2A/
│
├── .github/                        # GitHub configuration files
├── .trunk/                         # Trunk-related configuration
├── ai-description-service/         # AI description service for generating image descriptions
├── out/                            # Output directory for scraped data
├── src/                            # Source code directory
│   ├── jobs/                       # Scheduled jobs for scraping
│   ├── scraper/                    # Scraper-related modules
│   ├── static/                     # Static files for the Flask frontend
│   ├── templates/                  # HTML templates for the Flask frontend
│   ├── __init__.py                 # Application initialization
│   ├── app.py                      # Main Flask application
│   ├── constants.py                # Application constants
│   ├── log_utils.py                # Logging configuration
│   ├── models.py                   # Database models
│   ├── routes.py                   # Flask routes
│   └── scheduled_jobs_config.py    # Configuration for scheduled jobs
├── .dockerignore                   # Docker ignore file
├── .env                            # Environment variables for production
├── .env.dev                        # Environment variables for development
├── .gitignore                      # Git ignore file
├── docker-compose.dev.yml          # Docker Compose configuration for development
├── docker-compose.yml              # Docker Compose configuration for production
├── Dockerfile                      # Dockerfile for production
├── Dockerfile.dev                  # Dockerfile for development
├── LICENSE                         # License file (Apache 2.0)
├── README.md                       # Project README
├── requirements.txt                # Python dependencies
└── setup.cfg                       # Configuration for setup tools
```

## Testing
A dedicated set of static HTML files designed specifically for testing purposes is available at https://github.com/Web2AI/test-site.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the [Apache 2.0](LICENSE) License.