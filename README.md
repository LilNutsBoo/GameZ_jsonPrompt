# GameZ Prompt Engine (Heavily relied on user labor input and still under development)

> A structured-data-to-AI storytelling engine for the post-apocalyptic sandbox world of **GameZ**.  
> _Last updated: 2025-07-31_

---

## 🔍 What is this?

**GameZ Prompt Engine** is a specialized tool for extracting narrative-relevant data from Airtable and transforming it into AI-readable JSON prompts for driving dynamic, character-based storytelling in the GameZ universe.

It acts as the middleware between your game's structural data (NPCs, Tasks, Events, Timelines, Items) and large language models like GPT-4, generating prompts based on real-time selections, logic filters, and world states.

---

## 🧠 Core Features

- 📡 **Airtable Data Extraction**: Pulls structured records like NPCs, tasks, world events, timelines, and items.
- 🧮 **Dynamic Filtering & Scoring**: Based on internal NPC logic, behavior presets, emotional states, memory & relationship scoring.
- 🧾 **Prompt Generation**: Converts data into optimized AI-readable JSON prompt payloads.
- 💬 **AI Interaction Gateway**: Streamlit UI to select behaviors, trigger tasks, simulate dialogue or world events.
- 🧠 **Full support for GameZ NPCA Design System v3.0**.

---

## 🗂️ Project Structure

```
GameZ/
├── app/                  # Core app code and Streamlit UI
│   ├── gamez_ui.py
│   ├── data_loader.py
│   ├── npca_logic.py
│   ├── task_selector.py
│   ├── ...
│   ├── cache/            # Temporary logs, not tracked
│   └── local_database/   # Local Airtable mock data
├── .env                  # API keys (excluded from Git)
├── .gitignore
├── README.md
├── live_gaming_file/         # World timeline or story planning (optional)
└── legacy_file/          # Archived documents and rulebooks
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/GameZ-PromptEngine.git
cd GameZ-PromptEngine
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure `.env` with your Airtable keys
```env
AIRTABLE_API_KEY=your_token_here
AIRTABLE_BASE_ID=your_base_id_here
```

### 4. Launch the Streamlit interface
```bash
streamlit run app/gamez_ui.py
```

---

## 📦 Dependencies

- `streamlit`
- `python-dotenv`
- `requests`
- `pandas`
- `openai` *(if using OpenAI API directly)*

Check `requirements.txt` for exact versions.

---

## 📌 Current Capabilities

- Task filtering and export
- NPC behavior selection and scoring
- Timeline alignment
- Memory and autonomy log control
- Prompt-to-JSON preview and copy
- Cleanup and reset tools for cache/logs

---

## 📅 Planned Features

- [ ] Multi-round AI memory injection
- [ ] Prompt formatting for Claude / Function Calling
- [ ] Airtable write-back
- [ ] HuggingFace Spaces deployment
- [ ] Timeline-based auto-prompt scheduling

---

## 📚 About GameZ

GameZ is an AI-driven sandbox narrative framework built around realistic NPC behavior and disaster survival logic.  
This prompt engine powers its narrative core by making NPCs act, remember, and evolve in the extreme-heat end-times setting of **潼影** (a 1:1 fictional mirror of Chuzhou, China).

---

## 🧑‍💻 Credits

Created and maintained by **LilyJet**  
For feedback or contributions, open an [Issue](https://github.com/your-username/GameZ-PromptEngine/issues) or send a PR.

---

## 📜 License

MIT License — see `LICENSE` file.
