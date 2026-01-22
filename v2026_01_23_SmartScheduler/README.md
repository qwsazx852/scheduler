# Smart Employee Scheduler 🚀

An AI-powered, constraint-based employee scheduling system designed for fairness and flexibility.

## Features ✨

- **Smart Logic**:
  - **Fairness**: Balances total shifts and specifically weights "Weekend Shifts" to ensure equal burden.
  - **Role Preservation**: Prioritizes general staff for general tasks, saving "Leaders" for critical roles.
  - **Coverage Assurance**: Checks coverage every hour to prevent gaps.
  - **Variety**: Randomizes shift selection to prevent monotony.

- **User Interface (Streamlit)**:
  - **Auto-Save**: Changes to employee settings are saved immediately.
  - **Visualizations**: Gantt charts, Daily Distribution, and Employee Matrix (Employee View).
  - **Statistics**: Fairness dashboard to track workload.

- **API Integration (FastAPI)**:
  - Connects easily with **n8n** or other automation tools.
  - Exports `schedule_matrix` for easy Google Sheets integration.

## Files Structure 📂

- `app_scheduler.py`: Main UI application (Streamlit).
- `api_scheduler.py`: API Server (FastAPI).
- `scheduler_logic.py`: Core algorithms and business logic.
- `config_*.json`: Configuration files for employees, shifts, rules.

## How to Run 🏃‍♂️

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run UI (Streamlit)
```bash
streamlit run app_scheduler.py
```
Visit http://localhost:8501

### 3. Run API Server
```bash
python api_scheduler.py
```
API available at http://localhost:8000
