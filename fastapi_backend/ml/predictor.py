
import pickle
import re
from pathlib import Path
from functools import lru_cache

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


BASE_DIR = Path(__file__).resolve().parents[2]

VECTORIZER_PATH = BASE_DIR / "tfidf.pkl"
MODEL_PATH = BASE_DIR / "svm_model.pkl"

stop_words = set(stopwords.words("english"))


def preprocess_text(text):

    text = str(text).lower()

    text = re.sub(
        r"[^a-zA-Z]",
        " ",
        text,
    )

    tokens = word_tokenize(text)

    tokens = [
        word
        for word in tokens
        if word not in stop_words
    ]

    return " ".join(tokens)


@lru_cache(maxsize=1)
def load_ml_components():

    with open(VECTORIZER_PATH, "rb") as file:
        vectorizer = pickle.load(file)

    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    return vectorizer, model



def predict_tasks_in_batches(tasks, batch_size=1000):
    """
    Generate predictions incrementally.

    Accepts either:
    1. A list of task dictionaries.
    2. An iterable of task dictionaries.
    3. An iterable of task batches.

    Yields one list of predictions per batch.
    """

    if (
        not isinstance(batch_size, int)
        or isinstance(batch_size, bool)
        or batch_size <= 0
    ):
        raise ValueError("batch_size must be a positive integer.")

    vectorizer, model = load_ml_components()

    def process_batch(batch):
        task_titles = [
            preprocess_text(task["task_title"])
            for task in batch
        ]

        features = vectorizer.transform(task_titles)
        predictions = model.predict(features)

        results = []

        for task, prediction in zip(batch, predictions):
            prediction_value = int(prediction)

            prediction_label = (
                "Done"
                if prediction_value == 1
                else "Not Done"
            )

            results.append({
                "task_id": task["task_id"],
                "task_title": task["task_title"],
                "prediction": prediction_value,
                "predicted_status": prediction_label,
            })

        return results

    pending = []

    for item in tasks:
        # Support both individual records and batches.
        if isinstance(item, dict):
            incoming = [item]
        elif isinstance(item, (list, tuple)):
            incoming = item
        else:
            raise ValueError("Invalid task or task batch.")

        for task in incoming:
            if not isinstance(task, dict):
                raise ValueError("Invalid task record.")

            pending.append(task)

            if len(pending) == batch_size:
                yield process_batch(pending)
                pending = []

    if pending:
        yield process_batch(pending)

def predict_tasks(tasks):
    """
    Preserve the existing interface and return format.
    """

    return [
        prediction
        for batch in predict_tasks_in_batches(tasks)
        for prediction in batch
    ]
