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
        self.embeddings = []
        self._build_index()

    def _scene_to_text(self, scene):
        return f"Scene: {scene['heading']} | Characters: {', '.join(scene['characters'])} | Location: {scene['location']}"

    def _schedule_to_text(self, entry):
        return f"Day {entry['day']} | {entry['scene_heading']} | Location: {entry['location']} | Characters: {', '.join(entry['characters'])} | Time: {entry['start_time']}"

    def _build_index(self):
        self.text_lookup = [self._scene_to_text(s) for s in self.scenes] + \
                           [self._schedule_to_text(s) for s in self.schedule]
        self.embeddings = model.encode(self.text_lookup)

        dim = self.embeddings[0].shape[0]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.embeddings)

        print(f" FAISS index built with {len(self.text_lookup)} entries")

    def query(self, question, top_k=5):
        q_embedding = model.encode([question])
        D, I = self.index.search(q_embedding, top_k)

        retrieved = [self.text_lookup[i] for i in I[0]]
        prompt = f"User question: {question}\n\nContext:\n" + "\n".join(retrieved) + "\n\nAnswer in detail:"
        response = client.chat(model='mistral', messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
