# Getting Started - Visual Guide

## 📍 Where You Are Now

You have a complete recursive code agent system in:
```
d:\Documents\git\recursive-coder\
```

All files are ready to use!

## 🎯 What to Do Next (Choose Your Path)

### Path 1: Quick Verification (2 minutes)
```bash
cd d:\Documents\git\recursive-coder
python validate.py
```

✅ This checks that everything is installed correctly

### Path 2: Full Setup (3 minutes)
```bash
cd d:\Documents\git\recursive-coder
python project_setup.py
```

✅ This:
- Installs all dependencies
- Creates agents/ directory
- Lets you create an initial task
- Validates everything

### Path 3: See It In Action (5 minutes)
```bash
cd d:\Documents\git\recursive-coder
python example_usage.py
```

✅ This shows basic agent creation

Then try:
```bash
python complete_example.py
```

✅ This shows a complete workflow with all features

## 📖 Documentation Map

**Start Here (5 min read):**
- 📄 [QUICKSTART.md](QUICKSTART.md) - Get running in 5 minutes

**Learn More (30 min read):**
- 📄 [README.md](README.md) - Comprehensive guide
- 📄 [INDEX.md](INDEX.md) - Quick reference

**Detailed Reference:**
- 📄 [PROJECT_FILES.md](PROJECT_FILES.md) - File descriptions
- 📄 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - What was built

## 🗂️ File Organization

### 🐍 Python Core (Use these!)
```
recursive_agent.py          ← Main agent class
code_agent_integration.py   ← SmolAgents integration
logger.py                   ← Logging system
config.py                   ← Configuration
```

### 🔧 Configuration
```
pyproject.toml              ← Project setup
config_template.py          ← Custom configuration template
.gitignore                  ← Git exclusions
```

### 🚀 Getting Started
```
project_setup.py            ← Initial setup script
validate.py                 ← System validation
example_usage.py            ← Simple example
complete_example.py         ← Full demonstration
```

### 📚 Documentation
```
QUICKSTART.md               ← Quick start (5 min)
README.md                   ← Full guide (30 min)
INDEX.md                    ← Quick reference
PROJECT_FILES.md            ← File details
IMPLEMENTATION_SUMMARY.md   ← What was built
GETTING_STARTED.md          ← This file
```

## 💻 First Command

### Option A: Just Validate
```bash
python validate.py
```

Expected output:
```
Checking Python version... ✓ Python 3.10
Checking dependencies... ⚠ Missing optional: smol-agents, pytest
Checking project structure... ✓ All core files present
Testing imports... ✓ All modules importable
Testing agent creation... ✓ Agent can be created
Testing logger... ✓ Logger works
Testing CodeAgent integration... ✓ 7 tools available
Checking example files... ✓ All examples present

RESULTS: 6/8 checks passed
```

### Option B: Full Setup
```bash
python project_setup.py
```

This will:
1. Install dependencies
2. Create agents/ folder
3. Optionally create initial task
4. Run validation

### Option C: See It Working
```bash
python example_usage.py
```

Then:
```bash
python complete_example.py
```

## 🔑 Key Concepts (2-minute overview)

### What This System Does

1. **Loads a Task**: Reads `prompt.txt` (or you provide one)

2. **Analyzes It**: Decides if it's too complex to do at once

3. **Breaks It Down**: Creates child agents in `task_*` folders

4. **Generates Code**: Each agent writes `solution.py` with:
   - Multiple functions
   - Type hints
   - Tests

5. **Tests It**: Runs pytest automatically

6. **Integrates**: Parent calls child functions using Python's `inspect` module

### Example Workflow

```
Start: "Build a web scraper and data analyzer"
  ├─ "Web Scraper Module"
  │  └─ Creates: task_web_scraper/solution.py
  │
  └─ "Data Analyzer Module"  
     └─ Creates: task_data_analyzer/solution.py

Parent can then:
  - Import task_web_scraper/solution.py
  - Call functions like fetch_data(), parse_html()
  - Use results in its own code
```

## 📁 After Running Setup

You'll have this structure:
```
recursive-coder/
├── (all these source files)
└── agents/
    └── root/                    ← Your main agent
        ├── prompt.txt           ← Your task
        ├── solution.py          ← Generated code
        ├── test_solution.py     ← Generated tests
        ├── log.txt              ← Progress log
        ├── error.txt            ← Errors (if any)
        └── task_*/              ← Child agents (if created)
```

## 🎓 Recommended Learning Order

### 1. Quick Validation (30 seconds)
```bash
python validate.py
```

### 2. Read Quick Start (5 minutes)
Open [QUICKSTART.md](QUICKSTART.md)

### 3. Run Examples (5 minutes)
```bash
python example_usage.py
python complete_example.py
```

### 4. Read Full Guide (20 minutes)
Open [README.md](README.md)

### 5. Try It Yourself (10 minutes)
```python
from recursive_agent import RecursiveAgent
from pathlib import Path

agent = RecursiveAgent(agent_dir=Path("agents/my_task"))
result = agent.execute()
```

### 6. Integrate with SmolAgents (15 minutes)
See integration example in [complete_example.py](complete_example.py) or [README.md](README.md)

## 🎯 Common Tasks

### Create a new agent
```bash
mkdir agents/my_task
echo "Your task here" > agents/my_task/prompt.txt
```

### Run validation
```bash
python validate.py
```

### View logs
```bash
type agents\root\log.txt        # Windows
cat agents/root/log.txt         # Mac/Linux
```

### View errors
```bash
type agents\root\error.txt      # Windows
cat agents/root/error.txt       # Mac/Linux
```

### Run tests
```bash
pytest agents/root/test_solution.py -v
```

## ❓ Common Questions

**Q: Do I need to install anything first?**
A: Run `python project_setup.py` - it does it all

**Q: How do I create my first agent?**
A: Run `python project_setup.py` and answer the prompts

**Q: Can I customize settings?**
A: Yes! Copy `config_template.py` to create custom config

**Q: How does it integrate with SmolAgents?**
A: See complete_example.py or README.md integration section

**Q: What if something fails?**
A: Check `log.txt` and `error.txt` in the agent folder

**Q: Can I run agents in parallel?**
A: Currently sequential, but parallel support in future versions

## 🆘 Getting Help

1. **Validation Issues**? 
   → Run `python validate.py` to diagnose

2. **Setup Problems?**
   → Check Python version: `python --version` (needs 3.10+)

3. **Agent Failures?**
   → Check `agents/root/error.txt`

4. **Not sure what to do?**
   → Read [QUICKSTART.md](QUICKSTART.md)

5. **Need API details?**
   → Read [README.md](README.md)

6. **Which file does what?**
   → Check [PROJECT_FILES.md](PROJECT_FILES.md)

## ✅ Checklist

Ready to start? Follow this:

- [ ] You're in the recursive-coder directory
- [ ] You have Python 3.10 or newer
- [ ] You've read this getting started guide
- [ ] Run: `python validate.py`
- [ ] Read: [QUICKSTART.md](QUICKSTART.md)
- [ ] Run: `python example_usage.py`
- [ ] Create your first agent!

## 🚀 One-Minute Start

```bash
# 1. Navigate to project
cd d:\Documents\git\recursive-coder

# 2. Validate it works
python validate.py

# 3. See an example
python example_usage.py

# 4. Read quick start
notepad QUICKSTART.md
```

## 📞 System Status

✅ All files created
✅ All components implemented
✅ All documentation written
✅ All examples provided
✅ Validation script ready
✅ Setup script ready

**Ready to go!**

---

**Next Step:** Run `python validate.py` to verify everything is set up!

Then read [QUICKSTART.md](QUICKSTART.md) for the next steps.
