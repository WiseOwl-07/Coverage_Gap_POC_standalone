"""Standalone Streamlit App for Coverage Gap Detection.

This version runs directly on Streamlit Cloud without needing a separate FastAPI backend.
All agent logic is integrated directly into the Streamlit app.
"""
import streamlit as st
import json
import os
from pathlib import Path

# Import agent components
from app.agents.orchestrator import Orchestrator
from app.utils.policy_parser import parse_policy_file
from app.core.models import RiskSeverity

# Page configuration
st.set_page_config(
    page_title="Coverage Gap Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4788;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .gap-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid;
    }
    .gap-high {
        background-color: #ffe6e6;
        border-color: #dc3545;
    }
    .gap-medium {
        background-color: #fff3cd;
        border-color: #ffc107;
    }
    .gap-low {
        background-color: #d1ecf1;
        border-color: #17a2b8;
    }
    .severity-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .severity-high {
        background-color: #dc3545;
        color: white;
    }
    .severity-medium {
        background-color: #ffc107;
        color: #333;
    }
    .severity-low {
        background-color: #17a2b8;
        color: white;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f4788;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_orchestrator():
    """Create and cache the orchestrator instance."""
    return Orchestrator()


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">🛡️ Coverage Gap Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered P&C Insurance Analysis</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 About")
        st.info("""
        This tool uses **Agentic AI** to analyze insurance policies and identify coverage gaps.
        
        **How it works:**
        1. Upload policy data (JSON)
        2. AI agents analyze coverage
        3. View gaps and recommendations
        
        **Agents:**
        - 📊 Policy Analyzer
        - ⚠️ Risk Assessor
        - ✅ Best Practice Checker
        - 🎯 Gap Reasoner
        """)
        
        st.header("📁 Sample Policies")
        sample_policies = {
            "High Net Worth (Miami)": "app/data/sample_policies/high_networth_miami.json",
            "San Francisco Home": "app/data/sample_policies/san_francisco_home.json",
            "Well Covered (Chicago)": "app/data/sample_policies/well_covered_chicago.json"
        }
        
        selected_sample = st.selectbox(
            "Load sample policy:",
            ["None"] + list(sample_policies.keys())
        )
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Policy Data")
        
        policy_data = None
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload JSON policy file",
            type=["json"],
            help="Upload a policy JSON file for analysis"
        )
        
        if uploaded_file:
            policy_data = uploaded_file.read().decode('utf-8')
            st.success("✅ Policy file loaded")
        
        # Load sample policy
        elif selected_sample != "None":
            sample_path = Path(sample_policies[selected_sample])
            if sample_path.exists():
                policy_data = sample_path.read_text()
                st.success(f"✅ Loaded sample: {selected_sample}")
        
        # Show policy preview
        if policy_data:
            with st.expander("📄 View Policy Data"):
                policy_json = json.loads(policy_data)
                st.json(policy_json)
    
    with col2:
        st.subheader("🚀 Analysis")
        
        if policy_data:
            if st.button("🔍 Analyze Coverage", type="primary", use_container_width=True):
                with st.spinner("🤖 AI agents analyzing policy..."):
                    try:
                        # Parse policy
                        policy_input = parse_policy_file(file_content=policy_data)
                        
                        # Get cached orchestrator
                        orchestrator = get_orchestrator()
                        
                        # Run analysis
                        result = orchestrator.analyze_policy(policy_input)
                        
                        # Store in session state
                        st.session_state['analysis_result'] = {
                            'policy_number': result.policy_number,
                            'customer_name': result.customer_name,
                            'total_gaps_found': result.total_gaps_found,
                            'coverage_gaps': [
                                {
                                    'gap_type': gap.gap_type.value,
                                    'severity': gap.severity.value,
                                    'title': gap.title,
                                    'explanation': gap.explanation,
                                    'recommendation': gap.recommendation,
                                    'estimated_annual_premium': gap.estimated_annual_premium,
                                    'risk_factors': gap.risk_factors
                                }
                                for gap in result.coverage_gaps
                            ],
                            'total_estimated_premium_impact': result.total_estimated_premium_impact,
                            'analysis_summary': result.analysis_summary
                        }
                        
                        st.success("✅ Analysis complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)
        else:
            st.info("📥 Upload a policy file or select a sample to begin")
    
    # Display results
    if 'analysis_result' in st.session_state:
        result = st.session_state['analysis_result']
        
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result['total_gaps_found']}</div>
                <div class="metric-label">Coverage Gaps</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            high_priority = sum(1 for gap in result['coverage_gaps'] if gap['severity'] == 'High')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{high_priority}</div>
                <div class="metric-label">High Priority</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${result['total_estimated_premium_impact']:,.0f}</div>
                <div class="metric-label">Annual Premium Impact</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Analysis summary
        st.info(f"**Summary:** {result['analysis_summary']}")
        
        # Coverage gaps
        if result['coverage_gaps']:
            st.subheader("🎯 Identified Coverage Gaps")
            
            for gap in result['coverage_gaps']:
                severity = gap['severity']
                severity_class = f"severity-{severity.lower()}"
                gap_class = f"gap-{severity.lower()}"
                
                st.markdown(f"""
                <div class="gap-card {gap_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0;">{gap['title']}</h3>
                        <span class="severity-badge {severity_class}">{severity} Risk</span>
                    </div>
                    <p><strong>Why this matters:</strong> {gap['explanation']}</p>
                    <p><strong>Recommendation:</strong> {gap['recommendation']}</p>
                    {f"<p><strong>Estimated Premium:</strong> ${gap['estimated_annual_premium']:,.2f}/year</p>" if gap['estimated_annual_premium'] else ""}
                    {f"<p><strong>Risk Factors:</strong> {', '.join(gap['risk_factors'])}</p>" if gap['risk_factors'] else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No significant coverage gaps identified. Your policy provides adequate protection!")
        
        # Download report
        st.markdown("---")
        st.download_button(
            label="📥 Download Analysis Report (JSON)",
            data=json.dumps(result, indent=2),
            file_name=f"coverage_analysis_{result['policy_number']}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()
