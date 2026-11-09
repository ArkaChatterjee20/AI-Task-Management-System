import pickle


def main():

    with open("tfidf.pkl", "rb") as file:
        vectorizer = pickle.load(file)

    print("Vectorizer type:", type(vectorizer))
    print("Number of features:", len(vectorizer.get_feature_names_out()))

    sample_text = [
        "complete the machine learning project"
    ]

    transformed = vectorizer.transform(sample_text)

    print("Transformed shape:", transformed.shape)


if __name__ == "__main__":
    main()