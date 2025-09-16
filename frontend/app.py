import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = f"http://{os.getenv('BACKEND_HOST', 'localhost')}:{os.getenv('BACKEND_PORT', '8000')}"

st.set_page_config(
    page_title="Document Analyzer", 
    page_icon="📄",
    layout="wide"
)

def main():
    st.title("📄 Document Categorization & Content Extraction")
    st.markdown("Upload documents to automatically categorize them and extract key information for fraud prevention.")
    
    st.sidebar.title("📊 System Info")
    
    with st.expander("ℹ️ Supported File Types", expanded=False):
        st.markdown("""
        - **PDF files** (.pdf)
        - **Image files** (.png, .jpg, .jpeg)
        
        **Categories:**
        - Invoice
        - Marketplace Listing Screenshot  
        - Chat Screenshot
        - Website Screenshot
        - Other
        """)
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="Upload a PDF or image file for analysis"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📁 File Information")
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**File Type:** {uploaded_file.type}")
            st.write(f"**File Size:** {uploaded_file.size:,} bytes")
            
            if uploaded_file.type.startswith('image/'):
                st.image(uploaded_file, caption="Uploaded Image", width=300)
        
        with col2:
            if st.button("🔍 Analyze Document", type="primary"):
                with st.spinner("Processing document..."):
                    result = process_document(uploaded_file)
                    
                if result:
                    display_results(result)
    
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("🔧 API Health"):
        if st.button("Check Backend Status"):
            check_backend_health()

def process_document(uploaded_file) -> Optional[Dict[str, Any]]:
    try:
        files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
        
        response = requests.post(
            f"{BACKEND_URL}/process-document/",
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server. Please make sure it's running.")
        return None
    except Exception as e:
        st.error(f"❌ Error processing document: {str(e)}")
        return None

def display_results(result: Dict[str, Any]):
    st.subheader("📊 Analysis Results")
    
    if result.get("error"):
        st.error(f"❌ Processing Error: {result['error']}")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Category", 
            value=result["category"].replace("_", " ").title(),
            help="Predicted document category"
        )
    
    with col2:
        confidence = result["confidence"]
        confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.5 else "🔴"
        st.metric(
            label="Confidence", 
            value=f"{confidence:.1%}",
            help=f"Model confidence in prediction {confidence_color}"
        )
    
    with col3:
        st.metric(
            label="Processing Time", 
            value=f"{result['processing_time']:.2f}s",
            help="Time taken to process document"
        )
    
    st.markdown("---")
    
    extracted = result.get("extracted_content", {})
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Extracted Text", "🏷️ Key Entities", "📅 Dates & Metadata", "⚠️ Risk Analysis"])
    
    with tab1:
        text_content = extracted.get("text", "")
        if text_content:
            st.text_area("Extracted/Transcribed Text", text_content, height=200)
        else:
            st.info("No text content extracted or available.")
    
    with tab2:
        entities = extracted.get("key_entities", {})
        if entities:
            for entity_type, values in entities.items():
                if values:
                    st.write(f"**{entity_type.replace('_', ' ').title()}:**")
                    for value in values:
                        st.write(f"- {value}")
        else:
            st.info("No key entities extracted.")
    
    with tab3:
        col_dates, col_meta = st.columns(2)
        
        with col_dates:
            st.write("**📅 Dates:**")
            dates = extracted.get("dates", [])
            if dates:
                for date in dates:
                    st.write(f"- {date}")
            else:
                st.info("No dates found.")
        
        with col_meta:
            st.write("**📋 Metadata:**")
            metadata = extracted.get("metadata", {})
            if metadata:
                for key, value in metadata.items():
                    if key != "fraud_risk_indicators":
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    with tab4:
        metadata = extracted.get("metadata", {})
        risk_indicators = metadata.get("fraud_risk_indicators", [])
        
        if risk_indicators:
            st.warning("⚠️ **Potential Risk Indicators Found:**")
            for indicator in risk_indicators:
                st.write(f"- {indicator}")
        else:
            st.success("✅ No obvious fraud risk indicators detected.")
        
        urgency = metadata.get("urgency_indicators", [])
        if urgency:
            st.info("🚨 **Urgency Indicators:**")
            for item in urgency:
                st.write(f"- {item}")
    
    st.markdown("---")
    
    with st.expander("🔍 Raw JSON Output"):
        st.json(result)

def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ Backend is healthy")
        else:
            st.sidebar.error(f"❌ Backend returned {response.status_code}")
    except:
        st.sidebar.error("❌ Backend is unreachable")

if __name__ == "__main__":
    main()