# ui_app.py

import streamlit as st
import json
import os
from script_utils.rag_engine import RAGSearchEngine
from run_pipeline import process_screenplay_from_pdf

st.set_page_config(page_title="Screenplay Scheduler", layout="wide")
st.title("🎬 Screenplay Scheduler & Q&A")
st.markdown("Upload a screenplay PDF to generate a shooting schedule and ask questions!")

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# Sidebar for PDF upload
with st.sidebar:
    st.header("📄 Upload Screenplay")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your screenplay PDF to process it"
    )
    
    if uploaded_file is not None:
        # Check if this is a new file
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        if 'last_processed_file' not in st.session_state or st.session_state.last_processed_file != file_key:
            st.session_state.last_processed_file = file_key
            st.session_state.processing_complete = False
            st.session_state.processed_data = None
            st.session_state.rag_engine = None

# Main content area
# Process uploaded PDF if there's a new file
if uploaded_file is not None:
    # Process the PDF if not already processed
    if not st.session_state.processing_complete:
        with st.spinner("Processing screenplay... This may take a moment."):
            try:
                # Read PDF bytes
                pdf_bytes = uploaded_file.read()
                
                # Process the screenplay
                result = process_screenplay_from_pdf(pdf_bytes=pdf_bytes)
                
                # Store in session state
                st.session_state.processed_data = result
                st.session_state.processing_complete = True
                
                # Create RAG engine with new data
                st.session_state.rag_engine = RAGSearchEngine(
                    result['scenes'],
                    result['schedule']
                )
                
                st.success("✅ Screenplay processed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing screenplay: {str(e)}")
                st.session_state.processing_complete = False

# Display results if we have processed data (either from upload or loaded existing)
if st.session_state.processing_complete and st.session_state.processed_data:
        data = st.session_state.processed_data
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎭 Scenes", "📅 Schedule", "❓ Q&A"])
        
        with tab1:
            st.header("Overview")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Scenes", len(data['scenes']))
            
            with col2:
                st.metric("Shooting Days", len(data['call_sheets']))
            
            with col3:
                total_schedule_items = len(data['schedule'])
                st.metric("Schedule Items", total_schedule_items)
            
            # Summary statistics
            st.subheader("📈 Summary")
            
            # Characters
            all_characters = set()
            for scene in data['scenes']:
                all_characters.update(scene.get('characters', []))
            
            st.write(f"**Total Characters:** {len(all_characters)}")
            st.write(f"**Characters:** {', '.join(sorted(all_characters))}")
            
            # Locations
            all_locations = set()
            for scene in data['scenes']:
                if scene.get('location') and scene['location'] != 'UNKNOWN':
                    all_locations.add(scene['location'])
            
            st.write(f"**Total Locations:** {len(all_locations)}")
            st.write(f"**Locations:** {', '.join(sorted(all_locations))}")
        
        with tab2:
            st.header("🎭 Parsed Scenes")
            st.write(f"Total scenes: {len(data['scenes'])}")
            
            # Scene selector
            scene_options = [f"Scene {s['scene_number']}: {s['heading'][:50]}..." for s in data['scenes']]
            selected_scene_idx = st.selectbox("Select a scene to view details:", range(len(data['scenes'])), format_func=lambda x: scene_options[x])
            
            if selected_scene_idx is not None:
                scene = data['scenes'][selected_scene_idx]
                st.subheader(f"Scene {scene['scene_number']}")
                st.write(f"**Heading:** {scene['heading']}")
                st.write(f"**Location:** {scene['location']}")
                st.write(f"**Time of Day:** {scene['time_of_day']}")
                st.write(f"**Characters:** {', '.join(scene.get('characters', []))}")
        
        with tab3:
            st.header("📅 Shooting Schedule")
            st.write(f"Total schedule items: {len(data['schedule'])}")
            
            # Day selector
            days = sorted(data['call_sheets'].keys())
            selected_day = st.selectbox("Select a day to view schedule:", days)
            
            if selected_day:
                st.subheader(f"Day {selected_day}")
                
                # Show call sheet
                call_sheet = data['call_sheets'][selected_day]
                st.write(f"**Actors needed:** {', '.join(call_sheet['actors'])}")
                st.write(f"**Scenes:** {len(call_sheet['scenes'])}")
                
                # Show schedule items for this day
                day_schedule = [item for item in data['schedule'] if item['day'] == selected_day]
                
                st.subheader("Schedule Details")
                for item in day_schedule:
                    with st.expander(f"{item['start_time']} - {item['scene_heading'][:50]}..."):
                        st.write(f"**Location:** {item['location']}")
                        st.write(f"**Time of Day:** {item['time_of_day']}")
                        st.write(f"**Characters:** {', '.join(item['characters'])}")
                        st.write(f"**Duration:** {item['estimated_duration']}")
        
        with tab4:
            st.header("❓ Ask Questions")
            st.markdown("Ask questions about the script or shooting schedule using natural language.")
            
            if st.session_state.rag_engine:
                query = st.text_input(
                    "Ask a question:",
                    placeholder="e.g. When is [character name] scheduled? Which scenes take place at night?",
                    key="qa_input"
                )
                
                if query:
                    with st.spinner("Thinking..."):
                        try:
                            answer = st.session_state.rag_engine.query(query)
                            st.markdown("### Answer:")
                            st.write(answer)
                        except Exception as e:
                            st.error(f"Error generating answer: {str(e)}")
            else:
                st.warning("RAG engine not initialized. Please process a screenplay first.")
    
# Show upload prompt only if no data is loaded
if not (st.session_state.processing_complete and st.session_state.processed_data):
    st.info("👆 Please upload a screenplay PDF using the sidebar to get started.")
    
    # Show existing data if available
    if os.path.exists("output/parsed_script.json") and os.path.exists("output/shooting_schedule.json"):
        st.markdown("---")
        st.subheader("📂 Existing Data Found")
        st.write("You have previously processed data. Upload a new PDF to process it, or load existing data below.")
        
        if st.button("Load Existing Data"):
            try:
                with open("output/parsed_script.json") as f:
                    scenes = json.load(f)
                with open("output/shooting_schedule.json") as f:
                    schedule = json.load(f)
                
                # Load call sheets
                call_sheets = {}
                call_sheets_dir = "output/call_sheets"
                if os.path.exists(call_sheets_dir):
                    for file in os.listdir(call_sheets_dir):
                        if file.startswith("day_") and file.endswith(".json"):
                            day_num = int(file.replace("day_", "").replace(".json", ""))
                            with open(os.path.join(call_sheets_dir, file)) as f:
                                call_sheets[day_num] = json.load(f)
                
                st.session_state.processed_data = {
                    'scenes': scenes,
                    'schedule': schedule,
                    'call_sheets': call_sheets
                }
                st.session_state.rag_engine = RAGSearchEngine(scenes, schedule)
                st.session_state.processing_complete = True
                st.success("✅ Existing data loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading existing data: {str(e)}")
