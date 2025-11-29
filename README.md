# Smart Task Analyzer

An intelligent task prioritization system that analyzes tasks using multiple strategies and provides clear reasoning for priority decisions.

**Tech Stack:** Django REST Framework, Vanilla JavaScript, HTML5, CSS3

**Key Features:**
- ✅ **4 Sorting Strategies** - Smart Balance, Fastest Wins, High Impact, Deadline Driven
- ✅ **Circular Dependency Detection** - DFS-based cycle detection with warnings
- ✅ **Robust Data Validation** - Handles missing, invalid, and edge-case data
- ✅ **Overdue Task Handling** - Special treatment for past-due tasks
- ✅ **Configurable Weights** - Customize scoring factors
- ✅ **Beautiful UI** - Visual priority indicators with explanations

---

## Critical Thinking Elements

### 1. Multiple Sorting Strategies

**⚖️ Smart Balance** (35/35/15/15) - Balanced approach for general use
**⚡ Fastest Wins** (70/20/10) - Quick tasks first for momentum
**⭐ High Impact** (80/10/10) - Important tasks regardless of difficulty
**📅 Deadline Driven** (80/15/5) - Urgency-focused for time-sensitive work

Users select strategy via dropdown. Backend routes to appropriate algorithm:
```python
def calculate_priority(task, strategy="smart_balance", custom_weights=None):
    if strategy == "fastest_wins":
        return calculate_fastest_wins(task)
    # ... other strategies
```

### 2. Circular Dependency Detection

**Algorithm:** DFS with recursion stack - O(V + E) time complexity

Detects cycles like: Task A → Task B → Task C → Task A

**Implementation:**
```python
def detect_circular_dependencies(tasks):
    # Tracks visited nodes and recursion stack
    # Returns all cycles with human-readable warnings
```

**UX:** Non-blocking warnings displayed in UI with specific cycle paths

### 3. Edge Case Handling

**Overdue Tasks:**
```python
if days_left < 0:
    return 10.0  # Maximum urgency for overdue tasks
```

**Missing/Invalid Data:**
- Missing title → "Untitled Task"
- Missing importance → 5 (default medium)
- Negative hours → 0
- Invalid importance → Clamped to 1-10

**Data Sanitization:**
```python
def sanitize_task_data(task):
    # Validates all fields with sensible defaults
    # Handles type conversions with try/except
    # Clamps values to valid ranges
```

### 4. Configurable Algorithm

**Custom Weights for Smart Balance:**
```json
{
  "strategy": "smart_balance",
  "custom_weights": {
    "urgency": 0.5,
    "importance": 0.3,
    "effort": 0.1,
    "dependencies": 0.1
  }
}
```

### 5. Balancing Competing Priorities

**Eisenhower Matrix Applied:**

| Scenario | Strategy | Rationale |
|----------|----------|-----------|
| Product launch | Deadline Driven | Time-critical deliverables |
| Strategic planning | High Impact | Long-term value |
| Low energy day | Fastest Wins | Build momentum |
| Normal workflow | Smart Balance | Holistic balance |

**Dynamic Scoring:** Priorities auto-adjust daily as deadlines approach.

---

## Design Decision: Array vs Linked List

**Initial Consideration:** Sorted linked list for O(n) insertion

**Chosen:** Arrays with O(n log n) sorting

**Rationale:**
- **Stateless Architecture** - Each request is independent, no persistent state
- **Bulk Processing** - Tasks arrive in bulk, not incrementally
- **Dynamic Scoring** - Priority changes daily based on current date → requires re-sorting anyway
- **Task Mutability** - Changes require re-calculation regardless of data structure

**Conclusion:** Arrays provide simpler implementation with equivalent/better performance for this use case.

---

## Scoring Algorithm

### Formula (Smart Balance)
```
Score = (Urgency × 0.35) + (Importance × 0.35) + (Effort × 0.15) + (Dependencies × 0.15)
```

### Factor Scoring

**Urgency (0-10):** Days until deadline
- Overdue/Today: 10 | Tomorrow: 9 | 2-3 days: 8 | 4-7 days: 6 | 8-14 days: 4 | 30+ days: 1

**Importance (1-10):** User-defined priority (direct input)

**Effort (0-10):** Quick wins prioritized
- ≤1h: 10 | 2-3h: 8 | 4-6h: 6 | 7-12h: 4 | 12+h: 2

**Dependencies (0-10):** Tasks blocking others
- 0 deps: 0 | 1 dep: 3 | 2 deps: 6 | 3 deps: 8 | 4+ deps: 10

---

## Setup & Installation

### Backend
```bash
cd Backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install django djangorestframework django-cors-headers
python manage.py migrate
python manage.py runserver  # http://localhost:8000
```

### Frontend
```bash
cd Frontend
# Use Live Server (VS Code) or:
python -m http.server 5500  # http://127.0.0.1:5500
```

---

## API Documentation

### Analyze Tasks
**POST** `/api/tasks/analyze/`

**Request:**
```json
{
  "tasks": [
    {
      "title": "Fix bug",
      "due_date": "2025-11-30",
      "estimated_hours": 2,
      "importance": 10,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "title": "Fix bug",
      "score": 8.75,
      "reasons": [
        "🔥 Due TODAY — extremely urgent!",
        "⭐ CRITICAL importance (9-10/10)",
        "⚡ Short task — 2-3 hours"
      ]
    }
  ],
  "strategy": {
    "name": "Smart Balance",
    "icon": "⚖️",
    "weights": "35% urgency, 35% importance, 15% effort, 15% dependencies"
  },
  "warnings": [],
  "circular_dependencies": []
}
```

### Get Strategies
**GET** `/api/tasks/strategies/`

Returns all available strategies with metadata.

### Suggest Top Tasks
**POST** `/api/tasks/suggest/`

Returns top 3 tasks using Smart Balance strategy.

---

## Usage

1. **Add Tasks** - Fill form with title, due date, hours, importance, dependencies
2. **Select Strategy** - Choose from dropdown (Smart Balance, Fastest Wins, etc.)
3. **Analyze** - Click "Analyze & Sort Tasks"
4. **View Results** - See prioritized list (P1-P10) with color coding and reasons

**Priority Levels:**
- **P1-P3** (Red) - High priority
- **P4-P7** (Yellow) - Medium priority
- **P8-P10** (Green) - Low priority

---

## Technical Highlights

- **Sorting:** O(n log n) using Python's Timsort
- **Cycle Detection:** O(V + E) DFS algorithm
- **Security:** CORS configured, input validation, XSS protection
- **Code Quality:** Type hints, comprehensive docstrings, DRY principles
- **Backward Compatible:** Accepts simple array or structured request

---

## Future Improvements

**Short-term:**
- [ ] Persistent storage (PostgreSQL/SQLite)
- [ ] User authentication (JWT)
- [ ] Task categories/projects
- [ ] Export to CSV/PDF

**Long-term:**
- [ ] Machine learning for personalized scoring
- [ ] Team collaboration features
- [ ] Calendar integration
- [ ] Mobile app

---

## Author Notes

Created as a technical assignment demonstrating:
- Full-stack development
- Algorithm design (multiple strategies, graph algorithms)
- System architecture (stateless design, data structure trade-offs)
- Critical thinking (edge cases, competing priorities)
- Clean code practices

**Key Insight:** Chose arrays over linked lists despite O(n log n) vs O(n) trade-off because stateless architecture, bulk processing, and dynamic date-based scoring require re-sorting anyway, making simpler array implementation more practical.

---

## License

Created for educational and demonstration purposes.
