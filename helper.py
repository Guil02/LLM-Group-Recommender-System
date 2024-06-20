import pickle

class Helper:
    def __init__(self) -> None:
        pass

    # Function to save data structure using pickle
    def save_data(self, data, filename):
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
        # print(f"Data has been saved to {filename}")

    # Function to load data structure using pickle
    def load_data(self, filename):
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        # print(f"Data has been loaded from {filename}")
        return data