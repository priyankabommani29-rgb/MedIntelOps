import json
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

KB_DIR = os.path.join(
    BASE_DIR,
    "knowledge_base"
)


def save(name, data):

    with open(
        os.path.join(KB_DIR, name),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


# =====================================================
# DISEASES
# =====================================================

diseases = {

"Hypertension":{
"symptoms":["Headache","Dizziness","Blurred vision"],
"treatments":["ACE inhibitors","ARBs","Lifestyle modification"],
"tests":["Blood Pressure Measurement"]
},

"Diabetes Mellitus":{
"symptoms":["Polyuria","Polydipsia","Weight loss"],
"treatments":["Metformin","Insulin"],
"tests":["HbA1c","Fasting Blood Sugar"]
},

"Asthma":{
"symptoms":["Wheezing","Cough","Shortness of breath"],
"treatments":["Salbutamol","Inhaled corticosteroids"],
"tests":["Spirometry"]
},

"Pneumonia":{
"symptoms":["Fever","Productive cough","Chest pain"],
"treatments":["Amoxicillin","Azithromycin"],
"tests":["Chest X-Ray","CBC"]
},

"Stroke":{
"symptoms":["Weakness","Speech difficulty","Facial droop"],
"treatments":["Thrombolysis","Mechanical thrombectomy"],
"tests":["CT Brain","MRI Brain"]
},

"Heart Failure":{
"symptoms":["Shortness of breath","Edema","Fatigue"],
"treatments":["ACE inhibitors","Furosemide"],
"tests":["Echocardiogram"]
},

"Migraine":{
"symptoms":["Headache","Photophobia","Nausea"],
"treatments":["NSAIDs","Triptans"],
"tests":[]
},

"COVID-19":{
"symptoms":["Fever","Cough","Loss of smell"],
"treatments":["Supportive care","Remdesivir"],
"tests":["RT-PCR"]
},

"Tuberculosis":{
"symptoms":["Night sweats","Weight loss","Cough"],
"treatments":["Isoniazid","Rifampicin"],
"tests":["Sputum AFB"]
},

"Anemia":{
"symptoms":["Fatigue","Weakness","Pallor"],
"treatments":["Iron supplements"],
"tests":["CBC"]
},

"Chronic Kidney Disease":{
"symptoms":["Fatigue","Edema","Nausea"],
"treatments":["ACE inhibitors","Dialysis"],
"tests":["Creatinine","eGFR"]
},

"Liver Cirrhosis":{
"symptoms":["Jaundice","Ascites","Fatigue"],
"treatments":["Diuretics","Liver transplant"],
"tests":["LFT","Ultrasound"]
},

"Appendicitis":{
"symptoms":["Right lower quadrant pain","Fever","Vomiting"],
"treatments":["Appendectomy"],
"tests":["CT Abdomen","Ultrasound"]
},

"Sepsis":{
"symptoms":["Hypotension","Fever","Tachycardia"],
"treatments":["IV antibiotics","IV fluids"],
"tests":["Blood Culture","CBC"]
},

"Epilepsy":{
"symptoms":["Seizures"],
"treatments":["Valproate","Levetiracetam"],
"tests":["EEG","MRI Brain"]
},

"Hypothyroidism":{
"symptoms":["Fatigue","Weight gain","Cold intolerance"],
"treatments":["Levothyroxine"],
"tests":["TSH","Free T4"]
},

"Hyperthyroidism":{
"symptoms":["Weight loss","Tremor","Palpitations"],
"treatments":["Methimazole"],
"tests":["TSH","Free T4"]
},

"GERD":{
"symptoms":["Heartburn","Acid reflux"],
"treatments":["Omeprazole"],
"tests":["Endoscopy"]
},

"COPD":{
"symptoms":["Chronic cough","Dyspnea"],
"treatments":["Bronchodilators"],
"tests":["Spirometry"]
},

"Osteoarthritis":{
"symptoms":["Joint pain","Morning stiffness"],
"treatments":["NSAIDs","Physiotherapy"],
"tests":["X-Ray"]
}

}

# =====================================================

medications = sorted(list({

"Metformin","Insulin","ACE inhibitors","ARBs",
"Salbutamol","Amoxicillin","Azithromycin",
"Isoniazid","Rifampicin","Furosemide",
"Omeprazole","Levothyroxine","Methimazole",
"Remdesivir","Iron supplements",
"NSAIDs","Triptans",
"Valproate","Levetiracetam",
"Bronchodilators",
"Diuretics"

}))

# =====================================================

symptoms = sorted(list({

"Headache","Dizziness","Blurred vision",

"Polyuria","Polydipsia","Weight loss",

"Wheezing","Cough","Shortness of breath",

"Fever","Chest pain","Fatigue",

"Weakness","Speech difficulty",

"Facial droop",

"Photophobia","Nausea",

"Loss of smell",

"Night sweats",

"Pallor",

"Edema",

"Jaundice",

"Ascites",

"Vomiting",

"Hypotension",

"Tachycardia",

"Seizures",

"Cold intolerance",

"Palpitations",

"Heartburn",

"Acid reflux",

"Joint pain",

"Morning stiffness"

}))

# =====================================================

procedures = sorted(list({

"Appendectomy",

"Mechanical thrombectomy",

"Thrombolysis",

"Dialysis",

"Liver transplant",

"Physiotherapy"

}))

# =====================================================

tests = sorted(list({

"CBC",

"Chest X-Ray",

"Blood Pressure Measurement",

"HbA1c",

"Fasting Blood Sugar",

"CT Brain",

"MRI Brain",

"RT-PCR",

"Sputum AFB",

"Creatinine",

"eGFR",

"LFT",

"Ultrasound",

"CT Abdomen",

"Blood Culture",

"EEG",

"TSH",

"Free T4",

"Endoscopy",

"Spirometry",

"Echocardiogram",

"X-Ray"

}))

# =====================================================

save("diseases.json", diseases)

save("medications.json", medications)

save("symptoms.json", symptoms)

save("procedures.json", procedures)

save("laboratory_tests.json", tests)

print("="*60)
print("MEDICAL KNOWLEDGE BASE UPDATED")
print("="*60)
print("Diseases :",len(diseases))
print("Medications :",len(medications))
print("Symptoms :",len(symptoms))
print("Procedures :",len(procedures))
print("Laboratory Tests :",len(tests))