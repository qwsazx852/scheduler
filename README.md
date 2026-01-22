# Smart Employee Scheduler 🚀

An AI-powered, constraint-based employee scheduling system designed for fairness and flexibility.

**📖 [完整使用手冊 (User Manual)](USER_GUIDE.md)**: 點此查看完整的安裝、設定與自動化串接教學。

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

## Project Structure 🏗️ (Industry Standard)

- **`src/`**: Source code (Application logic, UI, API).
- **`config/`**: Configuration files (JSON).
- **`tests/`**: Debug scripts and unit tests.
- **`run.sh`**: Helper script for easy execution.

## How to Run 🏃‍♂️

### Quick Start
```bash
chmod +x run.sh
./run.sh        # Runs UI
./run.sh api    # Runs API
./run.sh test   # Runs Tests
```

### Manual Execution
```bash
streamlit run src/app_scheduler.py
python3 src/api_scheduler.py
```

### 3. Run API Server
```bash
python api_scheduler.py
```
API available at http://localhost:8000
