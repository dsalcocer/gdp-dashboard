import streamlit as st
import pandas as pd
import re
from io import StringIO

# Set page configuration
st.set_page_config(
    page_title="Text Classification Tool",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for dictionaries
if 'dictionaries' not in st.session_state:
    st.session_state.dictionaries = {
        'urgency_marketing': {
            'limited', 'limited time', 'limited run', 'limited edition', 'order now',
            'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
            'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
            'expires soon', 'final hours', 'almost gone'
        },
        'exclusive_marketing': {
            'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
            'members only', 'vip', 'special access', 'invitation only',
            'premium', 'privileged', 'limited access', 'select customers',
            'insider', 'private sale', 'early access'
        }
    }

def classify_text(text, dictionaries):
    """Classify text based on provided dictionaries"""
    text_lower = str(text).lower()
    classifications = []
    
    for category, keywords in dictionaries.items():
        for keyword in keywords:
            if keyword in text_lower:
                classifications.append(category)
                break
    
    return ', '.join(classifications) if classifications else 'unclassified'

def main():
    st.title("📊 Text Classification Tool")
    st.markdown("Upload your dataset and classify text using customizable keyword dictionaries.")
    
    # Sidebar for dictionary management
    st.sidebar.header("🔧 Dictionary Management")
    
    # Dictionary modification section
    st.sidebar.subheader("Current Categories")
    
    # Display and allow editing of existing dictionaries
    for category in list(st.session_state.dictionaries.keys()):
        with st.sidebar.expander(f"📝 {category}"):
            # Display current keywords
            current_keywords = list(st.session_state.dictionaries[category])
            keywords_text = '\n'.join(current_keywords)
            
            # Text area for editing keywords
            new_keywords = st.text_area(
                f"Keywords for {category}:",
                value=keywords_text,
                height=100,
                key=f"keywords_{category}"
            )
            
            # Update button
            if st.button(f"Update {category}", key=f"update_{category}"):
                # Parse the new keywords
                updated_keywords = set([kw.strip() for kw in new_keywords.split('\n') if kw.strip()])
                st.session_state.dictionaries[category] = updated_keywords
                st.success(f"Updated {category}!")
            
            # Delete category button
            if st.button(f"Delete {category}", key=f"delete_{category}"):
                del st.session_state.dictionaries[category]
                st.success(f"Deleted {category}!")
                st.rerun()
    
    # Add new category section
    st.sidebar.subheader("➕ Add New Category")
    new_category_name = st.sidebar.text_input("Category Name:")
    new_category_keywords = st.sidebar.text_area("Keywords (one per line):", height=80)
    
    if st.sidebar.button("Add Category"):
        if new_category_name and new_category_keywords:
            keywords_set = set([kw.strip() for kw in new_category_keywords.split('\n') if kw.strip()])
            st.session_state.dictionaries[new_category_name] = keywords_set
            st.sidebar.success(f"Added category: {new_category_name}")
            st.rerun()
        else:
            st.sidebar.error("Please provide both category name and keywords.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Data Upload & Processing")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV file with a column containing text to classify"
        )
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                st.success(f"File uploaded successfully! Shape: {df.shape}")
                
                # Column selection
                text_column = st.selectbox(
                    "Select the column containing text to classify:",
                    options=df.columns.tolist(),
                    help="Choose which column contains the text you want to classify"
                )
                
                # Preview data
                st.subheader("📋 Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Classification button
                if st.button("🚀 Classify Text", type="primary"):
                    if not st.session_state.dictionaries:
                        st.error("Please add at least one category with keywords before classifying.")
                    else:
                        # Apply classification
                        with st.spinner("Classifying text..."):
                            df['classification'] = df[text_column].apply(
                                lambda x: classify_text(x, st.session_state.dictionaries)
                            )
                        
                        st.success("Classification completed!")
                        
                        # Display results
                        st.subheader("📊 Classification Results")
                        
                        # Summary statistics
                        col_stats1, col_stats2, col_stats3 = st.columns(3)
                        
                        with col_stats1:
                            st.metric("Total Statements", len(df))
                        
                        with col_stats2:
                            classified_count = len(df[df['classification'] != 'unclassified'])
                            st.metric("Classified", classified_count)
                        
                        with col_stats3:
                            unclassified_count = len(df[df['classification'] == 'unclassified'])
                            st.metric("Unclassified", unclassified_count)
                        
                        # Classification distribution
                        st.subheader("📈 Classification Distribution")
                        classification_counts = df['classification'].value_counts()
                        st.bar_chart(classification_counts)
                        
                        # Detailed results table
                        st.subheader("🔍 Detailed Results")
                        
                        # Filter options
                        filter_option = st.selectbox(
                            "Filter results:",
                            options=['All', 'Classified Only', 'Unclassified Only'] + 
                                   [cat for cat in st.session_state.dictionaries.keys()]
                        )
                        
                        # Apply filter
                        if filter_option == 'All':
                            filtered_df = df
                        elif filter_option == 'Classified Only':
                            filtered_df = df[df['classification'] != 'unclassified']
                        elif filter_option == 'Unclassified Only':
                            filtered_df = df[df['classification'] == 'unclassified']
                        else:
                            filtered_df = df[df['classification'].str.contains(filter_option, na=False)]
                        
                        st.dataframe(
                            filtered_df[[text_column, 'classification']], 
                            use_container_width=True,
                            height=400
                        )
                        
                        # Download classified data
                        csv_buffer = StringIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()
                        
                        st.download_button(
                            label="📥 Download Classified Data",
                            data=csv_data,
                            file_name="classified_data.csv",
                            mime="text/csv",
                            type="secondary"
                        )
                        
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please make sure your file is a valid CSV format.")
    
    with col2:
        st.header("ℹ️ Current Dictionary")
        
        if st.session_state.dictionaries:
            for category, keywords in st.session_state.dictionaries.items():
                with st.expander(f"📂 {category} ({len(keywords)} keywords)"):
                    for keyword in sorted(keywords):
                        st.write(f"• {keyword}")
        else:
            st.info("No categories defined. Add some categories using the sidebar.")
        
        # Instructions
        st.header("📖 Instructions")
        st.markdown("""
        **How to use this tool:**
        
        1. **Upload Data**: Upload a CSV file with text to classify
        2. **Select Column**: Choose which column contains the text
        3. **Modify Dictionaries**: Use the sidebar to:
           - Edit existing categories
           - Add new categories
           - Delete unwanted categories
        4. **Classify**: Click the classify button to process your data
        5. **Review Results**: Examine the classification results and download
        
        **Dictionary Format:**
        - Each category contains keywords/phrases
        - Keywords are case-insensitive
        - Put each keyword on a new line
        - Text is classified if it contains any keyword from a category
        """)

if __name__ == "__main__":
    main()
