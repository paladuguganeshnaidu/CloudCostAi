from src.data.loader import load_dataset
from src.data.preprocessing import preprocess_dataset
from src.model.predict import predict_cost


def main():

    df = load_dataset("data/raw/gcp_final_approved_dataset.csv")

    df = preprocess_dataset(df)

    sample = df.iloc[[0]].copy()

    actual_cost = sample["Total Cost (INR)"].iloc[0]

    prediction = predict_cost(sample)

    print("\nPrediction Test\n")

    print(f"Actual Cost    : ₹{actual_cost:,.2f}")

    print(f"Predicted Cost : ₹{prediction[0]:,.2f}")

    print(f"Difference     : ₹{abs(actual_cost - prediction[0]):,.2f}")


if __name__ == "__main__":
    main()