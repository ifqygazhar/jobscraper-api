![poster](/image/poster.webp "poster")

# Job Scraper

This project is a job scraper designed to gather job listings from various sources. It is structured in Python and organized to maintain separation of concerns between configuration, business logic, helpers, routing, and singleton instances.

## Python

```
Python >= 3.10.6
```

## Install depedencies

```
pip install -r requirements.txt
```

## Structure Project

```
Root
│   .gitignore
│   main.py
│   README.md
│   requirements.txt
│
└───app
    │   __init__.py
    │
    ├───config
    │       sample_cookie.json
    │
    ├───controllers
    │   | scrape_glints.py
    │
    ├───helpers
    │   |  cookie_helper.py
    │   │ response.py
    │
    ├───routes
    │   │   route.py
    │
    ├───singletons
    │   │   cloudscraper.py
    │
    └───__pycache__
            __init__.cpython-310.pyc
```

### Docs Swagger

You can access the API documentation at `http://0.0.0.0:8000/docs/`

### Root

The root directory contains the main project files:

- main.py: Entry point of the application.
- README.md: Documentation file (this file).
- requirements.txt: Python dependencies for the project.

### App

The `app` folder contains all core modules and logic for the project, divided into the following subdirectories:

#### **config**

Contains configuration files:

- `sample_cookie.json`: Stores cookies in JSON format. You can export cookies using the [Cookie Editor](https://cookie-editor.cgagnier.ca/) browser extension.

#### **controllers**

Holds business logic for the application:

- `scrape_glints.py`: Logic for scraping job data from Glints.

#### **helpers**

Utility functions to be reused across the project:

- `cookie_helper.py`: Helps manage cookies.
- `response.py`: Handles standardized responses.

#### **routes**

Defines API routes and links them to their corresponding logic:

- `route.py`: Route for triggering Controller scraping logic.

#### **singletons**

Stores singleton instances for libraries:

- `cloudscraper.py`: Singleton for managing Cloudscraper instances.

---

## Usage

1. Run the application:

   ```bash
   python main.py
   ```

2. The application will expose endpoints defined in the `routes` folder.

Example : `GET http://0.0.0.0:8000/api/jobstreet?work=flutter`

3. Documentation About Endpoint Soon After All Done !

---

## Contributing

Feel free to fork this repository and contribute enhancements or bug fixes through pull requests.

---

## License

This project is licensed under the [MIT License](LICENSE).
