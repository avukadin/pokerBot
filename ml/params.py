saved_model_path = "./data/saved_models"
train_data_path = "./data/train_data"

# Preprocessing
PROCESSED_DATA_PATH = f"{train_data_path}/hands_processed.json"
VALID_HANDS_PATH = f"{train_data_path}/hands_valid.json"

# Training Data
HS_TRAIN_DATA_PATH = f"{train_data_path}/hand_prediction.pickle"
MOVE_TRAIN_DATA_PATH = f"{train_data_path}/move_prediction.pickle"

# Training Params
MAX_SAMPLES = 1000000 # Max training samples
MOVE_HISTORY = 20 # Number of past moves to include as model features
BATCH_SIZE = 32
EPOCHS = 10
HS_MODEL_PATH = f"{saved_model_path}/hand_strength_model.h5"
MOVE_MODEL_PATH = f"{saved_model_path}/move_model.h5"
HS_SAMPLE_PREDICTION_PATH = f"{train_data_path}/hand_strength_sample_predictions.csv" # Sample predictions on the validation data
MOVE_SAMPLE_PREDICTION_PATH = f"{train_data_path}/move_sample_predictions.csv" # Sample predictions on the validation data
