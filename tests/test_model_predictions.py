import pickle


def load_pickle(file_name):
    with open(file_name, "rb") as file:
        return pickle.load(file)


def main():

    # Load the TF-IDF vectorizer
    vectorizer = load_pickle("tfidf.pkl")

    # Load the three compatible models
    random_forest = load_pickle("model.pkl")
    naive_bayes = load_pickle("nb_model.pkl")
    svm = load_pickle("svm_model.pkl")

    # Sample task titles
    tasks = [
        "complete the machine learning project",
        "buy groceries from the market",
        "prepare presentation for tomorrow",
        "call the customer",
    ]

    # Convert text into TF-IDF features
    features = vectorizer.transform(tasks)

    print("Feature shape:", features.shape)

    # Generate predictions
    print("\nRandom Forest Predictions:")
    print(random_forest.predict(features))

    print("\nNaive Bayes Predictions:")
    print(naive_bayes.predict(features))

    print("\nSVM Predictions:")
    print(svm.predict(features))


if __name__ == "__main__":
    main()