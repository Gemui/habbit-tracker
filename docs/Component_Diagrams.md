# Component Interaction Diagrams

## Architecture Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HABIT TRACKER APPLICATION                         │
│                              Clean Architecture                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLI LAYER                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   create    │  │  complete   │  │   delete    │  │   analyze   │      │
│  │  command    │  │   command   │  │   command   │  │   command   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│         │                │                │                │             │
│         └────────────────┼────────────────┼────────────────┘             │
│                          │                │                              │
└─────────────────────────────────────────────────────────────────────────────┘
                           │                │
                           ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                    │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │         HabitService            │  │      AnalyticsService           │  │
│  │  ┌─────────────────────────┐    │  │  ┌─────────────────────────┐    │  │
│  │  │ • create_habit()       │    │  │  │ • get_habit_statistics()│    │  │
│  │  │ • complete_habit()     │    │  │  │ • calculate_streak()    │    │  │
│  │  │ • delete_habit()       │    │  │  │ • get_activity_summary()│    │  │
│  │  │ • get_habit_by_name()  │    │  │  │ • get_longest_streak()  │    │  │
│  │  │ • get_all_habits()     │    │  │  │ • calculate_completion_rate()│  │
│  │  └─────────────────────────┘    │  │  └─────────────────────────┘    │  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
│                          │                              │                 │
│                          └──────────────┬───────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CORE LAYER                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │      Models     │  │   Exceptions    │  │    Database     │            │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │            │
│  │  │   Habit   │  │  │  │  Custom   │  │  │  │ Database  │  │            │
│  │  │   Model   │  │  │  │Exception  │  │  │  │ Manager   │  │            │
│  │  └───────────┘  │  │  │  Classes  │  │  │  └───────────┘  │            │
│  │  ┌───────────┐  │  │  └───────────┘  │  │  ┌───────────┐  │            │
│  │  │Completion │  │  │                 │  │  │ Session   │  │            │
│  │  │   Model   │  │  │                 │  │  │ Factory   │  │            │
│  │  └───────────┘  │  │                 │  │  └───────────┘  │            │
│  │  ┌───────────┐  │  │                 │  │                 │            │
│  │  │Periodicity│  │  │                 │  │                 │            │
│  │  │   Enum    │  │  │                 │  │                 │            │
│  │  └───────────┘  │  │                 │  │                 │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                    │                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE LAYER                                │
│                    ┌─────────────────────────────┐                        │
│                    │         SQLite Database     │                        │
│                    │  ┌─────────────────────┐    │                        │
│                    │  │    habits table     │    │                        │
│                    │  │  ┌───────────────┐  │    │                        │
│                    │  │  │ id (PK)       │  │    │                        │
│                    │  │  │ name (UNIQUE) │  │    │                        │
│                    │  │  │ description   │  │    │                        │
│                    │  │  │ periodicity   │  │    │                        │
│                    │  │  │ created_at    │  │    │                        │
│                    │  │  └───────────────┘  │    │                        │
│                    │  └─────────────────────┘    │                        │
│                    │  ┌─────────────────────┐    │                        │
│                    │  │  completions table  │    │                        │
│                    │  │  ┌───────────────┐  │    │                        │
│                    │  │  │ id (PK)       │  │    │                        │
│                    │  │  │ habit_id (FK) │  │    │                        │
│                    │  │  │ completed_at  │  │    │                        │
│                    │  │  └───────────────┘  │    │                        │
│                    │  └─────────────────────┘    │                        │
│                    └─────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram: Habit Creation Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HABIT CREATION PROCESS FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

    USER INPUT
        │
        ▼
┌───────────────┐
│  CLI Command  │ ◄──── python main.py create --name "Exercise" --periodicity daily
│   Validation  │
└───────┬───────┘
        │ Validates format, required fields
        ▼
┌───────────────┐
│   Service     │ ◄──── HabitService.create_habit(name, description, periodicity)
│  Layer Call   │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Business     │ ◄──── • Check name uniqueness
│  Validation   │       • Validate periodicity enum
│               │       • Sanitize input data
└───────┬───────┘
        │ Validation passed
        ▼
┌───────────────┐
│  Model        │ ◄──── habit = Habit(name=name, description=desc, 
│  Creation     │                     periodicity=period, created_at=now())
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Database     │ ◄──── session.add(habit)
│  Persistence  │       session.commit()
└───────┬───────┘
        │ Success
        ▼
┌───────────────┐
│  Success      │ ◄──── Return habit object with generated ID
│  Response     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  CLI Output   │ ◄──── ✅ Habit 'Exercise' (daily) created successfully!
│  Formatting   │
└───────────────┘

    ERROR HANDLING FLOW:
    
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ Input Validation│    │ Business Logic  │    │ Database Error  │
    │    Failure      │    │    Failure      │    │    Handling     │
    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ Format Error    │    │Custom Exception │    │ Generic Error   │
    │ Message         │    │ with Context    │    │ with Suggestion │
    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     ▼
                            ┌─────────────────┐
                            │   User-Friendly │
                            │ Error Display   │
                            └─────────────────┘
```

## Component Interaction: Analytics Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ANALYTICS GENERATION PROCESS                           │
└─────────────────────────────────────────────────────────────────────────────┘

    ANALYTICS REQUEST
           │
           ▼
    ┌─────────────┐
    │ CLI Analyze │ ◄──── python main.py analyze list-all
    │   Command   │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Analytics   │ ◄──── analytics_service.get_all_habits_statistics()
    │ Service     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐     ┌──────────────────────────────────────┐
    │ Data        │ ◄───│ FOR EACH HABIT:                      │
    │ Retrieval   │     │ 1. Get habit details                │
    │             │     │ 2. Get completion history           │
    │             │     │ 3. Calculate statistics             │
    └──────┬──────┘     └──────────────────────────────────────┘
           │
           ▼
    ┌─────────────┐     ┌──────────────────────────────────────┐
    │ Statistical │ ◄───│ CALCULATIONS:                        │
    │ Processing  │     │ • Current streak calculation        │
    │             │     │ • Longest streak analysis           │
    │             │     │ • Completion rate computation       │
    │             │     │ • Activity summary generation       │
    └──────┬──────┘     └──────────────────────────────────────┘
           │
           ▼
    ┌─────────────┐     ┌──────────────────────────────────────┐
    │ Result      │ ◄───│ RESULT STRUCTURE:                    │
    │ Formatting  │     │ {                                    │
    │             │     │   'habit_id': 1,                    │
    │             │     │   'habit_name': 'Exercise',         │
    │             │     │   'current_streak': 5,              │
    │             │     │   'longest_streak': 12,             │
    │             │     │   'completion_rate': 85.7,          │
    │             │     │   'total_completions': 25           │
    │             │     │ }                                    │
    └──────┬──────┘     └──────────────────────────────────────┘
           │
           ▼
    ┌─────────────┐     ┌──────────────────────────────────────┐
    │ CLI Output  │ ◄───│ FORMATTED OUTPUT:                    │
    │ Generation  │     │ • ID: 1                             │
    │             │     │   Name: Exercise                     │
    │             │     │   🔥 Current Streak: 5 days         │
    │             │     │   🏆 Best Streak: 12 days           │
    │             │     │   📈 Completion Rate: 85.7%         │
    └─────────────┘     └──────────────────────────────────────┘

                        PARALLEL PROCESSING FOR MULTIPLE HABITS:
                        
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   Habit 1   │    │   Habit 2   │    │   Habit 3   │    │   Habit N   │
    │ Statistics  │    │ Statistics  │    │ Statistics  │    │ Statistics  │
    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
           │                  │                  │                  │
           └──────────────────┼──────────────────┼──────────────────┘
                              │                  │
                              ▼                  ▼
                       ┌─────────────────────────────┐
                       │    Combined Results         │
                       │    Sorted by Priority       │
                       └─────────────────────────────┘
```

## Session and Transaction Management

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATABASE SESSION MANAGEMENT                             │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ DatabaseManager │
    │    Singleton    │
    └─────────┬───────┘
              │ Creates and manages
              ▼
    ┌─────────────────┐     ┌──────────────────────────────────────┐
    │ SessionFactory  │ ◄───│ Configuration:                       │
    │                 │     │ • autocommit=False                  │
    │                 │     │ • autoflush=False                   │
    │                 │     │ • expire_on_commit=False            │
    │                 │     │ • bind=engine                       │
    └─────────┬───────┘     └──────────────────────────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Session Context │ ◄──── with DatabaseManager.get_session() as session:
    │    Manager      │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐     ┌──────────────────────────────────────┐
    │ Transaction     │ ◄───│ TRANSACTION FLOW:                    │
    │ Handling        │     │ 1. Begin transaction               │
    │                 │     │ 2. Execute operations               │
    │                 │     │ 3. Validate constraints             │
    │                 │     │ 4. Commit or rollback               │
    │                 │     │ 5. Close session                    │
    └─────────┬───────┘     └──────────────────────────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Automatic       │ ◄──── Exception handling with automatic rollback
    │ Cleanup         │       Session closure in finally block
    └─────────────────┘

    ERROR HANDLING AND RECOVERY:
    
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ Constraint      │    │ Connection      │    │ Business Logic  │
    │ Violation       │    │ Error           │    │ Error           │
    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ Rollback +      │    │ Retry Logic +   │    │ Custom Exception│
    │ Custom Exception│    │ Error Logging   │    │ + User Message  │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Testing Architecture Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TESTING STRATEGY OVERVIEW                          │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │   UNIT TESTS    │     │ INTEGRATION     │     │   FIXTURE       │
    │   (38 tests)    │     │     TESTS       │     │  MANAGEMENT     │
    │                 │     │   (28 tests)    │     │                 │
    └─────────┬───────┘     └─────────┬───────┘     └─────────┬───────┘
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │ • Model Tests   │     │ • CLI Tests     │     │ • Test Database │
    │ • Service Tests │     │ • Workflow Tests│     │ • Sample Data   │
    │ • Utility Tests │     │ • End-to-End    │     │ • Mock Objects  │
    └─────────┬───────┘     └─────────┬───────┘     └─────────┬───────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │ Test Execution  │
                            │    Pipeline     │
                            └─────────┬───────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │ Coverage Report │
                            │ Quality Metrics │
                            └─────────────────┘

    TEST ISOLATION STRATEGY:
    
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                        PER-TEST ISOLATION                               │
    │                                                                         │
    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
    │  │ Test Setup  │    │ Test        │    │ Test        │                │
    │  │ • Fresh DB  │ ───► Execution  │ ───► Cleanup     │                │
    │  │ • Sample    │    │ • Isolated  │    │ • DB Reset  │                │
    │  │   Data      │    │   State     │    │ • Memory    │                │
    │  │ • Mocks     │    │             │    │   Cleanup   │                │
    │  └─────────────┘    └─────────────┘    └─────────────┘                │
    └─────────────────────────────────────────────────────────────────────────┘
```

These diagrams provide a comprehensive visual representation of the component interactions, data flows, and architectural patterns implemented in the Habit Tracker application, supporting the conceptual analysis document with clear technical illustrations.






