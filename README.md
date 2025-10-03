# Habit Tracker CLI Application

A comprehensive command-line habit tracking application built with Python, SQLAlchemy, and Click. Track your daily and weekly habits, analyze your progress, and maintain streaks.

## 🌟 Features

- ✅ **Create and manage habits** with daily or weekly periodicity
- 📊 **Track completions** with automatic streak calculations  
- 📈 **Comprehensive analytics** including longest streaks and completion rates
- 🗄️ **SQLite database** with SQLAlchemy ORM for data persistence
- 🔄 **Database migrations** with Alembic for schema versioning
- 🧪 **Comprehensive test suite** with pytest (66 tests)
- 🎯 **Beautiful CLI interface** with colored output and emojis
- 📦 **Professional package structure** with proper separation of concerns
- 🔧 **Installable package** with console script entry points

## 📦 Installation

### Development Installation

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd tracking-app
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install in development mode:**
   ```bash
   pip install -e .
   ```

5. **Initialize the database:**
   ```bash
   alembic upgrade head
   ```

6. **Seed with sample data (optional):**
   ```bash
   python scripts/seed_data.py
   ```

### Package Installation

```bash
# Install as a package
pip install habit-tracker-1.0.0.tar.gz

# Use as command-line tool
habit-tracker --help
```

## 🚀 Usage

### Basic Commands

#### Create a New Habit
```bash
python main.py create
# Or with parameters:
python main.py create --name "Exercise" --description "Daily workout" --periodicity daily
```

#### Complete a Habit
```bash
python main.py complete "Exercise"
```

#### Delete a Habit
```bash
python main.py delete "Exercise"
```

### Analytics Commands

#### List All Habits
```bash
python main.py analyze list-all
```

#### Filter by Periodicity
```bash
python main.py analyze list-by-periodicity daily
python main.py analyze list-by-periodicity weekly
```

#### View Streaks
```bash
# Specific habit streak
python main.py analyze longest-streak "Exercise"

# Best streak across all habits
python main.py analyze longest-streak-all
```

#### Activity Summary
```bash
python main.py analyze summary --days 7
```

### Database Management

#### Reset Database
```bash
python main.py reset
```

#### Run Migrations
```bash
alembic upgrade head
```

## 🏗️ Project Structure

```
tracking-app/
├── 📝 README.md                    # Documentation
├── 📦 requirements.txt             # Dependencies  
├── 🔧 setup.py                     # Package setup
├── ⚙️  env.example                 # Environment variables example
├── 🧪 pytest.ini                  # Test configuration
├── 🎯 main.py                      # Simple entry point
├── ⚖️  alembic.ini                 # Migration config
├── 
├── 📦 habit_tracker/               # Main package
│   ├── __init__.py                 # Package exports
│   ├── 🖥️  cli/                    # CLI module
│   │   ├── __init__.py
│   │   └── commands.py             # CLI commands
│   ├── 🧠 core/                    # Core business logic
│   │   ├── __init__.py
│   │   ├── database.py             # Database configuration
│   │   ├── exceptions.py           # Custom exceptions
│   │   └── models/                 # Database models package
│   │       ├── __init__.py         # Model exports
│   │       ├── enums.py            # Enumerations
│   │       ├── habit.py            # Habit model
│   │       └── completion.py       # Completion model
│   ├── 🔧 services/                # Business services
│   │   ├── __init__.py
│   │   ├── habit_service.py        # Habit operations
│   │   └── analytics_service.py    # Analytics operations
│   ├── 🛠️  utils/                  # Utilities
│   │   ├── __init__.py
│   │   └── date_helpers.py         # Date utility functions
│   └── ⚙️  config/                 # Configuration
│       ├── __init__.py
│       └── settings.py             # Application settings
├── 
├── 📜 scripts/                     # Utility scripts
│   └── seed_data.py                # Data seeding script
├── 
├── 🧪 tests/                       # Test package (66 tests)
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/                       # Unit tests (38 tests)
│   │   ├── test_models.py          # Model tests
│   │   ├── test_services.py        # Service tests
│   │   └── test_utils.py           # Utility tests
│   ├── integration/                # Integration tests (28 tests)
│   │   └── test_full_app.py        # End-to-end tests
│   └── fixtures/                   # Test data
│       └── sample_data.py          # Reusable test data
├── 
├── 🗃️  migrations/                 # Database migrations
│   ├── env.py                      # Alembic environment
│   └── versions/                   # Migration scripts
├── 
├── 🗄️  data/                       # Data directory
│   └── habits.db                   # SQLite database
└── 
└── 🐍 venv/                        # Virtual environment
```

## 🏛️ Architecture

The application follows **clean architecture principles** with clear separation of concerns:

### Package Organization
- **`habit_tracker.core`**: Database models, exceptions, and configuration
- **`habit_tracker.services`**: Business logic and data operations
- **`habit_tracker.cli`**: User interface and command handling
- **`habit_tracker.utils`**: Shared utility functions
- **`habit_tracker.config`**: Application configuration management

### Layer Separation
- **Models Layer**: SQLAlchemy ORM models with relationships
- **Service Layer**: Business logic abstraction (HabitService, Analytics)
- **CLI Layer**: Click-based command interface with rich formatting
- **Database Layer**: SQLite with Alembic migrations and session management

### Database Schema

#### Habits Table
- `id`: Primary key
- `name`: Unique habit name (indexed)
- `description`: Optional description
- `periodicity`: ENUM (daily/weekly)
- `created_at`: Creation timestamp

#### Completions Table
- `id`: Primary key
- `habit_id`: Foreign key to habits (indexed)
- `completed_at`: Completion timestamp

### Enhanced Model Features
- **Habit Model**: Helper methods (`is_daily()`, `completion_count`)
- **Completion Model**: Date utilities (`is_today()`, `days_ago()`)
- **Enum Extensions**: Future-ready with additional status types

## 🧪 Testing

### Test Structure
```
tests/                              # 66 total tests
├── conftest.py                     # Shared fixtures
├── unit/                          # 38 unit tests
│   ├── test_models.py             # Model behavior (12 tests)
│   ├── test_services.py           # Business logic (17 tests)
│   └── test_utils.py              # Utility functions (9 tests)
└── integration/                   # 28 integration tests
    └── test_full_app.py           # End-to-end workflows
```

### Running Tests
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/ -v

# Run with coverage
pytest --cov=habit_tracker --cov-report=html

# Run specific test category
pytest -m unit
pytest -m integration
```

### Test Features
- ✅ **Isolated testing** with temporary databases
- ✅ **Shared fixtures** for consistent test data
- ✅ **Comprehensive coverage** of all components
- ✅ **Fast execution** (<0.2s for unit tests)
- ✅ **Professional structure** following pytest best practices

## 🌱 Sample Data

The application includes a seed script that creates 5 predefined habits with realistic completion data:

1. **Drink Water** (daily) - High consistency habit
2. **Go for a run** (daily) - Moderate consistency 
3. **Learn Python** (daily) - Good consistency
4. **Weekly Review** (weekly) - Planning habit
5. **Clean Apartment** (weekly) - Maintenance habit

Run the seed script:
```bash
python scripts/seed_data.py
```

## 🎯 CLI Examples

### Creating Your First Habit
```bash
$ python main.py create
Enter habit name: Read Books
Enter habit description: Read for 30 minutes daily
Enter periodicity (daily/weekly): daily
✅ Habit 'Read Books' (daily) created successfully!
```

### Completing a Habit
```bash
$ python main.py complete "Read Books"
✅ Habit 'Read Books' marked as complete for today!
🔥 Current streak: 5 days
```

### Viewing Analytics
```bash
$ python main.py analyze list-all

📊 All Tracked Habits:
--------------------------------------------------
• Name: Drink Water
  Periodicity: daily
  Created: 2023-11-01
  🔥 Current Streak: 12
  🏆 Best Streak: 15
  ✅ Total Completions: 25
  📈 Completion Rate: 89.3%
```

### Activity Summary
```bash
$ python main.py analyze summary

📊 Activity Summary (Last 7 days):
----------------------------------------
Total completions: 12
Habits with activity: 4/5

📈 Per-Habit Activity:
• Drink Water: 7 completions, 🔥 7 days streak
• Exercise: 5 completions, 🔥 3 days streak
• Reading: 3 completions, 💤 0 days streak
```

## 🔧 Development

### Package Development
```bash
# Install in development mode
pip install -e .

# Run linting
flake8 habit_tracker/

# Run type checking  
mypy habit_tracker/

# Build package
python setup.py sdist bdist_wheel
```

### Adding New Features
1. **Models**: Add to `habit_tracker/core/models/`
2. **Services**: Add to `habit_tracker/services/`
3. **CLI Commands**: Add to `habit_tracker/cli/commands.py`
4. **Tests**: Add corresponding unit and integration tests
5. **Documentation**: Update README and docstrings

## 🏆 Best Practices Implemented

### Code Quality
- ✅ **Clean Architecture**: Separation of concerns with distinct layers
- ✅ **Type Hints**: Full type annotations for better code quality
- ✅ **Error Handling**: Custom exceptions with meaningful messages
- ✅ **Documentation**: Comprehensive docstrings and comments
- ✅ **Package Structure**: Professional Python package organization

### Database & Data
- ✅ **Database Migrations**: Schema versioning with Alembic
- ✅ **ORM Best Practices**: Proper relationships and session management
- ✅ **Data Validation**: Input validation and constraint checking
- ✅ **Session Isolation**: Proper database session lifecycle

### Testing & Quality
- ✅ **Comprehensive Testing**: 66 tests with unit and integration coverage
- ✅ **Test Isolation**: Independent test execution with fixtures
- ✅ **Professional Structure**: Industry-standard test organization
- ✅ **CI Ready**: pytest configuration for continuous integration

### User Experience
- ✅ **Beautiful CLI**: Rich formatting with colors and emojis
- ✅ **Intuitive Commands**: Clear command structure and help text
- ✅ **Error Messages**: User-friendly error handling and feedback
- ✅ **Progress Tracking**: Visual indicators for streaks and achievements

### Development Experience  
- ✅ **Virtual Environment**: Isolated dependency management
- ✅ **Package Installation**: pip-installable with console scripts
- ✅ **Development Tools**: Proper setup.py and configuration files
- ✅ **Extensible Design**: Easy to add new features and commands

## 📋 Requirements

- **Python**: 3.8+
- **Core Dependencies**:
  - SQLAlchemy 2.0+ (Database ORM)
  - Alembic 1.12+ (Database migrations)
  - Click 8.1+ (CLI framework)
  - python-dateutil 2.8+ (Date utilities)
- **Development Dependencies**:
  - pytest 7.4+ (Testing framework)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the established patterns
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Update documentation as needed
7. Submit a pull request

### Contribution Guidelines
- Follow the existing code style and architecture
- Add unit tests for new functionality
- Update integration tests for workflow changes  
- Add docstrings to new functions and classes
- Update README for significant changes

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Python, SQLAlchemy, Click, and pytest**