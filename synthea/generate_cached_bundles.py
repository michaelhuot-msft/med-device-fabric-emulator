#!/usr/bin/env python3
"""
Generate Prepackaged/Cached Synthea-style Clinical Bundles
Conforms to load_fhir.py validation and device_registry.json qualifying conditions.
Includes rich clinical resources (MedicationRequest, Procedure, Heart Rate and BP Observations)
to fully hydrate all OMOP CDM tables (drug_exposure, procedure_occurrence, measurement, observation, person).
"""
import os
import json
import uuid
from datetime import datetime, timedelta
import random

# Qualifying SNOMED codes from device_registry.json
QUALIFYING_CONDITIONS = [
    {"code": "195967001", "display": "Asthma"},
    {"code": "13645005", "display": "Chronic obstructive lung disease"},
    {"code": "84114007", "display": "Heart failure"},
    {"code": "233604007", "display": "Pneumonia"},
    {"code": "59621000", "display": "Essential hypertension"},
    {"code": "162864005", "display": "Body mass index 30+ - obesity"},
    {"code": "840539006", "display": "COVID-19"}
]

ATLANTA_HOSPITALS = [
    "emory-university-hospital",
    "piedmont-atlanta-hospital",
    "grady-memorial-hospital",
    "northside-hospital",
    "wellstar-kennestone-hospital",
    "choa-egleston",
    "choa-scottish-rite",
    "choa-hughes-spalding"
]

MEDICATIONS = [
    {"code": "313226", "display": "Albuterol 0.09 MG/ACTUAT Inhalant Powder", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
    {"code": "310963", "display": "Fluticasone propionate 0.044 MG/ACTUAT Inhalant Suspension", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
    {"code": "855332", "display": "Lisinopril 10 MG Oral Tablet", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
    {"code": "866514", "display": "Metoprolol succinate 50 MG G Ext-Release Oral Tablet", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
    {"code": "197361", "display": "Amlodipine 5 MG Oral Tablet", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"}
]

PROCEDURES = [
    {"code": "43075005", "display": "Inhalation therapy", "system": "http://snomed.info/sct"},
    {"code": "3981000175107", "display": "Oxygen administration", "system": "http://snomed.info/sct"},
    {"code": "5300003", "display": "Artificial respiration", "system": "http://snomed.info/sct"},
    {"code": "182764009", "display": "Systemic arterial blood pressure measurement", "system": "http://snomed.info/sct"},
    {"code": "312850006", "display": "History taking", "system": "http://snomed.info/sct"}
]

def generate_patient(idx):
    patient_uuid = str(uuid.uuid4())
    encounter_uuid = str(uuid.uuid4())
    condition_uuid = str(uuid.uuid4())
    practitioner_npi = f"99998{10000 + idx}"
    
    # Assign hospital
    hospital = ATLANTA_HOSPITALS[idx % len(ATLANTA_HOSPITALS)]
    is_choa = "choa" in hospital or "childrens" in hospital
    
    # Age assignment: CHOA patients must be pediatric (< 21) to pass validation, others can be adult
    if is_choa:
        age_years = random.randint(2, 18)
    else:
        age_years = random.randint(25, 75)
        
    birth_date = (datetime.now() - timedelta(days=age_years*365.25 + random.randint(0, 365))).strftime("%Y-%m-%d")
    
    gender = random.choice(["male", "female"])
    first_name = random.choice(["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Elizabeth", "William", "Linda"])
    last_name = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"])
    
    # Qualifying condition
    cond = random.choice(QUALIFYING_CONDITIONS)
    
    bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": f"urn:uuid:{patient_uuid}",
                "resource": {
                    "resourceType": "Patient",
                    "id": patient_uuid,
                    "active": True,
                    "name": [
                        {
                            "use": "official",
                            "family": last_name,
                            "given": [first_name]
                        }
                    ],
                    "gender": gender,
                    "birthDate": birth_date,
                    "address": [
                        {
                            "use": "home",
                            "line": [f"{random.randint(100, 9999)} Peachtree St NE"],
                            "city": "Atlanta",
                            "state": "GA",
                            "postalCode": "30309",
                            "country": "US"
                        }
                    ]
                }
            },
            {
                "fullUrl": f"urn:uuid:{encounter_uuid}",
                "resource": {
                    "resourceType": "Encounter",
                    "id": encounter_uuid,
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                        "display": "ambulatory"
                    },
                    "subject": {
                        "reference": f"urn:uuid:{patient_uuid}"
                    },
                    "participant": [
                        {
                            "type": [
                                {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                            "code": "PPRF",
                                            "display": "primary performer"
                                        }
                                    ]
                                }
                            ],
                            "individual": {
                                "reference": f"Practitioner?identifier=http://hl7.org/fhir/sid/us-npi|{practitioner_npi}"
                            }
                        }
                    ],
                    "serviceProvider": {
                        "reference": f"Organization/{hospital}",
                        "display": hospital.replace("-", " ").title()
                    },
                    "location": [
                        {
                            "location": {
                                "reference": f"Location?identifier=http://example.org/location-ids|loc-{hospital}",
                                "display": f"Location {hospital.replace('-', ' ').title()}"
                            },
                            "status": "completed"
                        }
                    ]
                }
            },
            {
                "fullUrl": f"urn:uuid:{condition_uuid}",
                "resource": {
                    "resourceType": "Condition",
                    "id": condition_uuid,
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active"
                            }
                        ]
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed"
                            }
                        ]
                    },
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                                    "code": "encounter-diagnosis",
                                    "display": "Encounter Diagnosis"
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": cond["code"],
                                "display": cond["display"]
                             }
                        ],
                        "text": cond["display"]
                    },
                    "subject": {
                        "reference": f"urn:uuid:{patient_uuid}"
                    },
                    "encounter": {
                        "reference": f"urn:uuid:{encounter_uuid}"
                    },
                    "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            }
        ]
    }
    
    # 1. Add Oxygen Saturation Observation (vital-signs)
    obs_oxy_uuid = str(uuid.uuid4())
    bundle["entry"].append({
        "fullUrl": f"urn:uuid:{obs_oxy_uuid}",
        "resource": {
            "resourceType": "Observation",
            "id": obs_oxy_uuid,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "2708-6",
                        "display": "Oxygen saturation in Arterial blood by Pulse oximetry"
                    }
                ],
                "text": "Oxygen saturation"
            },
            "subject": {
                "reference": f"urn:uuid:{patient_uuid}"
            },
            "encounter": {
                "reference": f"urn:uuid:{encounter_uuid}"
            },
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "valueQuantity": {
                "value": round(random.uniform(93.0, 99.0), 1),
                "unit": "%",
                "system": "http://unitsofmeasure.org",
                "code": "%"
            }
        }
    })
    
    # 2. Add Heart Rate Observation (LOINC 8867-4 -> maps to OMOP measurement!)
    obs_hr_uuid = str(uuid.uuid4())
    bundle["entry"].append({
        "fullUrl": f"urn:uuid:{obs_hr_uuid}",
        "resource": {
            "resourceType": "Observation",
            "id": obs_hr_uuid,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate"
                    }
                ],
                "text": "Heart rate"
            },
            "subject": {
                "reference": f"urn:uuid:{patient_uuid}"
            },
            "encounter": {
                "reference": f"urn:uuid:{encounter_uuid}"
            },
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "valueQuantity": {
                "value": round(random.uniform(60.0, 100.0), 1),
                "unit": "beats/min",
                "system": "http://unitsofmeasure.org",
                "code": "/min"
            }
        }
    })

    # 3. Add Blood Pressure Observation (LOINC 8480-6 -> maps to OMOP measurement!)
    obs_bp_uuid = str(uuid.uuid4())
    bundle["entry"].append({
        "fullUrl": f"urn:uuid:{obs_bp_uuid}",
        "resource": {
            "resourceType": "Observation",
            "id": obs_bp_uuid,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure"
                    }
                ],
                "text": "Systolic blood pressure"
            },
            "subject": {
                "reference": f"urn:uuid:{patient_uuid}"
            },
            "encounter": {
                "reference": f"urn:uuid:{encounter_uuid}"
            },
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "valueQuantity": {
                "value": round(random.uniform(110.0, 140.0), 1),
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]"
            }
        }
    })

    # 4. Add MedicationRequest (RxNorm code -> maps to OMOP drug_exposure!)
    med = random.choice(MEDICATIONS)
    med_uuid = str(uuid.uuid4())
    bundle["entry"].append({
        "fullUrl": f"urn:uuid:{med_uuid}",
        "resource": {
            "resourceType": "MedicationRequest",
            "id": med_uuid,
            "status": "active",
            "intent": "order",
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "system": med["system"],
                        "code": med["code"],
                        "display": med["display"]
                    }
                ],
                "text": med["display"]
            },
            "subject": {
                "reference": f"urn:uuid:{patient_uuid}"
            },
            "encounter": {
                "reference": f"urn:uuid:{encounter_uuid}"
            },
            "authoredOn": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    })

    # 5. Add Procedure (SNOMED code -> maps to OMOP procedure_occurrence!)
    proc = random.choice(PROCEDURES)
    proc_uuid = str(uuid.uuid4())
    bundle["entry"].append({
        "fullUrl": f"urn:uuid:{proc_uuid}",
        "resource": {
            "resourceType": "Procedure",
            "id": proc_uuid,
            "status": "completed",
            "code": {
                "coding": [
                    {
                        "system": proc["system"],
                        "code": proc["code"],
                        "display": proc["display"]
                    }
                ],
                "text": proc["display"]
            },
            "subject": {
                "reference": f"urn:uuid:{patient_uuid}"
            },
            "encounter": {
                "reference": f"urn:uuid:{encounter_uuid}"
            },
            "performedDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    })
    
    filename = f"{first_name}_{last_name}_{patient_uuid}.json"
    return filename, bundle

def main():
    out_dir = "/Users/joey/git/med-device-fabric-emulator/synthea/prepackaged"
    
    # Delete existing files in output directory first to prevent naming collisions
    print(f"Cleaning existing files in {out_dir}...")
    if os.path.exists(out_dir):
        for file in os.listdir(out_dir):
            file_path = os.path.join(out_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Generating 10 comprehensive clinical bundle files in {out_dir}...")
    for idx in range(10):
        fname, bundle = generate_patient(idx)
        filepath = os.path.join(out_dir, fname)
        with open(filepath, "w") as f:
            json.dump(bundle, f, indent=2)
        print(f"  Generated {fname}")
        
    print("Done generating comprehensive clinical bundles!")

if __name__ == "__main__":
    main()
