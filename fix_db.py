import sqlite3

db = sqlite3.connect("visionflow.db")

print("Fixing tasks table...")

# Drop old tasks table
db.execute("DROP TABLE IF EXISTS tasks;")

# Create new tasks table
db.execute("""
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    completed INTEGER DEFAULT 0
);
""")

db.commit()
db.close()

print("Tasks table fixed successfully!")
