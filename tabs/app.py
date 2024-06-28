import streamlit as st
import pandas as pd
import os
import tempfile
import shutil

def load_template_headers(file_path):
    # Check if the file exists, create it if it doesn't
    if not os.path.exists(file_path):
        initial_df = pd.DataFrame(columns=["Template Header", "Possible Headers"])
        initial_df.to_excel(file_path, index=False)
        return []

    # Load the existing mappings
    existing_df = pd.read_excel(file_path)

    # Extract unique template headers from the existing DataFrame
    return existing_df["Template Header"].unique().tolist()

def save_updated_mappings(header_mappings, file_path):
    # Create a DataFrame for the updated mappings
    updated_mappings = []
    for header, possibles in header_mappings.items():
        concatenated_possibles = ", ".join(possibles)
        updated_mappings.append((header, concatenated_possibles))
    updated_df = pd.DataFrame(updated_mappings, columns=["Template Header", "Possible Headers"])

    # Write to a temporary file first to avoid permission issues
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    try:
        updated_df.to_excel(temp_file.name, index=False)
        temp_file.close()
        shutil.move(temp_file.name, file_path)
        return True
    except PermissionError:
        return False
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

def run():
    # Path to the existing Excel file
    file_path = "header_mappings.xlsx"

    # Load the template headers
    if 'template_headers' not in st.session_state:
        st.session_state.template_headers = load_template_headers(file_path)

    # Load the existing mappings
    existing_df = pd.read_excel(file_path)

    # Create a dictionary to hold the mappings
    header_mappings = {header: [] for header in st.session_state.template_headers}

    # Populate the dictionary with existing mappings
    for index, row in existing_df.iterrows():
        if row["Template Header"] in header_mappings and pd.notna(row["Possible Headers"]):
            header_mappings[row["Template Header"]].extend(row["Possible Headers"].split(", "))

    st.title("Header Mapping Input Tool")

    st.markdown("""
    ### Instructions:
    1. Select a template header from the dropdown menu.
    2. Enter a possible header that corresponds to the selected template header.
    3. Click 'Update Excel File' to save the new mapping.
    4. To add a new template header, click the '+ Add' button, enter the new header name, and click 'Save New Header'.
    """)

    # Check if adding a new template header
    if 'adding_new_header' not in st.session_state:
        st.session_state.adding_new_header = False

    if st.session_state.adding_new_header:
        # Input for the new template header
        new_header = st.text_input("Enter new template header")
        if st.button("Save New Header"):
            try:
                if not new_header:
                    st.toast("Please put a value ⛔")
                elif new_header in st.session_state.template_headers:
                    st.toast("Header already exists ❗")
                else:
                    st.session_state.template_headers.append(new_header)
                    # st.session_state.template_headers.sort()
                    st.session_state.adding_new_header = False
                    st.toast("New header added successfully! ✔️")
                    st.experimental_rerun()
            except Exception as e:
                st.toast(f"Error: {str(e)}")
    else:
        # Create columns for dropdown and button
        col1, col2 = st.columns([4, 0.3])

        with col1:
            # Dropdown to select a template header
            selected_header = st.selectbox("Select a Template Header", st.session_state.template_headers)
        
        with col2:
            # Adding a bit of margin to align button with the dropdown
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            # Button to add a new template header
            if st.button("➕"):
                st.session_state.adding_new_header = True
                st.experimental_rerun()
        
        # Text input for the possible header
        possible_header = st.text_input(f"Enter a possible header for '{selected_header}'")

        # Create two columns for buttons
        col3, col4 = st.columns([1, 1])

        with col3:
            # Button to update the Excel file
            if st.button("Update Excel File"):
                try:
                    if possible_header:
                        # Append the new possible header to the selected header
                        if possible_header not in header_mappings[selected_header]:
                            header_mappings[selected_header].append(possible_header)
                        
                        # Save the updated mappings
                        if save_updated_mappings(header_mappings, file_path):
                            st.toast("Excel file has been updated successfully! ✔️")
                        else:
                            st.toast("Permission denied: The file may be open in another application. 🚫")
                    else:
                        st.toast("Please enter a possible header before updating. 😕")
                except Exception as e:
                    st.toast(f"Error: {str(e)} 🥺")
        
    # Display the updated mappings in a table format
    st.markdown("## Current Header Mappings")
    st.markdown("The table below shows the current mappings of template headers to their possible headers:")

    # Prepare data for display
    display_data = pd.DataFrame([(header, ", ".join(possibles)) for header, possibles in header_mappings.items()],
                                columns=["Template Header", "Possible Headers"])

    # Apply formatting to the table and set the size
    st.dataframe(display_data.style.set_properties(**{
    }).set_table_styles([{
        'selector': 'thead th',
        'props': [('background-color', 'cornflowerblue'), ('color', 'white')]
    }]), height=600, width=1000)

# Run the Streamlit app
if __name__ == "__main__":
    run()