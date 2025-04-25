import os
import re
import tempfile
import streamlit as st
from dotenv import load_dotenv
from typing import List, Union, Literal
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from fpdf import FPDF

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- Pydantic Schema ---------------- #

class PrimaryMaterials(BaseModel):
    materials: List[str]
    standards: List[str]
    

class MechanicalProperties(BaseModel):
    tensile_strength: str
    compressive_strength: str
    shear_strength: str
    elasticity: str
    fatigue_resistance: str
    testing_standards: List[str]

class DegradationProfile(BaseModel):
    biodegradable: bool
    absorption_time: str
    breakdown_mechanism: str
    by_products: str
    standards: List[str]

class DimensionIntegrity(BaseModel):
    physical_dimensions: str
    surface_finish: str
    load_capacity: str
    durability: str
    standards: List[str]

class PerformanceCriteria(BaseModel):
    retention_strength: str
    failure_threshold: str
    wear_resistance: str
    shelf_life: str
    standards: List[str]

class FunctionalPerformance(BaseModel):
    function: str
    properties: List[str]
    performance_standards: List[str]
    notes: str

class MedicalDeviceReport(BaseModel):
    primary_materials: PrimaryMaterials = Field(alias="Primary Materials")
    mechanical_properties: MechanicalProperties = Field(alias="Mechanical Properties")
    degradation_profile: DegradationProfile = Field(alias="Degradation Profile")
    dimension_integrity: DimensionIntegrity = Field(alias="Dimension and Structural Integrity")
    performance_criteria: PerformanceCriteria = Field(alias="Performance Criteria")
    functional_and_performance_characteristics: FunctionalPerformance = Field(alias="Functional and Performance Characteristics")

# ---------------- LangChain Parser ---------------- #

parser = PydanticOutputParser(pydantic_object=MedicalDeviceReport)

# ---------------- LLM Init ---------------- #

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.2,
    api_key=GROQ_API_KEY
)

# ---------------- Streamlit Setup ---------------- #

st.set_page_config(page_title="Medical Device Report Generator", page_icon="🩺")
st.title("🩺 Medical Device Report Generator")
st.markdown("Enter the device name to generate a **validated and structured** technical report.")

device_name = st.text_input("**Device Name**", placeholder="e.g., Hip Implant")
generate_button = st.button("🚀 Generate Report")

# ---------------- Prompt Setup ---------------- #

system_message = SystemMessage(content=f"""
You are a regulatory documentation assistant. You will generate a structured medical device report that matches this Pydantic schema exactly:

{parser.get_format_instructions()}

Include all 6 sections:
1. Primary Materials  
2. Mechanical Properties  
3. Degradation Profile  
4. Dimension and Structural Integrity  
5. Functional and Performance Characteristics  
6. Performance Criteria

Respond only with valid JSON. No markdown or commentary.
""")

human_message_template = "Device: {device_name}"

# ---------------- Display Helper ---------------- #

def render_section(title, data):
    st.markdown(f"### 📄 {title}")
    for key, value in data.model_dump().items():
        label = key.replace('_', ' ').capitalize()
        if isinstance(value, list):
            st.markdown(f"**{label}:**")
            for item in value:
                st.markdown(f"- {item}")
        else:
            st.markdown(f"**{label}:** {value}")

# ---------------- Enhanced PDF Generator ---------------- #

class PDFReport(FPDF):
    def header(self):
        # Header with a title and styled text
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, "Medical Device Report", border=0, ln=True, align='C')
        self.ln(5)
    
    def footer(self):
        # Footer with page numbers
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def add_section(self, title, section):
        # Section title with a light blue background
        self.set_font("Arial", "B", 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(2)
        self.set_font("Arial", "", 12)
        # Add section content
        for key, value in section.model_dump().items():
            label = key.replace('_', ' ').capitalize()
            if isinstance(value, list):
                self.cell(0, 8, f"{label}:", ln=True)
                for item in value:
                    self.set_x(self.l_margin + 10)  # indent bullet points
                    self.multi_cell(0, 8, f"- {item}")
            else:
                self.multi_cell(0, 8, f"{label}: {value}")
        self.ln(5)
        # Draw a horizontal line separator
        self.set_draw_color(0, 0, 0)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

def generate_pdf(report: MedicalDeviceReport, device_name: str) -> str:
    pdf = PDFReport()
    pdf.add_page()
    
    # Device name header
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Device Name: {device_name}", ln=True)
    pdf.ln(5)
    
    # Add all report sections with enhanced styling
    pdf.add_section("Primary Materials", report.primary_materials)
    pdf.add_section("Mechanical Properties", report.mechanical_properties)
    pdf.add_section("Degradation Profile", report.degradation_profile)
    pdf.add_section("Dimension and Structural Integrity", report.dimension_integrity)
    pdf.add_section("Performance Criteria", report.performance_criteria)
    pdf.add_section("Functional & Performance Characteristics", report.functional_and_performance_characteristics)
    
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', device_name)
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{safe_name}.pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# ---------------- Run Agent + Display ---------------- #

if generate_button:
    if not device_name:
        st.warning("Please enter a device name.")
    else:
        with st.spinner("Generating structured report..."):
            prompt = ChatPromptTemplate.from_messages([
                system_message,
                HumanMessage(content=human_message_template.format(device_name=device_name))
            ])
            try:
                messages = prompt.format_messages()
                response = llm(messages)
                content = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
                report = parser.parse(content)
 
                st.success("✅ Valid structured report generated!")
 
                render_section("Primary Materials", report.primary_materials)
                render_section("Mechanical Properties", report.mechanical_properties)
                render_section("Degradation Profile", report.degradation_profile)
                render_section("Dimension and Structural Integrity", report.dimension_integrity)
                render_section("Performance Criteria", report.performance_criteria)
                render_section("Functional and Performance Characteristics", report.functional_and_performance_characteristics)
 
                with st.expander("📦 Full JSON Output"):
                    st.code(report.model_dump_json(indent=2), language="json")
 
                pdf_path = generate_pdf(report, device_name)
                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download Report as PDF", f, file_name=f"{device_name}_report.pdf", mime="application/pdf")
 
            except Exception as e:
                st.error("⚠️ Failed to parse structured response.")
                st.text_area("Raw Output", response.content)
                st.exception(e)
