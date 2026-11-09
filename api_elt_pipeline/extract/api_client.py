import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://jsonplaceholder.typicode.com"


def create_session():
    """
    Create an HTTP session with retry capability.
    """

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def get_todos():
    """
    Fetch todo/task data from the JSONPlaceholder API.
    """

    url = f"{BASE_URL}/todos"

    session = create_session()

    try:
        logging.info("Requesting data from: %s", url)

        response = session.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        logging.info(
            "API request successful. Status code: %s",
            response.status_code,
        )

        return response.json()

    except requests.exceptions.Timeout:
        logging.error("API request timed out.")
        raise

    except requests.exceptions.HTTPError as error:
        logging.error(
            "HTTP error occurred: %s",
            error,
        )
        raise

    except requests.exceptions.RequestException as error:
        logging.error(
            "API request failed: %s",
            error,
        )
        raise

    finally:
        session.close()