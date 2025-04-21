# rebuild_label_encoder.py
import joblib
from sklearn.preprocessing import LabelEncoder

# Full list of states and disaster types
states = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

disasters = [
    "Flood", "Earthquake", "Landslide", "Drought", "Severe Storm",
    "Cyclone", "Heatwave", "Cold Wave", "Industrial Hazard"
]

# Combine them all
all_labels = states + disasters

# Train the encoder
encoder = LabelEncoder()
encoder.fit(all_labels)

# Save to model folder (overwrite old one)
joblib.dump(encoder, "model/label_encoder.pkl")
print("✅ label_encoder.pkl updated and saved.")
