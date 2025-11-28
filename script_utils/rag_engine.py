import faiss
from sentence_transformers import SentenceTransformer
from ollama import Client

client = Client()
model = SentenceTransformer('all-MiniLM-L6-v2')

class RAGSearchEngine:
    def __init__(self, scenes, schedule):
        self.scenes = scenes
        self.schedule = schedule
        self.index = None
        self.text_lookup = []
        self.scene_lookup = []  # Store full scene objects for context
        self.schedule_lookup = []  # Store full schedule entries
        self.embeddings = []
        self._build_index()

    def _scene_to_text(self, scene):
        """Create a rich text representation of a scene for indexing."""
        base_info = f"Scene {scene['scene_number']}: {scene['heading']} | Location: {scene['location']} | Time: {scene['time_of_day']} | Characters: {', '.join(scene.get('characters', []))}"
        
        # Include action/dialogue content if available (first 500 chars for indexing)
        actions = scene.get('actions', [])
        if actions:
            action_text = ' '.join(actions[:20])  # First 20 action lines
            if len(action_text) > 500:
                action_text = action_text[:500] + "..."
            base_info += f" | Content: {action_text}"
        
        return base_info

    def _scene_to_full_text(self, scene):
        """Create a complete text representation of a scene with all content."""
        text = f"=== Scene {scene['scene_number']} ===\n"
        text += f"HEADING: {scene['heading']}\n"
        text += f"LOCATION: {scene['location']}\n"
        text += f"TIME OF DAY: {scene['time_of_day']}\n"
        text += f"CHARACTERS: {', '.join(scene.get('characters', []))}\n"
        
        # Include full action/dialogue content
        actions = scene.get('actions', [])
        if actions:
            text += f"\nCONTENT:\n"
            text += '\n'.join(actions)
        
        return text

    def _schedule_to_text(self, entry):
        return f"Day {entry['day']} | {entry['scene_heading']} | Location: {entry['location']} | Characters: {', '.join(entry['characters'])} | Time: {entry['start_time']} | Duration: {entry.get('estimated_duration', 'N/A')}"

    def _schedule_to_full_text(self, entry):
        """Create a complete text representation of a schedule entry."""
        text = f"=== Day {entry['day']} - {entry['start_time']} ===\n"
        text += f"SCENE: {entry['scene_heading']}\n"
        text += f"LOCATION: {entry['location']}\n"
        text += f"TIME OF DAY: {entry['time_of_day']}\n"
        text += f"CHARACTERS: {', '.join(entry['characters'])}\n"
        text += f"DURATION: {entry.get('estimated_duration', 'N/A')}\n"
        return text

    def _build_index(self):
        # Build index with scene summaries
        self.text_lookup = [self._scene_to_text(s) for s in self.scenes] + \
                           [self._schedule_to_text(s) for s in self.schedule]
        
        # Store full scene and schedule objects for context retrieval
        self.scene_lookup = self.scenes
        self.schedule_lookup = self.schedule
        
        self.embeddings = model.encode(self.text_lookup)

        dim = self.embeddings[0].shape[0]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.embeddings)

        print(f" FAISS index built with {len(self.text_lookup)} entries")

    def query(self, question, top_k=5):
        q_embedding = model.encode([question])
        D, I = self.index.search(q_embedding, top_k)

        # Retrieve full context for the top-k results
        retrieved_contexts = []
        num_scenes = len(self.scenes)
        
        for idx in I[0]:
            if idx < num_scenes:
                # It's a scene - get full scene content
                scene = self.scene_lookup[idx]
                retrieved_contexts.append(self._scene_to_full_text(scene))
            else:
                # It's a schedule entry
                schedule_idx = idx - num_scenes
                if schedule_idx < len(self.schedule_lookup):
                    entry = self.schedule_lookup[schedule_idx]
                    retrieved_contexts.append(self._schedule_to_full_text(entry))
        
        # Build comprehensive prompt with script understanding instructions
        script_summary = self._get_script_summary()
        
        prompt = f"""You are an expert screenplay analyst. You have access to a parsed screenplay and its shooting schedule. 
Your task is to answer questions about the script, characters, scenes, locations, and shooting schedule with deep understanding of the story and context.

{script_summary}

=== RELEVANT CONTEXT FROM THE SCRIPT ===

{chr(10).join(retrieved_contexts)}

=== USER QUESTION ===
{question}

=== INSTRUCTIONS ===
- Read and understand the full context provided above, including dialogue, actions, and scene details
- Use the complete scene content (not just summaries) to provide accurate, detailed answers
- Reference specific scenes, characters, locations, and dialogue when relevant
- If the question is about the shooting schedule, use the schedule information provided
- Be thorough and cite specific details from the script when answering
- If information is not available in the context, say so clearly

=== YOUR ANSWER ===
"""
        
        try:
            response = client.chat(model='llama3.2', messages=[{"role": "user", "content": prompt}])
            return response['message']['content']
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise Exception(
                    f"Model 'llama3.2' not found. Please run: ollama pull llama3.2\n"
                    f"Original error: {str(e)}"
                )
            raise
    
    def _get_script_summary(self):
        """Generate a summary of the script for context."""
        total_scenes = len(self.scenes)
        total_days = len(set(entry['day'] for entry in self.schedule))
        
        # Get all unique characters
        all_characters = set()
        for scene in self.scenes:
            all_characters.update(scene.get('characters', []))
        
        # Get all unique locations
        all_locations = set()
        for scene in self.scenes:
            if scene.get('location') and scene['location'] != 'UNKNOWN':
                all_locations.add(scene['location'])
        
        # Get top characters and locations for summary
        top_characters = ', '.join(sorted(list(all_characters))[:20])
        top_locations = ', '.join(sorted(list(all_locations))[:15])
        
        summary = f"""SCRIPT OVERVIEW:
- Total Scenes: {total_scenes}
- Total Shooting Days: {total_days}
- Total Characters: {len(all_characters)}
- Total Locations: {len(all_locations)}
- Main Characters: {top_characters}
- Main Locations: {top_locations}

"""
        return summary
