# Assets Directory

This directory contains media and reference materials for the Music AI Recommender System project.

## 📁 Folder Structure

```
assets/
├── diagrams/          # System architecture diagrams
│   ├── architecture.mmd
│   └── README.md
└── README.md          # This file
```

## 📊 Available Assets

### System Architecture Diagrams

**Location**: `diagrams/`

The system architecture is documented in multiple formats:

1. **architecture.mmd** (Required - Mermaid Source)
   - Pure Mermaid syntax for the complete system architecture
   - Shows all 5 phases, data flows, and components
   - Can be viewed on GitHub, GitLab, VS Code, and online editors
   - See `diagrams/README.md` for details

2. **SYSTEM_DIAGRAM.md** (Root directory)
   - Same diagram embedded in Markdown with detailed explanations
   - Component descriptions
   - Data flow documentation
   - Testing strategy breakdown

## 🎯 How to Use Assets

### Viewing the Architecture Diagram

**Option 1: GitHub**
- Navigate to `diagrams/architecture.mmd`
- GitHub renders Mermaid automatically
- Click to view the full diagram

**Option 2: VS Code**
- Install "Markdown Preview Mermaid Support" extension
- Open `diagrams/README.md`
- Extension renders the diagram in preview pane

**Option 3: Mermaid Live Editor**
- Go to https://mermaid.live
- Copy contents of `diagrams/architecture.mmd`
- Paste into the editor
- Interact with the diagram (zoom, pan)

**Option 4: Online**
- Any Markdown viewer that supports Mermaid
- GitLab, Notion, Confluence, etc.

### Exporting to PNG/SVG

If you need image exports:

1. **From Mermaid Live Editor**
   - Open the diagram in https://mermaid.live
   - Click "Download" menu
   - Choose PNG or SVG format
   - Save to `assets/` folder (optional)

2. **From VS Code**
   - Install "Markdown to PDF" extension
   - Export Markdown file to PDF
   - Screenshot or convert as needed

3. **Using mmdc (Command Line)**
   ```bash
   npm install -g mermaid-cli
   mmdc -i diagrams/architecture.mmd -o diagrams/architecture.png
   ```

## 📝 File Formats

### .mmd (Mermaid Source - REQUIRED)
- **Purpose**: Source of truth for the diagram
- **Format**: Plain text, Mermaid syntax
- **Storage**: Version controlled in git
- **Editing**: Any text editor (VS Code recommended)
- **Viewing**: GitHub, GitLab, VS Code, online editors

### .png (PNG Export - OPTIONAL)
- **Purpose**: Embedded images in documentation
- **Format**: Raster image
- **Storage**: Can be committed or generated
- **Viewing**: All tools
- **Drawback**: Not version-controllable for edits

## 🔄 Workflow for Updates

When you need to update the system diagram:

1. **Edit the source**
   ```bash
   # Edit the Mermaid source
   vim diagrams/architecture.mmd
   ```

2. **Preview changes**
   - Use Mermaid Live Editor: https://mermaid.live
   - Or VS Code with Mermaid extension

3. **Save and commit**
   ```bash
   git add diagrams/architecture.mmd
   git commit -m "update: Refine system architecture diagram"
   ```

4. **Optional: Export to PNG**
   - If needed for embedding in docs
   - But **keep the .mmd file as primary source**

## 📚 Documentation Map

Assets relate to these documentation files:

| File | Type | Location | Purpose |
|------|------|----------|---------|
| `architecture.mmd` | Mermaid | `diagrams/` | System architecture |
| `SYSTEM_DIAGRAM.md` | Markdown | Root | Architecture with explanations |
| `SYSTEM_ARCHITECTURE.mmd` | Mermaid | Root | Original diagram (can be removed) |
| `README.md` | Markdown | Root | Quick start guide |
| `ENHANCEMENTS.md` | Markdown | Root | Enhancement features |

## 🎓 Architecture Components

The diagram shows:

### Input Layer
- User profiles (genre, mood, energy preferences)
- Natural language feedback

### 5 Processing Phases
1. **PLAN**: Parse feedback and extract intent
2. **ACT**: Adjust preferences and recommend
3. **VALIDATE**: Check recommendation quality
4. **LEARN**: Update embeddings
5. **HUMAN LOOP**: User validates and provides feedback

### Data Layer
- Song database (68 songs × 14 features)
- Mood embeddings (17 moods × 2D space)
- Genre relationships (semantic graph)
- Feedback memory (learning history)

### Testing & Validation
- 7 test suites (104 total tests)
- Integration with all phases
- Quality gates before learning

### Output Layer
- Original recommendations (baseline)
- Adjusted recommendations (after feedback)
- Learning statistics (metrics)

## 💡 Best Practices

✅ **DO:**
- Keep `.mmd` files as source of truth
- Commit to git for version control
- Use VS Code for editing with preview
- Update diagram when architecture changes
- Include `diagrams/` in documentation

❌ **DON'T:**
- Edit exported PNG files (use the .mmd instead)
- Store large binary files as primary
- Manually draw diagrams without source
- Ignore diagram when architecture changes

## 🚀 Integration with Project

The assets directory supports:
- **Documentation**: Embed in README, guides
- **Presentations**: Use in slides, reports
- **Code Review**: Reference in PRs
- **Onboarding**: Show new contributors
- **Design**: System design discussions

## 📞 Questions?

Refer to:
1. `diagrams/README.md` — About the diagram
2. `SYSTEM_DIAGRAM.md` — Detailed explanation
3. `CLAUDE.md` — Project guidance
4. `ENHANCEMENTS.md` — Feature details
