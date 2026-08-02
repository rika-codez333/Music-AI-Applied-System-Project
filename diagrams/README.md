# System Architecture Diagrams

This directory contains the system architecture diagrams for the Music AI Recommender System.

## 📊 Files

### `architecture.mmd`
**Main system architecture diagram (Mermaid source)**

Shows the complete agentic feedback loop with:
- **Input Layer**: User profile and feedback
- **Plan Phase**: Feedback analyzer parsing
- **Act Phase**: Search and recommendations
- **Validate Phase**: Quality checking
- **Learn Phase**: Embedding updates
- **Data Layer**: Storage and embeddings
- **Testing Layer**: 104 comprehensive tests
- **Output Layer**: Recommendations and statistics
- **Human in the Loop**: User validation and feedback

**View the diagram:**
1. GitHub: Opens automatically when viewing the .mmd file
2. VS Code: Install "Markdown Preview Mermaid Support" extension
3. Mermaid Live Editor: Visit https://mermaid.live and paste the contents
4. GitLab/Notion: Renders automatically

## 🎯 What the Diagram Shows

### Component Breakdown
- **5 Processing Phases**: Orchestrated Plan → Act → Validate → Learn
- **3 Data Sources**: Songs, Embeddings, Genre Relationships
- **4 Storage Types**: Database, Embeddings, Relationships, Memory
- **7 Test Suites**: 104 total tests covering all components
- **Human Feedback Loop**: User evaluation and validation

### Data Flow
```
User Input
    ↓
[PLAN] Parse feedback → Extract intent
    ↓
[ACT] Adjust preferences → Generate recommendations
    ↓
[VALIDATE] Check if adjustment worked → Confidence score
    ↓
[LEARN] Update embeddings (if validated)
    ↓
User sees results → Provides feedback → Loop repeats
```

### Color Coding
- 🔵 **Blue**: Input layer (user data)
- 🟧 **Orange**: Processing phases
- 🟪 **Purple**: Data storage
- 🟩 **Green**: Testing and validation
- 🟥 **Pink**: Output recommendations
- 🟨 **Yellow**: Human interaction

## 📝 About Mermaid Files

Mermaid is a JavaScript-based diagramming tool that uses a simple syntax to create diagrams.

**Advantages:**
- ✅ Plain text (version control friendly)
- ✅ Renders natively on GitHub, GitLab
- ✅ No need for external image editors
- ✅ Easy to maintain and update
- ✅ Can export to PNG, SVG

**Formats Supported:**
- `.mmd` files (pure Mermaid syntax)
- Markdown code blocks with `mermaid` language tag

## 🔄 How to Update the Diagram

1. Edit `architecture.mmd` in your text editor
2. Preview in Mermaid Live Editor (https://mermaid.live)
3. Save changes to the file
4. Commit to git

## 📚 Related Documentation

See also:
- `../SYSTEM_DIAGRAM.md` — Detailed architecture explanation
- `../README.md` — Quick start guide
- `../ENHANCEMENTS.md` — Optional features documentation

## 🎓 Integration with Project

This diagram serves as the visual reference for:
- System design overview
- Component relationships
- Data flow through phases
- Testing coverage
- Human-AI interaction points

All components shown have corresponding:
- Source files in `src/`
- Test files in `tests/`
- Documentation in root docs
