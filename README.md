# Scraper Service

## Overview

The Scraper Service is a crucial component of our healthcare microservices architecture, designed to fetch and parse drug details. Built with Python, this service provides robust web scraping capabilities for medication information lookup. This service will use requests module as well as asyncio and aiohttp modules for faster scraping. 

## Features

- Fetch drug details from pulically available resources
- Parse HTML content to extract useful information
- Caching mechanism for improved performance
- Dockerized for easy deployment and scaling

## Tech Stack

- Python
- AIOHTTP, Asyncio
- Docker

## Project Structure

scraper-service/
│── src/
│ ├── scraper.py
│ ├── utils/
│ │ ├── cache.py
│── .github/workflows/
│── Dockerfile
│── requirements.txt
│── README.md
text

## Setup and Installation

1. Clone the repository:
git clone https://github.com/Maverics-Seneca/scraper-service.git
text

2. Install dependencies:
cd scraper-service
pip install -r requirements.txt
text

3. Run the scraper:
python src/scraper.py
text

## Docker

To build and run the service using Docker:

docker build -t scraper-service .
docker run scraper-service
text

## CI/CD

This project uses GitHub Actions for continuous integration and deployment. The workflow is defined in `.github/workflows/ci-cd.yml`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
