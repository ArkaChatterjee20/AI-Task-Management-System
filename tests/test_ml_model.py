import pickle


def inspect_model(file_name):

    print(f"\nInspecting: {file_name}")

    with open(file_name, "rb") as file:
        model = pickle.load(file)

    print("Type:", type(model))

    if hasattr(model, "classes_"):
        print("Classes:", model.classes_)

    if hasattr(model, "n_features_in_"):
        print(
            "Expected features:",
            model.n_features_in_
        )


def main():

    files = [
        "final_model.pkl",
        "model.pkl",
        "nb_model.pkl",
        "svm_model.pkl",
        "task_model.pkl",
        "tfidf.pkl",
    ]

    for file_name in files:

        try:
            inspect_model(file_name)

        except Exception as error:

            print(
                f"Could not load {file_name}: {error}"
            )


if __name__ == "__main__":
    main()