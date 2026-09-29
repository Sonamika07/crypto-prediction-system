from backend.app.services.prediction_service import get_latest_prediction


result = get_latest_prediction()

print("LATEST PREDICTION")
print(result)