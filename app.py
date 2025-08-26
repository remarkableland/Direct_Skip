import streamlit as st
import pandas as pd
import io
from typing import Dict, Optional

# Column mapping based on MAP.xlsx
COLUMN_MAPPING = {
    "OWNER_1_FIRST": "First Name",
    "OWNER_1_LAST": "Last Name", 
    "OWNER_ADDRESS": "Mailing Address",
    "OWNER_CITY": "Mailing City",
    "OWNER_STATE": "Mailing State",
    "OWNER_ZIP": "Mailing Zip",
    "PROP_ADDRESS": "Property Address",
    "PROP_CITY": "Property City",
    "PROP_STATE": "Property State",
    "PROP_ZIP": "Property Zip"
}

def process_csv(df: pd.DataFrame, property_ref_code: str) -> pd.DataFrame:
    """
    Process the input CSV by mapping columns and adding custom field.
    
    Args:
        df: Input DataFrame
        property_ref_code: Custom property reference code
        
    Returns:
        Processed DataFrame with mapped columns
    """
    # Create new DataFrame with only the columns we want to keep
    mapped_df = pd.DataFrame()
    
    # Map existing columns according to the mapping
    for source_col, target_col in COLUMN_MAPPING.items():
        if source_col in df.columns:
            mapped_df[target_col] = df[source_col]
        else:
            # Create empty column if source column doesn't exist
            mapped_df[target_col] = ""
            st.warning(f"Column '{source_col}' not found in input file. Created empty '{target_col}' column.")
    
    # Add the custom field
    mapped_df["Custom Field 1"] = property_ref_code
    
    return mapped_df

def validate_input_file(df: pd.DataFrame) -> bool:
    """
    Validate that the input CSV has expected structure.
    
    Args:
        df: Input DataFrame
        
    Returns:
        True if valid, False otherwise
    """
    expected_columns = list(COLUMN_MAPPING.keys())
    missing_columns = [col for col in expected_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing expected columns: {missing_columns}")
        return False
    
    return True

def main():
    st.title("🏠 Property CSV Mapper")
    st.markdown("---")
    
    st.markdown("""
    This tool maps property search CSV files to a standardized format based on your mapping configuration.
    
    **Mapping Configuration:**
    - OWNER_1_FIRST → First Name
    - OWNER_1_LAST → Last Name  
    - OWNER_ADDRESS → Mailing Address
    - OWNER_CITY → Mailing City
    - OWNER_STATE → Mailing State
    - OWNER_ZIP → Mailing Zip
    - PROP_ADDRESS → Property Address
    - PROP_CITY → Property City
    - PROP_STATE → Property State
    - PROP_ZIP → Property Zip
    """)
    
    st.markdown("---")
    
    # File upload section
    st.header("📁 Upload Property Search CSV")
    uploaded_file = st.file_uploader(
        "Choose your property search CSV file",
        type=['csv'],
        help="Upload the CSV file containing property data to be mapped"
    )
    
    # Property reference code input
    st.header("🏷️ Property Reference Code")
    property_ref_code = st.text_input(
        "Enter Property Reference Code",
        placeholder="e.g. PROJ-2025-001",
        help="This code will be added to 'Custom Field 1' for all records"
    )
    
    if uploaded_file is not None and property_ref_code:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
            
            # Show preview of input data
            with st.expander("📊 Preview Input Data (First 5 rows)"):
                st.dataframe(df.head())
            
            # Validate input
            if validate_input_file(df):
                # Process the CSV
                mapped_df = process_csv(df, property_ref_code)
                
                st.header("✨ Processing Results")
                st.success(f"🎉 Successfully mapped {len(mapped_df)} records!")
                
                # Show preview of output data
                with st.expander("📋 Preview Mapped Data (First 5 rows)"):
                    st.dataframe(mapped_df.head())
                
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Input Columns", len(df.columns))
                with col2:
                    st.metric("Output Columns", len(mapped_df.columns))
                with col3:
                    st.metric("Records Processed", len(mapped_df))
                
                # Download section
                st.header("💾 Download Mapped CSV")
                
                # Convert DataFrame to CSV
                csv_buffer = io.StringIO()
                mapped_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                # Generate filename
                original_filename = uploaded_file.name.rsplit('.', 1)[0]
                output_filename = f"{original_filename}_mapped.csv"
                
                st.download_button(
                    label="📥 Download Mapped CSV",
                    data=csv_data,
                    file_name=output_filename,
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Show mapping summary
                with st.expander("🔍 Column Mapping Details"):
                    mapping_df = pd.DataFrame([
                        {"Source Column": k, "Target Column": v, "Status": "✅ Found" if k in df.columns else "❌ Missing"}
                        for k, v in COLUMN_MAPPING.items()
                    ])
                    st.dataframe(mapping_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please ensure your CSV file is properly formatted and contains the expected columns.")
    
    elif uploaded_file is not None and not property_ref_code:
        st.warning("⚠️ Please enter a Property Reference Code to continue.")
    
    elif uploaded_file is None and property_ref_code:
        st.warning("⚠️ Please upload a CSV file to continue.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>Property CSV Mapper v1.0 | Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
