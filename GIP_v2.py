import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any

# Initialize Faker for Indian locale
fake = Faker('en_IN')

# Configuration
TOTAL_PROVIDERS = 500
QUALITY_DISTRIBUTION = {
    'complete': 0.60,
    'incomplete': 0.20,
    'outdated': 0.15,
    'errors': 0.05
}

# Reference Data
MALE_FIRST_NAMES = [
    'Rajesh', 'Amit', 'Suresh', 'Vijay', 'Anil', 'Ramesh', 'Pradeep', 'Sanjay',
    'Rakesh', 'Manoj', 'Ashok', 'Dinesh', 'Ravi', 'Ajay', 'Rahul', 'Rohit',
    'Anand', 'Deepak', 'Vikas', 'Kiran'
]

FEMALE_FIRST_NAMES = [
    'Priya', 'Anjali', 'Neha', 'Pooja', 'Swati', 'Kavita', 'Deepa', 'Sunita',
    'Shalini', 'Madhuri', 'Asha', 'Meera', 'Nisha', 'Sapna', 'Anita', 'Jyoti',
    'Seema', 'Vandana'
]

LAST_NAMES = [
    'Sharma', 'Kumar', 'Singh', 'Patel', 'Gupta', 'Reddy', 'Shah', 'Verma',
    'Iyer', 'Nair', 'Rao', 'Desai', 'Mehta', 'Joshi', 'Pillai', 'Agarwal',
    'Banerjee', 'Chatterjee', 'Das', 'Khan', 'Malhotra', 'Kapoor', 'Khanna',
    'Chopra', 'Bhatia'
]

SPECIALTIES = [
    'General Medicine', 'Pediatrics', 'Cardiology', 'Dermatology', 'Orthopedics',
    'Gynecology & Obstetrics', 'Psychiatry', 'Radiology', 'Anesthesiology',
    'Emergency Medicine', 'Neurology', 'Oncology', 'Ophthalmology', 'Urology',
    'ENT', 'Gastroenterology', 'Endocrinology', 'Pulmonology', 'Nephrology',
    'General Surgery', 'Plastic Surgery', 'Pathology', 'Ayurveda', 'Homeopathy',
    'Dentistry'
]

SUBSPECIALTIES = {
    'Cardiology': ['Interventional Cardiology', 'Electrophysiology', 'Heart Failure'],
    'Orthopedics': ['Joint Replacement', 'Spine Surgery', 'Sports Medicine'],
    'Neurology': ['Stroke', 'Epilepsy', 'Movement Disorders'],
    'Oncology': ['Medical Oncology', 'Radiation Oncology', 'Surgical Oncology'],
    'General Surgery': ['Laparoscopic Surgery', 'Bariatric Surgery', 'Trauma Surgery']
}

CITIES_AND_AREAS = {
    'Mumbai': ['Andheri', 'Bandra', 'Powai', 'Dadar', 'Borivali', 'Churchgate', 'Worli', 'Juhu'],
    'Delhi': ['Saket', 'Dwarka', 'Rohini', 'Greater Kailash', 'Vasant Kunj', 'Defence Colony'],
    'Bangalore': ['Koramangala', 'Indiranagar', 'Whitefield', 'Jayanagar', 'HSR Layout', 'Electronic City'],
    'Chennai': ['T Nagar', 'Anna Nagar', 'Adyar', 'Velachery', 'OMR', 'Nungambakkam'],
    'Hyderabad': ['Banjara Hills', 'Jubilee Hills', 'Gachibowli', 'Hitech City', 'Secunderabad'],
    'Pune': ['Koregaon Park', 'Kalyani Nagar', 'Kothrud', 'Hinjewadi', 'Aundh']
}

STATE_MAPPING = {
    'Mumbai': 'Maharashtra',
    'Pune': 'Maharashtra',
    'Delhi': 'Delhi',
    'Bangalore': 'Karnataka',
    'Chennai': 'Tamil Nadu',
    'Hyderabad': 'Telangana'
}

HOSPITALS = {
    'Mumbai': ['Lilavati Hospital', 'Kokilaben Hospital', 'Fortis Hospital Mulund', 'Breach Candy Hospital'],
    'Delhi': ['AIIMS Delhi', 'Fortis Vasant Kunj', 'Max Saket', 'Apollo Delhi'],
    'Bangalore': ['Manipal Hospital', 'Apollo Bangalore', 'Fortis Bangalore', 'Narayana Health City'],
    'Chennai': ['Apollo Chennai', 'Fortis Malar', 'MIOT International', 'Kauvery Hospital'],
    'Hyderabad': ['Apollo Hyderabad', 'KIMS Hospital', 'Care Hospital', 'Yashoda Hospital'],
    'Pune': ['Ruby Hall Clinic', 'Sahyadri Hospital', 'Deenanath Mangeshkar Hospital', 'Jupiter Hospital']
}

MEDICAL_SCHOOLS = [
    'AIIMS Delhi', 'CMC Vellore', 'JIPMER Puducherry', 'Maulana Azad Medical College Delhi',
    'King Georges Medical University Lucknow', 'Grant Medical College Mumbai',
    'Madras Medical College Chennai', 'Armed Forces Medical College Pune'
]

INSURANCE_NETWORKS = [
    'Star Health Insurance', 'ICICI Lombard', 'HDFC Ergo', 'Max Bupa Health Insurance',
    'Care Health Insurance', 'Bajaj Allianz', 'New India Assurance', 'United India Insurance'
]

LANGUAGES = {
    'Maharashtra': ['English', 'Hindi', 'Marathi'],
    'Karnataka': ['English', 'Hindi', 'Kannada'],
    'Tamil Nadu': ['English', 'Tamil'],
    'Delhi': ['English', 'Hindi'],
    'Telangana': ['English', 'Hindi', 'Telugu']
}

def generate_phone(quality: str) -> str:
    if quality == 'complete':
        return f"+91 {random.randint(7000000000, 9999999999)}"
    elif quality == 'outdated':
        return f"+91 5555555555"
    elif quality == 'errors':
        return str(random.randint(1000000, 9999999))
    return ""

def generate_email(first_name: str, last_name: str, quality: str) -> str:
    if quality == 'complete':
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        return f"dr.{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
    elif quality == 'outdated':
        return f"old_{first_name.lower()}@email.com"
    elif quality == 'errors':
        return f"{first_name.lower()}@invalid"
    return ""

def generate_registration_number(state: str, quality: str) -> str:
    if quality == 'complete':
        state_code = state[:2].upper()
        return f"{state_code}/{random.randint(10000, 99999)}"
    elif quality == 'errors':
        return "ERROR/12345"
    return f"{state[:2].upper()}/{random.randint(10000, 99999)}"

def introduce_typo(text: str) -> str:
    if not text:
        return text
    if len(text) < 4:
        return text
    
    # Common typo patterns
    pos = random.randint(0, len(text)-1)
    typos = [
        lambda t, p: t[:p] + t[p+1:],  # deletion
        lambda t, p: t[:p] + random.choice('abcdefghijklmnopqrstuvwxyz') + t[p:],  # insertion
        lambda t, p: t[:p] + t[p+1] + t[p] + t[p+2:] if p < len(t)-1 else t  # transposition
    ]
    return random.choice(typos)(text, pos)

def generate_provider(idx: int, quality: str) -> Dict[str, Any]:
    gender = random.choice(['M', 'F'])
    first_name = random.choice(MALE_FIRST_NAMES if gender == 'M' else FEMALE_FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    city = random.choice(list(CITIES_AND_AREAS.keys()))
    state = STATE_MAPPING[city]
    area = random.choice(CITIES_AND_AREAS[city])
    specialty = random.choice(SPECIALTIES)
    
    if quality == 'errors':
        first_name = introduce_typo(first_name)
        last_name = introduce_typo(last_name)
    
    provider = {
        # Demographics
        'provider_id': f"PRV{idx:06d}",
        'registration_number': generate_registration_number(state, quality),
        'first_name': first_name,
        'last_name': last_name,
        'full_name': f"Dr. {first_name} {last_name}",
        'gender': gender,
        'date_of_birth': fake.date_of_birth(minimum_age=30, maximum_age=70).strftime('%Y-%m-%d'),
        'profile_photo_url': "" if random.random() < 0.7 else f"https://provider-photos.healthverify.ai/{idx}.jpg",

        # Contact Information
        'practice_name': f"Dr. {last_name}'s {specialty} Clinic" + (" (CLOSED)" if quality == 'outdated' else ""),
        'practice_address': fake.street_address() + (" (MOVED)" if quality == 'outdated' else ""),
        'area': area,
        'city': city,
        'state': state,
        'pin_code': fake.postcode() if quality != 'errors' else str(random.randint(1000, 9999)),
        'phone': generate_phone(quality),
        'alternate_phone': generate_phone(quality) if random.random() < 0.3 else "",
        'email': generate_email(first_name, last_name, quality),
        'website': f"https://dr{last_name.lower()}.com" if quality == 'complete' and random.random() < 0.3 else "",

        # Professional Details
        'specialty': specialty,
        'sub_specialty': random.choice(SUBSPECIALTIES.get(specialty, [''])) if specialty in SUBSPECIALTIES else "",
        'qualification': random.choice(['MBBS', 'MD', 'MS', 'DNB']),
        'medical_school': random.choice(MEDICAL_SCHOOLS),
        'graduation_year': random.randint(1985, 2020),
        'license_number': generate_registration_number(state, quality),
        'license_state': state,
        'license_status': 'Active' if quality != 'outdated' else 'Expired',
        'board_certification': random.choice(['MCI', 'DNB', 'MRCP']),
        'certification_year': random.randint(1990, 2022),

        # Network Affiliations
        'hospital_affiliation': random.choice(HOSPITALS[city]),
        'group_practice': f"{last_name} Medical Associates" if random.random() < 0.4 else "",
        'insurance_networks': ", ".join(random.sample(INSURANCE_NETWORKS, random.randint(2, 5))),
        'empanelment_status': random.choice(['Empanelled', 'Not Empanelled', 'Pending']),
        'network_tier': f"Tier {random.randint(1, 3)}",

        # Services
        'clinical_focus': ", ".join(random.sample(SUBSPECIALTIES.get(specialty, [specialty]), min(len(SUBSPECIALTIES.get(specialty, [specialty])), random.randint(1, 3)))),
        'procedures_offered': "General Consultation, Specialty Procedures",
        'consultation_fee': random.randint(500, 5000),
        'appointment_availability': 'Not Accepting' if quality == 'outdated' else random.choice(['Available', 'Limited']),
        'teleconsultation_available': random.choice(['Yes', 'No']),
        'emergency_services': random.choice(['Yes', 'No']),

        # Location and Facilities
        'facility_type': random.choice(['Clinic', 'Hospital', 'Diagnostic Center', 'Multi-specialty']),
        'diagnostic_facilities': ", ".join(random.sample(['X-Ray', 'CT Scan', 'MRI', 'Ultrasound', 'Lab'], random.randint(1, 5))),
        'parking_available': random.choice(['Yes', 'No']),
        'wheelchair_accessible': random.choice(['Yes', 'No']),

        # Additional Metadata
        'languages_spoken': ", ".join(LANGUAGES[state]),
        'accepting_new_patients': 'No' if quality == 'outdated' else random.choice(['Yes', 'Limited']),
        'data_quality_flag': quality,
        'created_date': (datetime.now() - timedelta(days=random.randint(1, 730))).strftime('%Y-%m-%d'),
        'last_verified_date': (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d'),
        'last_updated_date': datetime.now().strftime('%Y-%m-%d')
    }

    # Apply quality-specific modifications
    if quality == 'incomplete':
        optional_fields = ['website', 'alternate_phone', 'group_practice', 'sub_specialty',
                         'profile_photo_url', 'diagnostic_facilities']
        for field in random.sample(optional_fields, random.randint(2, 4)):
            provider[field] = ""

    return provider

def save_to_csv(data: List[Dict[str, Any]], filename: str = 'Indian_providers.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"CSV file saved: {filename}")

def save_to_excel(data: List[Dict[str, Any]], filename: str = 'Indian_providers.xlsx'):
    df = pd.DataFrame(data)
    
    # Create Excel writer object
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Write all data
        df.to_excel(writer, sheet_name='All Providers', index=False)
        
        # Write quality-specific sheets
        for quality in ['complete', 'incomplete', 'outdated', 'errors']:
            quality_df = df[df['data_quality_flag'] == quality]
            quality_df.to_excel(writer, sheet_name=quality.capitalize(), index=False)
    
    print(f"Excel file saved: {filename}")

def save_to_json(data: List[Dict[str, Any]], filename: str = 'Indian_providers.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON file saved: {filename}")

def print_statistics(data: List[Dict[str, Any]]):
    df = pd.DataFrame(data)
    
    print("\n=== Dataset Statistics ===")
    print(f"\nTotal Providers: {len(df)}")
    
    print("\nQuality Distribution:")
    quality_dist = df['data_quality_flag'].value_counts()
    for quality, count in quality_dist.items():
        print(f"{quality.capitalize()}: {count} ({count/len(df)*100:.1f}%)")
    
    print("\nGeographic Distribution:")
    city_dist = df['city'].value_counts()
    for city, count in city_dist.items():
        print(f"{city}: {count} ({count/len(df)*100:.1f}%)")
    
    print("\nSpecialty Distribution:")
    specialty_dist = df['specialty'].value_counts().head(10)
    print("Top 10 Specialties:")
    for specialty, count in specialty_dist.items():
        print(f"{specialty}: {count}")
    
    print("\nData Completeness:")
    null_counts = df.isnull().sum()
    if null_counts.any():
        print("\nFields with missing values:")
        for field, count in null_counts[null_counts > 0].items():
            print(f"{field}: {count} missing")
    else:
        print("No missing values in required fields")

def main():
    # Calculate records per quality type
    total_records = {
        'complete': int(TOTAL_PROVIDERS * QUALITY_DISTRIBUTION['complete']),
        'incomplete': int(TOTAL_PROVIDERS * QUALITY_DISTRIBUTION['incomplete']),
        'outdated': int(TOTAL_PROVIDERS * QUALITY_DISTRIBUTION['outdated']),
        'errors': TOTAL_PROVIDERS - int(TOTAL_PROVIDERS * QUALITY_DISTRIBUTION['complete']) 
                                   - int(TOTAL_PROVIDERS * QUALITY_DISTRIBUTION['incomplete'])
                                   - int(TOTAL_PROVIDERS * QUALITY_DISTRIBUTION['outdated'])
    }
    
    providers = []
    idx = 1
    
    # Generate providers for each quality type
    for quality, count in total_records.items():
        for _ in range(count):
            providers.append(generate_provider(idx, quality))
            idx += 1
    
    # Shuffle the providers to mix quality types
    random.shuffle(providers)
    
    # Save in different formats
    save_to_csv(providers)
    save_to_excel(providers)
    save_to_json(providers)
    
    # Print statistics
    print_statistics(providers)

if __name__ == "__main__":
    main()