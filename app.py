import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from typing import Dict, Optional, Tuple

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

def deduplicate_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Remove duplicate records based on owner name and mailing address combination.
    
    Args:
        df: Input DataFrame with mapped columns
        
    Returns:
        Tuple of (deduplicated DataFrame, number of duplicates removed)
    """
    initial_count = len(df)
    
    # Create a composite key for deduplication based on:
    # - Owner full name (First Name + Last Name)
    # - Mailing Address
    # This combination should uniquely identify a unique owner-mailing address relationship
    
    # Fill NaN values with empty strings for consistent comparison
    df_clean = df.fillna('')
    
    # Create composite key columns for deduplication
    df_clean['_dedup_owner'] = (df_clean['First Name'].str.strip().str.upper() + 
                               ' ' + df_clean['Last Name'].str.strip().str.upper()).str.strip()
    
    df_clean['_dedup_mailing'] = (df_clean['Mailing Address'].str.strip().str.upper() + 
                                 ' ' + df_clean['Mailing City'].str.strip().str.upper() + 
                                 ' ' + df_clean['Mailing State'].str.strip().str.upper()).str.strip()
    
    # Remove duplicates based on the composite key
    # Keep the first occurrence of each unique combination
    df_deduped = df_clean.drop_duplicates(subset=['_dedup_owner', '_dedup_mailing'], keep='first')
    
    # Remove the temporary deduplication columns
    df_deduped = df_deduped.drop(columns=['_dedup_owner', '_dedup_mailing'])
    
    # Calculate number of duplicates removed
    duplicates_removed = initial_count - len(df_deduped)
    
    return df_deduped, duplicates_removed

def process_csv(df: pd.DataFrame, property_ref_code: str) -> Tuple[pd.DataFrame, int]:
    """
    Process the input CSV by mapping columns, adding custom field, and deduplicating.
    
    Args:
        df: Input DataFrame
        property_ref_code: Custom property reference code
        
    Returns:
        Tuple of (processed DataFrame with mapped columns, number of duplicates removed)
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
    
    # Deduplicate the data
    deduplicated_df, duplicates_removed = deduplicate_dataframe(mapped_df)
    
    return deduplicated_df, duplicates_removed

def generate_output_filename(property_ref_code: str) -> str:
    """
    Generate output filename in format: YYYYMMDD_CustomField_DirectSkip_Import.csv
    
    Args:
        property_ref_code: Property reference code from user input
        
    Returns:
        Generated filename string
    """
    # Get current date in YYYYMMDD format
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Clean the property reference code for filename (remove invalid characters)
    if property_ref_code:
        custom_field = re.sub(r'[<>:"/\\|?*]', '', str(property_ref_code))
        custom_field = custom_field.replace(' ', '_')  # Replace spaces with underscores
        filename = f"{date_str}_{custom_field}_DirectSkip_Import.csv"
    else:
        filename = f"{date_str}_DirectSkip_Import.csv"
    
    return filename

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
    **Features include column mapping, deduplication, and custom field addition.**
    
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
    
    **Deduplication Logic:**
    Removes duplicates based on owner name + mailing address combination.
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
                # Process the CSV (includes mapping, custom field, and deduplication)
                mapped_df, duplicates_removed = process_csv(df, property_ref_code)
                
                st.header("✨ Processing Results")
                
                # Show deduplication results
                if duplicates_removed > 0:
                    st.warning(f"🔄 **Deduplication**: Removed {duplicates_removed} duplicate records")
                else:
                    st.info("✅ **Deduplication**: No duplicates found")
                
                st.success(f"🎉 Successfully processed {len(mapped_df)} unique records!")
                
                # Show preview of output data
                with st.expander("📋 Preview Mapped Data (First 5 rows)"):
                    st.dataframe(mapped_df.head())
                
                # Summary statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Input Records", len(df))
                with col2:
                    st.metric("Duplicates Removed", duplicates_removed)
                with col3:
                    st.metric("Final Records", len(mapped_df))
                with col4:
                    st.metric("Output Columns", len(mapped_df.columns))
                
                # Processing summary
                st.info(f"""
                📋 **Processing Summary:**
                • Original records: {len(df):,}
                • Duplicates removed: {duplicates_removed:,}
                • Final unique records: {len(mapped_df):,}
                • Deduplication rate: {(duplicates_removed/len(df)*100):.1f}%
                """)
                
                # Download section
                st.header("💾 Download Mapped CSV")
                
                # Convert DataFrame to CSV
                csv_buffer = io.StringIO()
                mapped_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                # Generate filename using date + property reference code + "DirectSkip_Import"
                output_filename = generate_output_filename(property_ref_code)
                
                st.download_button(
                    label="📥 Download Mapped CSV",
                    data=csv_data,
                    file_name=output_filename,
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Show filename info
                st.info(f"📁 **Filename**: `{output_filename}`")
                
                # Show mapping summary
                with st.expander("🔍 Column Mapping Details"):
                    mapping_df = pd.DataFrame([
                        {"Source Column": k, "Target Column": v, "Status": "✅ Found" if k in df.columns else "❌ Missing"}
                        for k, v in COLUMN_MAPPING.items()
                    ])
                    st.dataframe(mapping_df, use_container_width=True)
                
                # Show deduplication details
                with st.expander("🔄 Deduplication Details"):
                    st.markdown("""
                    **Deduplication Method:**
                    - Creates composite key from: Owner Name + Mailing Address + Mailing City + Mailing State
                    - Converts text to uppercase for case-insensitive comparison
                    - Keeps the first occurrence of each unique combination
                    - Removes temporary matching columns after processing
                    
                    **Why This Works:**
                    - Same owner + same mailing address = likely duplicate
                    - Accounts for slight formatting differences in text
                    - Preserves data integrity by keeping complete first occurrence
                    - Focuses on unique recipients rather than unique properties
                    """)
        
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
        <small>Property CSV Mapper v1.1 | Built with Streamlit | Now with Deduplication</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
