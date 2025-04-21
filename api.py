from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
import traceback

app = Flask(__name__, static_folder='static', template_folder='templates')

# ------------------- ROUTES for HTML Pages -------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')

@app.route('/mitigation')
def mitigation():
    return render_template('mitigation.html')

@app.route('/preparedness')
def preparedness():
    return render_template('preparedness.html')

# ---------------------- Dynamic Routes for Cards ----------------------
@app.route('/cards/<card_name>')
def card_page(card_name):
    try:
        # Load from htmlCards/ folder
        return render_template(f'htmlCards/{card_name}.html')
    except TemplateNotFound:
        return "Card page not found", 404

# ------------------- Model and API Logic -------------------

# Load model and encoders
# model = joblib.load('model/disaster_preparedness_xgb_model.pkl')
# label_encoder = joblib.load('model/label_encoder.pkl')
# model_features = joblib.load('model/model_features.pkl')

# Disaster data
all_disasters = [
    "Flood", "Earthquake", "Landslide", "Drought", "Severe Storm", 
    "Cyclone", "Heatwave", "Cold Wave", "Industrial Hazard"
]

states_and_uts = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", 
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

disaster_risk_map = {region: all_disasters for region in states_and_uts}

risk_tiers = {
    "High": ["Earthquake", "Cyclone", "Flood"],
    "Medium": ["Landslide", "Severe Storm", "Industrial Hazard"],
    "Low": ["Drought", "Heatwave", "Cold Wave"]
}

custom_checklists = {
    "Earthquake": [
        "Secured heavy furniture", "Learned how to turn off utilities", "Emergency contact numbers known",
        "Prepared evacuation plan", "Kept shoes and flashlight beside bed", "First aid kit ready",
        "Important documents accessible", "Practiced earthquake drill", "Know nearest safe zone",
        "Know region's seismic history"
    ],
    "Flood": [
        "Know flood evacuation routes", "Have waterproof bags for documents", "First aid kit ready",
        "Food & water supplies", "Follow flood alerts", "Elevated electrical appliances",
        "Flood insurance taken", "Practiced flood drill", "Emergency contact numbers known",
        "Nearby shelters identified"
    ],
    "Cyclone": [
        "Reinforced windows and doors", "Tree branches trimmed", "Evacuation kit ready",
        "Important documents secured", "Battery-operated radio available", "Emergency contact numbers known",
        "Cyclone alerts followed", "Family trained on safety steps", "Mock drill done", "Water storage prepared"
    ],
    "Drought": [
        "Rainwater harvesting in place", "Water usage optimized", "Stored water for drinking",
        "Drip irrigation used", "Drought-resilient crops selected", "Emergency water plan",
        "Family informed of drought coping methods", "Local drought alerts followed",
        "Check wells and pumps", "Stored food"
    ],
    "Cold Wave": [
        "Warm clothing ready", "Heaters in safe condition", "Insulated home",
        "Emergency contact numbers known", "Backup heating source", "Food & water supplies",
        "Family trained for cold exposure", "Medical needs addressed", "Pets prepared", "Followed cold alerts"
    ],
    "Heatwave": [
        "Hydration plan followed", "Access to cool areas", "Avoided outdoor work during peak hours",
        "First aid for heatstroke known", "Family educated on symptoms", "Fans and AC functional",
        "Windows shaded", "Light cotton clothes used", "Followed heatwave alerts", "Mock drill conducted"
    ],
    "Landslide": [
        "Monitored slope signs", "Retaining walls checked", "Evacuation plan ready",
        "Emergency contact numbers known", "Drainage paths cleared", "Important items secured",
        "Followed weather updates", "Nearby shelters identified", "Practiced landslide drill",
        "Avoided unstable ground"
    ],
    "Severe Storm": [
        "Trimmed trees and shrubs", "Secured outdoor objects", "Emergency kit ready",
        "Listened to storm warnings", "Safe room identified", "Power backups ready",
        "Important papers waterproofed", "Mock drill done", "First aid kit ready", "Emergency contacts updated"
    ],
    "Industrial Hazard": [
        "Know local industry risks", "Toxic leak evacuation plan", "Gas masks and filters ready",
        "Government alerts followed", "Emergency contact numbers known", "Safe routes identified",
        "Community drill participated", "Important documents safe", "Family trained", "Nearby hospitals listed"
    ]
}

custom_recommendations = {
    "Earthquake": [
        "Secure your home structure with a professional inspection.",
        "Install seismic shut-off valves for gas lines.",
        "Join a local community earthquake awareness group."
    ],
    "Flood": [
        "Install water sensors in flood-prone areas.",
        "Keep sandbags ready for quick use.",
        "Subscribe to SMS flood alerts from local authorities."
    ],
    "Cyclone": [
        "Reinforce your home's roofing materials.",
        "Establish a cyclone-safe room in your home.",
        "Register for community cyclone warning updates."
    ],
    "Drought": [
        "Invest in a water-efficient irrigation system.",
        "Monitor local groundwater levels regularly.",
        "Collaborate with neighbors to manage water usage."
    ],
    "Cold Wave": [
        "Insulate plumbing to prevent freezing.",
        "Check on elderly neighbors during extreme cold.",
        "Register for cold wave alerts from the local government."
    ],
    "Heatwave": [
        "Create a cool room with blackout curtains and fans.",
        "Coordinate with neighbors for mutual aid during heat spikes.",
        "Join a local heatwave preparedness campaign."
    ],
    "Landslide": [
        "Install proper drainage systems around your home.",
        "Avoid heavy construction near slopes.",
        "Use vegetation to help stabilize soil."
    ],
    "Severe Storm": [
        "Anchor outdoor structures like sheds or swings.",
        "Get your roof inspected before storm season.",
        "Keep mobile phone power banks charged at all times."
    ],
    "Industrial Hazard": [
        "Attend safety training from local industries.",
        "Install indoor air quality sensors.",
        "Keep an emergency go-bag with safety gear and essentials."
    ]
}

def get_risk_tier(disaster_type):
    for tier, disasters in risk_tiers.items():
        if disaster_type in disasters:
            return {"High": 2, "Medium": 1, "Low": 0}[tier]
    return 1

def calculate_completion(checklist_responses):
    return sum(checklist_responses.values()) / len(checklist_responses) * 100

def get_improvement_tips(level):
    tips = {
        "Needs Urgent Prep": [
            "Complete all urgent checklist items immediately.",
            "Create an evacuation plan and share with family."
        ],
        "Moderately Prepared": [
            "Review missing checklist items.",
            "Conduct a disaster drill with household members."
        ],
        "Well Prepared": [
            "Stay updated with local disaster alerts.",
            "Refresh emergency supplies every 6 months."
        ]
    }
    return tips.get(level, [])

def get_recommendations(disaster_type, level):
    return custom_recommendations.get(disaster_type, [])

# ------------------- API ENDPOINTS -------------------

@app.route('/api/states', methods=['GET'])
def get_states():
    return jsonify({"states": list(disaster_risk_map.keys())})

@app.route('/api/disasters', methods=['GET'])
def get_disasters():
    state = request.args.get('state')
    if not state or state not in disaster_risk_map:
        return jsonify({"error": "Invalid state"}), 400
    return jsonify({"disasters": disaster_risk_map[state]})

@app.route('/api/checklist', methods=['GET'])
def get_checklist():
    disaster_type = request.args.get('disaster_type')
    if not disaster_type or disaster_type not in custom_checklists:
        return jsonify({"error": "Invalid disaster type"}), 400
    return jsonify({"checklist": custom_checklists[disaster_type]})

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("🔥 Received data:", data)

        # Check all required fields are present
        required_fields = ['state', 'disaster_type', 'household_size', 'has_kit', 'checklist_responses']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Load models
        model = joblib.load("model/disaster_preparedness_xgb_model.pkl")
        label_encoder = joblib.load("model/label_encoder.pkl")
        model_features = joblib.load("model/model_features.pkl")

        checklist_responses = data['checklist_responses']
        # ✅ Use the full checklist from user's form
        checklist_features = {
            key: int(value)
            for key, value in checklist_responses.items()
}

        print("✅ Checklist features:", checklist_features)

        try:
            encoded_state = label_encoder.transform([data['state']])[0]
            encoded_disaster = label_encoder.transform([data['disaster_type']])[0]
        except ValueError as ve:
            print("❌ Label encoding failed:", ve)
            return jsonify({"error": f"Encoding error: {str(ve)}"}), 400

        # ✅ Build input for the model based on expected features
        feature_dict = {}
        for feature in model_features:
            if feature == 'state':
                feature_dict['state'] = encoded_state
            elif feature == 'disaster_type':
                feature_dict['disaster_type'] = encoded_disaster
            elif feature == 'household_size':
                feature_dict['household_size'] = int(data['household_size'])
            elif feature == 'has_kit':
                feature_dict['has_kit'] = int(data['has_kit'])
            else:
                feature_dict[feature] = checklist_features.get(feature, 0)

        # print("📦 Final input for model:", feature_dict)

        final_input = pd.DataFrame([feature_dict], columns=model_features)

        prediction = model.predict(final_input)[0]
        preparedness_level = int(prediction)  # or decode if needed

        # ✅ Add this mapping
        level_labels = {
            0: "Needs Urgent Prep",
            1: "Moderately Prepared",
            2: "Well Prepared"
        }
        level_label = level_labels.get(preparedness_level, "Unknown")

        awareness_score = sum(checklist_features.values())
        completion_percentage = (awareness_score / len(checklist_features)) * 100 if checklist_features else 0


        return jsonify({
            "preparedness_level": level_label,
            "completion_percentage": completion_percentage,
            "awareness_score": awareness_score,
            "improvement_tips": get_improvement_tips(level_label),
            "recommendations": get_recommendations(data['disaster_type'], level_label)
})


    except Exception as e:
        import traceback
        traceback.print_exc()
        print("🔥 ERROR in /api/predict:", str(e))
        return jsonify({"error": str(e)}), 500


# ------------------- Run Server -------------------

if __name__ == '__main__':
    app.run(debug=True)
