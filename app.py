import os
import time
import datetime
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Ensure audio directory exists
BASE_DIR = Path(__file__).parent.resolve()
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Meta
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Farmers Welfare Scheme Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. Multilingual Localization Dictionary
# -----------------------------------------------------------------------------
LOCALES = {
    "English": {
        "title": "Farmers Welfare Scheme Assistant",
        "subtitle": "🌾 Smart Voice & Text Assistant for Central and State Agricultural Schemes",
        "badge": "Govt & State Welfare Schemes AI",
        "select_lang": "Choose Language / மொழியை தேர்ந்தெடுக்கவும் / భాషను ఎంచుకోండి",
        "input_header": "Ask Your Farming & Welfare Scheme Query",
        "input_placeholder": "E.g., How do I apply for PM-KISAN 17th installment? What are the crop insurance eligibility criteria?",
        "voice_record_title": "🎙️ Voice Input (Microphone Recording)",
        "voice_record_caption": "Click the microphone button below to record your voice. Click again to stop.",
        "voice_transcribing": "🔄 Transcribing audio with Groq Whisper (whisper-large-v3-turbo)...",
        "transcribed_success": "✅ Voice Transcribed Successfully:",
        "audio_playback_label": "🎧 Recorded Audio Preview:",
        "submit_btn": "🔍 Get Scheme Assistance",
        "clear_btn": "🧹 Clear",
        "quick_topics_label": "Popular Farmer Queries:",
        "quick_topics": [
            "PM-KISAN ₹6,000 Installment Status",
            "PM Fasal Bima (Crop Insurance)",
            "Kisan Credit Card (KCC) Loan Limit",
            "Solar Pump Subsidy (PM-KUSUM)",
            "Tractor & Farm Machinery Subsidy"
        ],
        "response_title": "📢 Assistant Response & Scheme Details",
        "helpline_title": "📞 Kisan Call Center & Helplines",
        "helpline_text": "National Toll-Free Helpline: 1800-180-1551 (6:00 AM to 10:00 PM)",
        "docs_needed": "📑 Essential Documents Required",
        "steps_title": "📌 How to Apply Step-by-Step",
        "benefits_title": "🎁 Key Benefits & Financial Assistance",
        "sidebar_schemes_title": "🌱 Featured Welfare Schemes",
        "sidebar_about": "About this Assistant",
        "sidebar_about_desc": "Empowering farmers across India with instant, multilingual guidance on government subsidies, direct benefit transfers, and welfare initiatives.",
        "groq_settings_title": "🔑 Groq Whisper API Settings",
        "status_ready": "Assistant Ready"
    },
    "தமிழ் (Tamil)": {
        "title": "உழவர் நலத்திட்ட வழிகாட்டி உதவியாளர்",
        "subtitle": "🌾 மத்திய மற்றும் மாநில அரசு உழவர் நலத்திட்டங்களுக்கான குரல் & உரை வழிகாட்டி",
        "badge": "வேளாண் நலத்திட்ட AI உதவியாளர்",
        "select_lang": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "input_header": "உங்கள் வேளாண் மற்றும் திட்டக் கேள்வியைக் கேளுங்கள்",
        "input_placeholder": "எ.கா: பி.எம்-கிசான் உதவித்தொகை பெறுவது எப்படி? பயிர் காப்பீடு விவரங்கள் என்ன?",
        "voice_record_title": "🎙️ குரல் பதிவு (மைக்ரோஃபோன்)",
        "voice_record_caption": "கீழே உள்ள மைக்ரோஃபோன் பொத்தானை அழுத்தி பேசவும். நிறுத்துவதற்கு மீண்டும் அழுத்தவும்.",
        "voice_transcribing": "🔄 குரல் உரையாக மாற்றப்படுகிறது (Groq Whisper)...",
        "transcribed_success": "✅ குரல் வெற்றிகரமாக மாற்றப்பட்டது:",
        "audio_playback_label": "🎧 பதிவு செய்யப்பட்ட ஆடியோ:",
        "submit_btn": "🔍 திட்ட விவரங்களைப் பெறுங்கள்",
        "clear_btn": "🧹 அழிக்கவும்",
        "quick_topics_label": "அடிக்கடி கேட்கப்படும் கேள்விகள்:",
        "quick_topics": [
            "பி.எம்-கிசான் ₹6000 தவணை நிலை",
            "பயிர் காப்பீட்டுத் திட்டம் (PMFBY)",
            "உழவர் கடன் அட்டை (KCC)",
            "சூரிய மின் பம்பு மானியம் (KUSUM)",
            "டிராக்டர் & வேளாண் கருவி மானியம்"
        ],
        "response_title": "📢 உதவியாளரின் விளக்கம் மற்றும் திட்ட விவரங்கள்",
        "helpline_title": "📞 உழவர் உதவி எண்கள்",
        "helpline_text": "தேசிய உழவர் கட்டணமில்லா உதவி எண்: 1800-180-1551 (காலை 6 மணி முதல் இரவு 10 மணி வரை)",
        "docs_needed": "📑 தேவையான முக்கிய ஆவணங்கள்",
        "steps_title": "📌 விண்ணப்பிக்கும் வழிமுறைகள்",
        "benefits_title": "🎁 திட்டத்தின் பலன்கள் & நிதி உதவி",
        "sidebar_schemes_title": "🌱 முக்கிய உழவர் நலத்திட்டங்கள்",
        "sidebar_about": "உதவியாளர் பற்றி",
        "sidebar_about_desc": "விவசாயிகளுக்கு அரசு நலத்திட்டங்கள், மானியங்கள் மற்றும் உதவித்தொகை பற்றிய தகவல்களை தாய்மொழியில் வழங்குகிறது.",
        "groq_settings_title": "🔑 Groq Whisper API அமைப்புகள்",
        "status_ready": "உதவியாளர் தயார் நிலையில் உள்ளார்"
    },
    "తెలుగు (Telugu)": {
        "title": "రైతు సంక్షేమ పథకాల సహాయకుడు",
        "subtitle": "🌾 కేంద్ర, రాష్ట్ర వ్యవసాయ పథకాల కోసం ఆధునిక వాయిస్ మరియు టెక్స్ట్ అసిస్టెంట్",
        "badge": "రైతు సంక్షేమ పథకాల AI",
        "select_lang": "భాషను ఎంచుకోండి",
        "input_header": "మీ వ్యవసాయ & పథకాల సందేహాన్ని అడగండి",
        "input_placeholder": "ఉదాహరణ: పీఎం కిసాన్ నిధులు ఎలా పొందాలి? పంట బీమా అర్హతలు ఏమిటి?",
        "voice_record_title": "🎙️ వాయిస్ ఇన్‌పుట్ (మైక్రోఫోన్ రికార్డింగ్)",
        "voice_record_caption": "మీ వాయిస్ రికార్డ్ చేయడానికి క్రింది మైక్రోఫోన్ బటన్‌ను క్లిక్ చేయండి.",
        "voice_transcribing": "🔄 ఆడియో ప్రాసెస్ అవుతోంది (Groq Whisper)...",
        "transcribed_success": "✅ వాయిస్ విజయవంతంగా మార్చబడింది:",
        "audio_playback_label": "🎧 రికార్డ్ చేసిన ఆడియో:",
        "submit_btn": "🔍 పథకం వివరాలు పొందండి",
        "clear_btn": "🧹 క్లియర్",
        "quick_topics_label": "ప్రముఖ ప్రశ్నలు:",
        "quick_topics": [
            "పీఎం కిసాన్ ₹6,000 వాయిదా వివరాలు",
            "రైతు భరోసా / పంట బీమా (PMFBY)",
            "కిసాన్ క్రెడిట్ కార్డు (KCC)",
            "సోలార్ పంపు సబ్సిడీ (PM-KUSUM)",
            "ట్రాక్టర్ & వ్యవసాయ యంత్రాల సబ్సిడీ"
        ],
        "response_title": "📢 సహాయక సమాధానం & పథకం వివరాలు",
        "helpline_title": "📞 కిసాన్ కాల్ సెంటర్ & హెల్ప్‌లైన్",
        "helpline_text": "జాతీయ ఉచిత హెల్ప్‌లైన్: 1800-180-1551 (ఉదయం 6:00 నుండి రాత్రి 10:00 వరకు)",
        "docs_needed": "📑 అవసరమైన పత్రాలు",
        "steps_title": "📌 దరఖాస్తు చేసుకునే విధానం",
        "benefits_title": "🎁 ముఖ్యమైన ప్రయోజనాలు & ఆర్థిక సహాయం",
        "sidebar_schemes_title": "🌱 ముఖ్యమైన రైతు పథకాలు",
        "sidebar_about": "ఈ అసిస్టెంట్ గురించి",
        "sidebar_about_desc": "రైతులకు ప్రభుత్వ సబ్సిడీలు, సంక్షేమ పథకాల వివరాలను సులభంగా మాతృభాషలో అందించే వేదిక.",
        "groq_settings_title": "🔑 Groq Whisper API సెట్టింగులు",
        "status_ready": "అసిస్టెంట్ సిద్ధంగా ఉంది"
    }
}

# -----------------------------------------------------------------------------
# 3. Scheme Knowledge Base
# -----------------------------------------------------------------------------
KNOWLEDGE_BASE = {
    "English": {
        "default": {
            "title": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "overview": "PM-KISAN provides direct income support of ₹6,000 per year in three equal installments of ₹2,000 directly into the Aadhaar-linked bank accounts of eligible farmer families.",
            "benefits": [
                "₹6,000 per annum in 3 four-monthly installments of ₹2,000.",
                "Direct Benefit Transfer (DBT) without intermediaries.",
                "Universal coverage for small, marginal, and landholding farmers."
            ],
            "docs": ["Aadhaar Card", "Land Ownership Record (7/12, Patta/Chitta)", "Active Bank Account linked with Aadhaar", "Mobile Number"],
            "steps": [
                "Visit the official portal at pmkisan.gov.in or nearest CSC center.",
                "Click on 'New Farmer Registration' and enter Aadhaar number & State.",
                "Provide land record details and bank account credentials.",
                "Complete e-KYC via Aadhaar OTP or Biometrics to ensure uninterrupted installments."
            ]
        },
        "pmkisan": {
            "title": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
            "overview": "Direct financial assistance of ₹6,000 annually given in 3 installments of ₹2,000 every 4 months to all eligible landholding farmer families.",
            "benefits": [
                "₹2,000 deposited every 4 months directly to your bank account.",
                "100% centrally funded scheme.",
                "Assistance for purchasing seeds, fertilizers, and equipment."
            ],
            "docs": ["Aadhaar Card", "Land Title (Patta/Khata)", "Aadhaar-seeded Bank Passbook", "Active Mobile Number"],
            "steps": [
                "Go to pmkisan.gov.in -> Farmer Corner -> New Farmer Registration.",
                "Enter Aadhaar and Mobile number; verify OTP.",
                "Upload Land Revenue record copy.",
                "Complete mandatory e-KYC using Aadhaar OTP."
            ]
        },
        "insurance": {
            "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "overview": "Comprehensive risk insurance covering loss of crops due to non-preventable natural risks from pre-sowing to post-harvest stages.",
            "benefits": [
                "Uniform low premium: 2% for Kharif crops, 1.5% for Rabi crops, and 5% for commercial/horticultural crops.",
                "Full insured amount paid against localized calamities and pest attacks.",
                "Claims settled directly to farmer bank accounts."
            ],
            "docs": ["Crop Sowing Certificate / Adangal / Pahani", "Land Revenue Passbook", "Aadhaar Card", "Bank Account Details"],
            "steps": [
                "Enroll before the cutoff date through Bank, CSC Center, or pmfby.gov.in.",
                "Submit sowing proof and premium amount.",
                "In case of crop loss, report within 72 hours via Crop Insurance App or toll-free 14447."
            ]
        },
        "kcc": {
            "title": "Kisan Credit Card (KCC) Scheme",
            "overview": "Provides farmers with timely credit for agricultural requirements, seeds, fertilizers, and animal husbandry at a highly subsidized interest rate.",
            "benefits": [
                "Credit limit up to ₹3 Lakhs at an effective interest rate of 4% (with 3% prompt repayment incentive).",
                "No collateral required for loans up to ₹1.60 Lakhs.",
                "Covers crop cultivation, post-harvest expenses, and dairy/poultry farming."
            ],
            "docs": ["Application Form", "Land Record Documents", "ID & Address Proof (Aadhaar/Voter ID)", "Passport Size Photograph"],
            "steps": [
                "Download KCC application form from bank website or nearest rural bank.",
                "Submit land ownership proof and crop details to your local bank branch.",
                "Bank inspects documents and issues KCC card within 14 working days."
            ]
        },
        "solar": {
            "title": "PM-KUSUM Solar Pump Scheme",
            "overview": "Enables farmers to install standalone solar agriculture pumps or solarize existing grid-connected agriculture pumps with up to 60-90% subsidy.",
            "benefits": [
                "Up to 60% government subsidy (30% Central + 30% State).",
                "Farmers contribute only 10% to 40% of the capital cost.",
                "Daytime uninterrupted clean solar power for irrigation."
            ],
            "docs": ["Aadhaar Card", "Land Mutation / Revenue Record", "Bank Account Details", "Electricity Connection details (if grid-connected)"],
            "steps": [
                "Register on the state renewable energy development agency portal (e.g. TEDA, REDA, etc.).",
                "Select pump capacity (3HP, 5HP, or 7.5HP) based on borewell and land size.",
                "Pay the beneficiary share and receive government installation."
            ]
        },
        "machinery": {
            "title": "Sub-Mission on Agricultural Mechanization (SMAM)",
            "overview": "Subsidies ranging from 40% to 50% (and up to 80% for Custom Hiring Centers) for buying tractors, power tillers, harvesters, and implements.",
            "benefits": [
                "40% to 50% subsidy for individual small and marginal farmers.",
                "Special incentives for women and SC/ST farmers.",
                "Access to modern farm equipment to reduce labor costs and increase yield."
            ],
            "docs": ["Aadhaar Card", "Land Record (Patta/Chitta)", "Bank Passbook", "Caste/Category Certificate (if applicable)"],
            "steps": [
                "Visit agrimachinery.nic.in and register under farmer category.",
                "Select desired equipment and approved dealership.",
                "Upload land and identity documents to generate subsidy sanction token."
            ]
        }
    },
    "தமிழ் (Tamil)": {
        "default": {
            "title": "பிரதமர் கிசான் சம்மான் நிதி (PM-KISAN)",
            "overview": "விவசாயக் குடும்பங்களுக்கு ஆண்டுதோறும் ₹6,000 நிதி உதவி மூன்று சம தவணைகளாக (தலா ₹2,000) நேரடியாக அவர்களின் ஆதார் இணைக்கப்பட்ட வங்கிக் கணக்கில் வரவு வைக்கப்படுகிறது.",
            "benefits": [
                "ஆண்டுக்கு ₹6,000 நேரடி வங்கிப் பரிமாற்றம் (DBT).",
                "விதை, உரம் மற்றும் வேளாண் இடுபொருட்கள் வாங்க உதவி.",
                "இடைத்தரகர்கள் இன்றி நேரிடையாக வங்கிக் கணக்கில் சேரும்."
            ],
            "docs": ["ஆதார் அட்டை", "நிலப்பட்டா / சிட்டா / அடங்கல்", "ஆதார் இணைக்கப்பட்ட வங்கிக் கணக்கு புத்தகம்", "மொபைல் எண்"],
            "steps": [
                "pmkisan.gov.in இணையதளம் அல்லது அருகிலுள்ள இ-சேவை மையத்தை அணுகவும்.",
                "'New Farmer Registration' மூலம் ஆதார் மற்றும் நில விவரங்களை உள்ளிடவும்.",
                "ஆதார் OTP அல்லது பயோமெட்ரிக் மூலம் e-KYC சரிபார்ப்பை பூர்த்தி செய்யவும்."
            ]
        },
        "pmkisan": {
            "title": "பி.எம்-கிசான் உதவித்தொகை திட்டம்",
            "overview": "விவசாயிகளுக்கு 4 மாதங்களுக்கு ஒருமுறை ₹2,000 வீதம் ஆண்டுக்கு மொத்தம் ₹6,000 வங்கி கணக்கில் செலுத்தப்படுகிறது.",
            "benefits": [
                "ஆண்டுக்கு 3 தவணைகளில் ₹6,000 உதவித்தொகை.",
                "சிறு, குறு விவசாயிகளுக்கு முழுமையான பலன்.",
                "எளிய ஆன்லைன் பதிவு மற்றும் கண்காணிப்பு."
            ],
            "docs": ["ஆதார் அட்டை", "பட்டா / சிட்டா நகல்", "வங்கி கணக்கு விவரம்", "கைபேசி எண்"],
            "steps": [
                "pmkisan.gov.in போர்ட்டலில் சென்று நில ஆவணங்களை பதிவேற்றவும்.",
                "e-KYC நிலையை சரிபார்த்து புதுப்பிக்கவும்.",
                "வேளாண் விரிவாக்க அலுவலர் மூலம் சரிபார்க்கப்படும்."
            ]
        },
        "insurance": {
            "title": "பிரதம மந்திரி பயிர் காப்பீட்டுத் திட்டம் (PMFBY)",
            "overview": "இயற்கை பேரிடர்கள், வறட்சி, பூச்சி தாக்குதல் மற்றும் வெள்ளத்தால் ஏற்படும் பயிர் இழப்புகளுக்கு முழு காப்பீடு மற்றும் இழப்பீடு வழங்குகிறது.",
            "benefits": [
                "குறைந்த பிரீமியம் விகிதம்: காரிஃப் பயிர்களுக்கு 2%, ரபி பயிர்களுக்கு 1.5%.",
                "பயிர் சேதமடைந்தால் 72 மணி நேரத்திற்குள் தகவல் தெரிவித்து இழப்பீடு பெறலாம்.",
                "நேரடியாக வங்கிக் கணக்கில் இழப்பீட்டுத் தொகை வரவு."
            ],
            "docs": ["அடங்கல் / விதைப்புச் சான்றிதழ்", "பட்டா நகல்", "ஆதார் அட்டை", "வங்கி கணக்கு புத்தகம்"],
            "steps": [
                "தொடக்க வேளாண்மை கூட்டுறவு வங்கி அல்லது இ-சேவை மையம் மூலம் விண்ணப்பிக்கவும்.",
                "பயிர் சேதம் ஏற்பட்டால் 'Crop Insurance' ஆப் அல்லது 14447 என்ற உதவி எண்ணில் பதிவு செய்யவும்."
            ]
        },
        "kcc": {
            "title": "கிசான் கிரெடிட் கார்டு (KCC) பயிர்க் கடன் திட்டம்",
            "overview": "விவசாயிகளுக்கு குறைந்த வட்டியில் உடனடியாக வேளாண் மற்றும் கால்நடை பராமரிப்பு கடன் வழங்கப்படுகிறது.",
            "benefits": [
                "₹3 லட்சம் வரை 4% குறைந்த வட்டி விகிதத்தில் கடன்.",
                "₹1.60 லட்சம் வரை பிணையம் (Security) தேவையில்லை.",
                "கால்நடை வளர்ப்பு மற்றும் மீன்வளர்ப்புக்கும் கடன் உண்டு."
            ],
            "docs": ["விண்ணப்பப் படிவம்", "நில உரிமை ஆவணங்கள்", "ஆதார் அட்டை", "புகைப்படம்"],
            "steps": [
                "அருகிலுள்ள தேசியமயமாக்கப்பட்ட அல்லது கூட்டுறவு வங்கியை அணுகவும்.",
                "KCC விண்ணப்ப படிவத்துடன் பட்டா மற்றும் சிட்டாவை சமர்ப்பிக்கவும்."
            ]
        },
        "solar": {
            "title": "பி.எம்-குசும் (PM-KUSUM) சூரிய மின் பம்பு திட்டம்",
            "overview": "விவசாய நிலங்களில் 60% முதல் 70% வரை அரசு மானியத்துடன் சோலார் பம்புசெட்டுகள் அமைக்கும் திட்டம்.",
            "benefits": [
                "மத்திய மற்றும் மாநில அரசு இணைந்து 60% மானியம் வழங்குகிறது.",
                "பகல் நேரத்தில் தடையற்ற இலவச மின்சாரம் மற்றும் பாசன வசதி.",
                "கூடுதல் மின்சாரத்தை மின்கட்டமைப்பிற்கு விற்று வருமானம் ஈட்டலாம்."
            ],
            "docs": ["ஆதார் அட்டை", "நில உரிமை ஆவணம்", "வங்கி விவரங்கள்", "கிணறு / போர்வெல் சான்று"],
            "steps": [
                "TEDA / வேளாண் பொறியியல் துறை போர்ட்டலில் விண்ணப்பிக்கவும்.",
                "விவசாயி பங்களிப்பு தொகையை செலுத்தி சோலார் மோட்டார் பெறலாம்."
            ]
        },
        "machinery": {
            "title": "வேளாண் இயந்திரமயமாக்கல் திட்டம் (SMAM)",
            "overview": "டிராக்டர்கள், பவர்டில்லர்கள், களையெடுக்கும் கருவிகள் வாங்க விவசாயிகளுக்கு 40% முதல் 50% வரை மானியம்.",
            "benefits": [
                "டிராக்டர் மற்றும் கருவிகளுக்கு 40% - 50% நேரடி மானியம்.",
                "பெண் விவசாயிகள் மற்றும் ஆதிதிராவிட விவசாயிகளுக்கு கூடுதல் முன்னுரிமை.",
                "வேளாண் கூலி செலவு குறைந்து மகசூல் அதிகரிக்கும்."
            ],
            "docs": ["ஆதார் அட்டை", "பட்டா / சிட்டா", "வங்கி பாஸ்புக்", "சாதிச் சான்றிதழ் (பொருந்தினால்)"],
            "steps": [
                "agrimachinery.nic.in அல்லது உழவன் செயலியில் பதிவு செய்யவும்.",
                "அங்கீகரிக்கப்பட்ட நிறுவனத்திடமிருந்து இயந்திரத்தை தேர்வு செய்து மானியம் பெறவும்."
            ]
        }
    },
    "తెలుగు (Telugu)": {
        "default": {
            "title": "పీఎం కిసాన్ సమ్మాన్ నిధి (PM-KISAN)",
            "overview": "అర్హులైన రైతు కుటుంబాలకు సంవత్సరానికి ₹6,000 ఆర్థిక సహాయం 3 విడతల్లో (విడతకు ₹2,000) నేరుగా ఆధార్ లింక్ అయిన బ్యాంకు ఖాతాలో జమ చేయబడుతుంది.",
            "benefits": [
                "ఏడాదికి ₹6,000 రూపాయల ప్రత్యక్ష నగదు బదిలీ (DBT).",
                "విత్తనాలు, ఎరువుల కొనుగోలుకు ఆర్థిక భరోసా.",
                "ఎటువంటి దళారులు లేకుండా నేరుగా ఖాతాలో జమ."
            ],
            "docs": ["ఆధార్ కార్డు", "భూమి పట్టాదారు పాస్ పుస్తకం / 1B", "ఆధార్ లింక్డ్ బ్యాంక్ ఖాతా", "మొబైల్ నంబర్"],
            "steps": [
                "pmkisan.gov.in వెబ్‌సైట్ లేదా రైతు భరోసా కేంద్రం (RBK) / CSC సెంటర్‌ను సందర్శించండి.",
                "'New Farmer Registration' ద్వారా వివరాలను నమోదు చేయండి.",
                "ఆధార్ OTP ద్వారా e-KYC ప్రక్రియను పూర్తి చేయండి."
            ]
        },
        "pmkisan": {
            "title": "పీఎం కిసాన్ మరియు రైతు సంక్షేమ నిధి",
            "overview": "రైతులకు ప్రతి 4 నెలలకు ఒకసారి ₹2,000 చొప్పున ఏడాదికి ₹6,000 అందించే కేంద్ర ప్రభుత్వ పథకం.",
            "benefits": [
                "ఏడాదికి 3 విడతలలో ₹6,000 పెట్టుబడి సాయం.",
                "చిన్న మరియు సన్నకారు రైతులకు ఎంతో ఉపయోగకరం.",
                "సులభమైన ఆన్‌లైన్ సేవలు మరియు ట్రాకింగ్."
            ],
            "docs": ["ఆధార్ కార్డు", "పట్టాదారు పాస్ పుస్తకం", "బ్యాంక్ పాస్‌బుక్", "ఫోన్ నంబర్"],
            "steps": [
                "pmkisan.gov.in పోర్టల్‌లో నమోదు చేసుకోండి.",
                "e-KYC పూర్తయిందో లేదో సరిచూసుకోండి.",
                "గ్రామ వ్యవసాయ సహాయకుడి ద్వారా ధృవీకరించబడుతుంది."
            ]
        },
        "insurance": {
            "title": "ప్రధాన మంత్రి ఫసల్ బీమా యోజన (PMFBY)",
            "overview": "ప్రకృతి వైపరీత్యాలు, అకాల వర్షాలు మరియు తెగుళ్ల వల్ల పంట నష్టపోతే రైతులకు పూర్తి బీమా రక్షణ.",
            "benefits": [
                "ఖరీఫ్ పంటలకు 2%, రబీ పంటలకు 1.5% అతి తక్కువ ప్రీమియం.",
                "పంట నష్టం జరిగిన 72 గంటల్లో సమాచారం అందించి క్లెయిమ్ పొందవచ్చు.",
                "క్లెయిమ్ మొత్తం నేరుగా బ్యాంక్ ఖాతాలో జమ."
            ],
            "docs": ["పంట సాగు ధృవీకరణ పత్రం / అడంగల్", "పట్టాదారు పాస్‌బుక్", "ఆధార్ కార్డు", "బ్యాంక్ ఖాతా వివరాలు"],
            "steps": [
                "రైతు భరోసా కేంద్రం లేదా సమీప బ్యాంక్ ద్వారా నమోదు చేసుకోండి.",
                "పంట నష్టం జరిగితే 'Crop Insurance' యాప్ లేదా 14447 టోల్‌ఫ్రీ నంబర్‌కు కాల్ చేయండి."
            ]
        },
        "kcc": {
            "title": "కిసాన్ క్రెడిట్ కార్డు (KCC) పథకం",
            "overview": "రైతులకు తక్కువ వడ్డీకే వ్యవసాయ మరియు పశుసంవర్ధక పెట్టుబడి రుణాలు అందించే పథకం.",
            "benefits": [
                "₹3 లక్షల వరకు కేవలం 4% వడ్డీకే రుణం.",
                "₹1.60 లక్షల వరకు ఎటువంటి హామీ (Collateral) అవసరం లేదు.",
                "డైరీ, కోళ్ల పెంపకం మరియు మత్స్య రంగానికి కూడా వర్తిస్తుంది."
            ],
            "docs": ["దరఖాస్తు ఫారమ్", "భూమి యాజమాన్య పత్రాలు", "ఆధార్ కార్డు", "పాస్‌పోర్ట్ సైజ్ ఫోటో"],
            "steps": [
                "మీ సమీప గ్రామీణ లేదా జాతీయ బ్యాంకును సంప్రదించండి.",
                "KCC దరఖాస్తును సమర్పించి 14 రోజుల్లో కార్డు పొందండి."
            ]
        },
        "solar": {
            "title": "పీఎం-కుసుమ్ (PM-KUSUM) సోలార్ పంపుల పథకం",
            "overview": "వ్యవసాయ బోర్లకు 60% వరకు సబ్సిడీతో సోలార్ పంపు సెట్లను ఏర్పాటు చేసుకునే పథకం.",
            "benefits": [
                "కేంద్ర, రాష్ట్ర ప్రభుత్వాల ద్వారా 60% వరకు సబ్సిడీ.",
                "పగటి పూట ఉచిత, నాణ్యమైన సౌర విద్యుత్ లభ్యత.",
                "మిగులు విద్యుత్‌ను గ్రిడ్‌కు విక్రయించి అదనపు ఆదాయం పొందవచ్చు."
            ],
            "docs": ["ఆధార్ కార్డు", "భూమి రికార్డులు (1B/పట్టా)", "బ్యాంక్ ఖాతా వివరాలు", "బోరు వివరాలు"],
            "steps": [
                "రాష్ట్ర పునరుత్పాదక ఇంధన పోర్టల్ ద్వారా దరఖాస్తు చేసుకోండి.",
                "రైతు వాటా చెల్లించి సోలార్ పంపు అమరిక పొందండి."
            ]
        },
        "machinery": {
            "title": "వ్యవసాయ యంత్రీకరణ ఉప-మిషన్ (SMAM)",
            "overview": "ట్రాక్టర్లు, పవర్ టిల్లర్లు, పంట కోత యంత్రాల కొనుగోలుపై 40% నుండి 50% వరకు రాయితీ.",
            "benefits": [
                "ట్రాక్టర్లు మరియు వ్యవసాయ పరికరాలపై 40% - 50% రాయితీ.",
                "మహిళా మరియు SC/ST రైతులకు ప్రత్యేక రాయితీలు.",
                "కూలీల కొరతను అధిగమించి దిగుబడి పెంచుకోవచ్చు."
            ],
            "docs": ["ఆధార్ కార్డు", "పట్టాదారు పాస్‌బుక్", "బ్యాంక్ ఖాతా వివరాలు", "కుల ధృవీకరణ పత్రం (వర్తిస్తే)"],
            "steps": [
                "agrimachinery.nic.in పోర్టల్‌లో రిజిస్టర్ చేసుకోండి.",
                "అనుమతి పొందిన డీలర్ నుండి పరికరాన్ని ఎంచుకోండి."
            ]
        }
    }
}

# -----------------------------------------------------------------------------
# 4. Custom CSS for Modern Agriculture-Themed UI
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Noto+Sans+Tamil:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&display=swap');

    :root {
        --primary-green: #1b5e20;
        --accent-emerald: #2e7d32;
        --light-emerald: #e8f5e9;
        --amber-gold: #ff8f00;
        --warm-sun: #fff8e1;
        --card-bg: #ffffff;
        --text-dark: #1e293b;
        --text-muted: #64748b;
        --border-color: #d1fae5;
    }

    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans Tamil', 'Noto Sans Telugu', sans-serif;
    }

    /* Top Banner Header */
    .hero-banner {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #43a047 100%);
        border-radius: 20px;
        padding: 2.2rem 1.8rem;
        color: white;
        text-align: center;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(27, 94, 32, 0.25), 0 8px 10px -6px rgba(27, 94, 32, 0.2);
        position: relative;
        overflow: hidden;
    }

    .hero-banner::before {
        content: "🌾 🚜 ☀️ 🌿 💧 🌾";
        position: absolute;
        bottom: -10px;
        right: 15px;
        font-size: 2.5rem;
        opacity: 0.15;
        letter-spacing: 8px;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        letter-spacing: -0.5px;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }

    .hero-subtitle {
        font-size: 1.05rem;
        font-weight: 400;
        opacity: 0.95;
        max-width: 750px;
        margin: 0 auto;
        color: #f1f8e9;
    }

    /* Modern Card Containers */
    .custom-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.2rem;
    }

    .voice-box-container {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
        border: 1.5px solid #86efac;
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.08);
    }

    .transcription-badge {
        background: #ffffff;
        border: 1.5px solid #22c55e;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 0.8rem;
        box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1);
    }

    .response-card {
        background: linear-gradient(180deg, #ffffff 0%, #fafffa 100%);
        border: 1.5px solid #a7f3d0;
        border-radius: 18px;
        padding: 1.8rem;
        box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.1);
        margin-top: 1.5rem;
    }

    .response-header {
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 2px solid #e8f5e9;
        padding-bottom: 0.8rem;
        margin-bottom: 1.2rem;
    }

    .response-header h3 {
        color: #1b5e20;
        margin: 0;
        font-weight: 700;
    }

    /* Section Badges */
    .tag-badge {
        display: inline-block;
        background: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Helpline Alert Box */
    .helpline-box {
        background: #f0fdf4;
        border-left: 5px solid #22c55e;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 15px;
        font-size: 0.95rem;
        color: #14532d;
    }

    /* Streamlit Button Tweaks */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.25s ease !important;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.25) !important;
    }

    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 1.6rem !important;
        }
        .hero-banner {
            padding: 1.4rem 1rem !important;
        }
        .hero-subtitle {
            font-size: 0.92rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. Session State Management
# -----------------------------------------------------------------------------
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "English"

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

if "last_transcription" not in st.session_state:
    st.session_state.last_transcription = ""

if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

if "last_recorded_file" not in st.session_state:
    st.session_state.last_recorded_file = None

if "has_searched" not in st.session_state:
    st.session_state.has_searched = False

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

# -----------------------------------------------------------------------------
# 6. Groq Whisper Transcription Helper
# -----------------------------------------------------------------------------
def transcribe_audio_with_groq(file_path: str, api_key: str) -> tuple[bool, str]:
    """
    Sends the WAV audio to Groq Whisper API using whisper-large-v3-turbo model.
    Returns (success_boolean, result_text_or_error_message).
    """
    if not api_key or api_key.strip() in ("", "your_groq_api_key_here"):
        return (
            False,
            "Groq API Key is missing. Please add your `GROQ_API_KEY` in the `.env` file or enter it in the sidebar."
        )
    
    try:
        client = Groq(api_key=api_key.strip())
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="json"
            )
            
            # Groq Python SDK returns an object with .text attribute
            if hasattr(transcription, "text"):
                text = transcription.text.strip()
            elif isinstance(transcription, dict) and "text" in transcription:
                text = transcription["text"].strip()
            else:
                text = str(transcription).strip()

            if not text:
                return False, "No speech detected in the audio recording. Please try speaking closer to the microphone."
                
            return True, text

    except Exception as exc:
        error_str = str(exc)
        if "AuthenticationError" in str(type(exc)) or "401" in error_str:
            return False, "Groq Authentication Failed: Invalid API key provided. Please verify your GROQ_API_KEY."
        elif "RateLimitError" in str(type(exc)) or "429" in error_str:
            return False, "Groq API Rate limit reached. Please wait a few seconds and try again."
        else:
            return False, f"Groq Whisper Transcription Error: {error_str}"

# -----------------------------------------------------------------------------
# 7. Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 Language / மொழி / భాష")
    lang_choice = st.selectbox(
        label="Select Application Language",
        options=["English", "தமிழ் (Tamil)", "తెలుగు (Telugu)"],
        index=["English", "தமிழ் (Tamil)", "తెలుగు (Telugu)"].index(st.session_state.selected_lang),
        label_visibility="collapsed"
    )
    if lang_choice != st.session_state.selected_lang:
        st.session_state.selected_lang = lang_choice
        st.rerun()

    lang = st.session_state.selected_lang
    loc = LOCALES[lang]

    st.markdown("---")
    st.markdown(f"#### {loc['groq_settings_title']}")
    
    # API Key input / status
    current_key = st.session_state.groq_api_key or os.getenv("GROQ_API_KEY", "")
    key_input = st.text_input(
        label="Groq API Key",
        value=current_key if current_key != "your_groq_api_key_here" else "",
        type="password",
        placeholder="gsk_...",
        help="Model: whisper-large-v3-turbo. Get a free API key at https://console.groq.com/keys"
    )
    if key_input != st.session_state.groq_api_key:
        st.session_state.groq_api_key = key_input
    
    if st.session_state.groq_api_key and st.session_state.groq_api_key != "your_groq_api_key_here":
        st.success("🟢 Groq API Key Configured")
    else:
        st.warning("⚠️ Enter Groq API Key or configure .env")

    st.markdown("---")
    st.markdown(f"#### {loc['sidebar_schemes_title']}")
    
    schemes_preview = [
        ("🌾 PM-KISAN", "₹6,000 / Year Income Support"),
        ("🛡️ PM Fasal Bima (PMFBY)", "Comprehensive Crop Insurance"),
        ("💳 Kisan Credit Card (KCC)", "4% Subsidized Farm Loan"),
        ("☀️ PM-KUSUM", "Up to 60% Solar Pump Subsidy"),
        ("🚜 Farm Mechanization (SMAM)", "40%-50% Tractor Subsidy")
    ]
    
    for name, desc in schemes_preview:
        with st.expander(name, expanded=False):
            st.caption(desc)

    st.markdown("---")
    st.markdown(f"#### ℹ️ {loc['sidebar_about']}")
    st.info(loc['sidebar_about_desc'])
    
    st.markdown(
        """
        <div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 20px;">
            🌾 <b>Farmers Welfare Scheme Assistant</b><br>
            Powered by Groq Whisper & Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------------------------------------------------------
# 8. Helper Knowledge Base Lookup Function
# -----------------------------------------------------------------------------
def get_scheme_response(query: str, language: str):
    q = query.lower()
    kb = KNOWLEDGE_BASE[language]

    if any(k in q for k in ["pmkisan", "pm-kisan", "kisan", "installment", "₹6000", "6000", "கிசான்", "தவணை", "కిసాన్", "వాయిదా"]):
        return kb["pmkisan"]
    elif any(k in q for k in ["bima", "insurance", "crop insurance", "fasal", "காப்பீடு", "பயிர் காப்பீடு", "నష్టపరిహారం", "బీమా", "పంట బీమా"]):
        return kb["insurance"]
    elif any(k in q for k in ["kcc", "credit card", "loan", "வட்டி", "கடன்", "రుణం", "క్రెడిట్ కార్డు"]):
        return kb["kcc"]
    elif any(k in q for k in ["solar", "pump", "kusum", "சூரிய", "பம்பு", "சோலார்", "సోలార్", "కుసుమ్"]):
        return kb["solar"]
    elif any(k in q for k in ["tractor", "machinery", "equipment", "டிராக்டர்", "இயந்திரம்", "ట్రాక్టర్", "యంత్రాలు"]):
        return kb["machinery"]
    else:
        return kb["default"]

# -----------------------------------------------------------------------------
# 9. Main Application Header
# -----------------------------------------------------------------------------
loc = LOCALES[st.session_state.selected_lang]

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-badge">🏛️ {loc['badge']}</div>
        <h1 class="hero-title">{loc['title']}</h1>
        <p class="hero-subtitle">{loc['subtitle']}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 10. Voice Recording Section (audio-recorder-streamlit & Groq Whisper)
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="voice-box-container">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-size: 1.3rem;">🎙️</span>
            <b style="font-size: 1.05rem; color: #166534;">{loc['voice_record_title']}</b>
            <span style="background: #dcfce7; color: #15803d; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; border: 1px solid #bbf7d0;">Groq Whisper whisper-large-v3-turbo</span>
        </div>
        <div style="font-size: 0.88rem; color: #374151; margin-bottom: 10px;">
            {loc['voice_record_caption']}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

rec_col1, rec_col2 = st.columns([1, 3])

with rec_col1:
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#dc2626",
        neutral_color="#16a34a",
        icon_name="microphone",
        icon_size="2x",
        pause_threshold=2.0
    )

with rec_col2:
    # Check if a new audio recording was captured
    if audio_bytes and audio_bytes != st.session_state.last_audio_bytes:
        st.session_state.last_audio_bytes = audio_bytes
        
        # 1. Save audio as WAV file into audio/ folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        wav_filename = f"query_{timestamp}.wav"
        wav_path = AUDIO_DIR / wav_filename

        try:
            with open(wav_path, "wb") as f:
                f.write(audio_bytes)
            st.session_state.last_recorded_file = str(wav_path)
            
            # 2. Send audio to Groq Whisper API (whisper-large-v3-turbo)
            with st.spinner(loc['voice_transcribing']):
                success, transcription_result = transcribe_audio_with_groq(
                    file_path=str(wav_path),
                    api_key=st.session_state.groq_api_key or os.getenv("GROQ_API_KEY", "")
                )

            # 3. Handle transcription result
            if success:
                st.session_state.user_query = transcription_result
                st.session_state.last_transcription = transcription_result
                st.session_state.has_searched = True
                st.rerun()
            else:
                st.error(f"❌ {transcription_result}")

        except Exception as file_err:
            st.error(f"❌ Error saving or processing audio file: {str(file_err)}")

# Show audio preview and transcription badge if available
if st.session_state.last_recorded_file and os.path.exists(st.session_state.last_recorded_file):
    with st.expander(loc['audio_playback_label'], expanded=False):
        st.audio(st.session_state.last_recorded_file, format="audio/wav")
        st.caption(f"📁 Saved file: `{st.session_state.last_recorded_file}`")

if st.session_state.last_transcription:
    st.markdown(
        f"""
        <div class="transcription-badge">
            <span style="color: #15803d; font-weight: 700; font-size: 0.9rem;">{loc['transcribed_success']}</span>
            <div style="margin-top: 4px; font-size: 1.05rem; color: #1e293b; font-weight: 500;">
                "{st.session_state.last_transcription}"
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------------------------------------------------------
# 11. Interactive Text Query Input Area
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"#### 💬 {loc['input_header']}")

# Quick suggestion chips
st.markdown(f"<span style='color: #475569; font-size: 0.88rem; font-weight: 600;'>{loc['quick_topics_label']}</span>", unsafe_allow_html=True)
chip_cols = st.columns(len(loc['quick_topics']))
for idx, topic in enumerate(loc['quick_topics']):
    with chip_cols[idx]:
        if st.button(f"📌 {topic}", key=f"chip_{idx}", use_container_width=True):
            st.session_state.user_query = topic
            st.session_state.has_searched = True

# Text Input Area
query_text = st.text_area(
    label="Farmer Query Input",
    value=st.session_state.user_query,
    placeholder=loc['input_placeholder'],
    height=90,
    label_visibility="collapsed"
)

# Action Buttons Row
btn_col1, btn_col2 = st.columns([2, 1])

with btn_col1:
    submit_clicked = st.button(loc['submit_btn'], use_container_width=True, type="primary")

with btn_col2:
    if st.button(loc['clear_btn'], use_container_width=True):
        st.session_state.user_query = ""
        st.session_state.last_transcription = ""
        st.session_state.has_searched = False
        st.session_state.last_audio_bytes = None
        st.session_state.last_recorded_file = None
        st.rerun()

# -----------------------------------------------------------------------------
# 12. Execution & Scheme Response Presentation Area
# -----------------------------------------------------------------------------
current_query = query_text.strip() or st.session_state.user_query.strip()

if submit_clicked or (st.session_state.has_searched and current_query):
    if not current_query:
        st.warning("⚠️ Please enter a question or record your voice to ask your query.")
    else:
        with st.spinner("🌾 Consulting Government Scheme Knowledge Base..."):
            time.sleep(0.3)  # Smooth transition
            result = get_scheme_response(current_query, st.session_state.selected_lang)

        st.markdown(
            f"""
            <div class="response-card">
                <div class="response-header">
                    <span style="font-size: 1.8rem;">🏛️</span>
                    <div>
                        <span class="tag-badge">Verified Scheme Details</span>
                        <h3 style="margin: 0; color: #1b5e20;">{result['title']}</h3>
                    </div>
                </div>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #334155; margin-bottom: 1.2rem;">
                    {result['overview']}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.markdown(f"##### {loc['benefits_title']}")
            for benefit in result['benefits']:
                st.markdown(f"- 🟢 **{benefit}**")

            st.markdown(f"##### {loc['docs_needed']}")
            for doc in result['docs']:
                st.markdown(f"- 📄 {doc}")

        with res_col2:
            st.markdown(f"##### {loc['steps_title']}")
            for i, step in enumerate(result['steps'], 1):
                st.markdown(f"**{i}.** {step}")

        # Helpline Banner
        st.markdown(
            f"""
            <div class="helpline-box">
                <b>{loc['helpline_title']}:</b> {loc['helpline_text']}
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------------------------------------------------------
# 13. Footer
# -----------------------------------------------------------------------------
st.markdown("---")
f_col1, f_col2 = st.columns([2, 1])
with f_col1:
    st.caption("🌾 **Farmers Welfare Scheme Assistant** | Multilingual Voice & AI Guidance Portal")
with f_col2:
    st.caption(f"🟢 {loc['status_ready']} • {datetime.date.today().strftime('%B %d, %Y')}")
