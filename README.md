# Deaglo API Gateway

## Getting Started

Follow these instructions to set up and configure the project on your local machine.

### Setting Up the Virtual Environment

1. Create a virtual environment with Python 3.11.6:

    ```bash
    virtualenv venv -p python3.11
    ```

2. Activate the virtual environment:

    - **On Windows:**

        ```bat
        .\venv\Scripts\activate
        ```

    - **On macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

        OR

        ```bash
        . venv/bin/activate
        ```

### Installing Dependencies

Install project dependencies from `requirements.txt` using pip:

```bash
pip install -r requirements.txt
```

### Linting

```bash
# check all files and fix automatically
black .

# log every checked file
black . --verbose
```

### Environment Variables

To set up an environment for development:

1. Copy `.env.example` and rename it to `.env`
2. Replace default values as needed
