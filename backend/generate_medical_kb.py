import json
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

KB_DIR = os.path.join(BASE_DIR, "knowledge_base")

os.makedirs(KB_DIR, exist_ok=True)

diseases = {
    "Hypertension": {
        "symptoms": ["Headache", "Dizziness", "Blurred vision"],
        "treatments": ["ACE inhibitors", "ARBs", "Lifestyle modification"],
        "tests": ["Blood Pressure Measurement"]
    },
    "Diabetes Mellitus": {
        "symptoms": ["Frequent urination", "Excessive thirst", "Fatigue"],
        "treatments": ["Metformin", "Insulin", "Diet control"],
        "tests": ["HbA1c", "Fasting Blood Sugar"]
    },
    "Asthma": {
        "symptoms": ["Shortness of breath", "Wheezing", "Cough"],
        "treatments": ["Salbutamol", "Inhaled corticosteroids"],
        "tests": ["Spirometry"]
    },
    "Pneumonia": {
        "symptoms": ["Fever", "Chest pain", "Productive cough"],
        "treatments": ["Antibiotics", "Supportive care"],
        "tests": ["Chest X-Ray", "CBC"]
    },
    "Migraine": {
        "symptoms": ["Headache", "Nausea", "Photophobia"],
        "treatments": ["NSAIDs", "Triptans"],
        "tests": []
    },
    "Stroke": {
        "symptoms": ["Weakness", "Speech difficulty", "Facial drooping"],
        "treatments": ["Thrombolysis", "Mechanical thrombectomy"],
        "tests": ["CT Brain", "MRI Brain"]
    },
    "Heart Failure": {
        "symptoms": ["Shortness of breath", "Leg swelling", "Fatigue"],
        "treatments": ["Diuretics", "ACE inhibitors"],
        "tests": ["Echocardiogram"]
    },
    "COVID-19": {
        "symptoms": ["Fever", "Cough", "Loss of smell"],
        "treatments": ["Supportive care", "Antivirals"],
        "tests": ["RT-PCR"]
    },
    "Tuberculosis": {
        "symptoms": ["Weight loss", "Night sweats", "Chronic cough"],
        "treatments": ["Isoniazid", "Rifampicin"],
        "tests": ["Sputum AFB", "Chest X-Ray"]
    },
    "Anemia": {
        "symptoms": ["Fatigue", "Pallor", "Weakness"],
        "treatments": ["Iron supplements"],
        "tests": ["CBC"]
    }
}

medications = [
    "Metformin",
    "Insulin",
    "Paracetamol",
    "Ibuprofen",
    "Aspirin",
    "Salbutamol",
    "ACE inhibitors",
    "ARBs",
    "Amoxicillin",
    "Azithromycin",
    "Atorvastatin",
    "Omeprazole",
    "Isoniazid",
    "Rifampicin",
    "Furosemide"
]

symptoms = [
    "Fever",
    "Headache",
    "Cough",
    "Chest pain",
    "Fatigue",
    "Nausea",
    "Vomiting",
    "Dizziness",
    "Shortness of breath",
    "Weight loss",
    "Blurred vision",
    "Weakness",
    "Night sweats",
    "Pallor",
    "Loss of smell"
]

procedures = [
    "ECG",
    "CT Scan",
    "MRI",
    "Blood Pressure Measurement",
    "Chest X-Ray",
    "Spirometry",
    "Mechanical thrombectomy",
    "Thrombolysis",
    "Ultrasound"
]

laboratory_tests = [
    "CBC",
    "HbA1c",
    "RT-PCR",
    "Fasting Blood Sugar",
    "Liver Function Test",
    "Kidney Function Test",
    "Troponin",
    "CRP",
    "ESR",
    "Sputum AFB"
]

files = {
    "diseases.json": diseases,
    "medications.json": medications,
    "symptoms.json": symptoms,
    "procedures.json": procedures,
    "laboratory_tests.json": laboratory_tests
}

for filename, content in files.items():

    with open(
        os.path.join(KB_DIR, filename),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            content,
            f,
            indent=4
        )

print("=" * 60)
print("MEDICAL KNOWLEDGE BASE GENERATED")
print("=" * 60)

for filename in files:
    print("✓", filename)