#!/usr/bin/env python3
"""
Database Migration Script for Mermaid Render

This script manages database schema migrations and data management
for the Mermaid Render project.

Usage:
    python scripts/db-migrate.py <command> [options]

Commands:
    init        - Initialize migration system
    create      - Create a new migration
    migrate     - Apply pending migrations
    rollback    - Rollback last migration
    status      - Show migration status
    reset       - Reset database (DANGEROUS)
    seed        - Seed database with test data
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DatabaseMigrator:
    """Manages database migrations for the project."""
    
    def __init__(self, project_root: Optional[Path] = None, db_url: Optional[str] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.migrations_dir = self.project_root / "migrations"
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///mermaid_render.db")
        
        # For simplicity, we'll use SQLite for this example
        # In production, this would support PostgreSQL, MySQL, etc.
        if self.db_url.startswith("sqlite:///"):
            self.db_path = self.project_root / self.db_url.replace("sqlite:///", "")
        else:
            self.db_path = self.project_root / "mermaid_render.db"
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message."""
        prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        print(f"{prefix.get(level, '📝')} {message}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(str(self.db_path))
    
    def init_migration_system(self) -> bool:
        """Initialize the migration system."""
        self.log("Initializing migration system...")
        
        # Create migrations directory
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Create migrations table
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum TEXT NOT NULL
                )
            """)
            conn.commit()
        
        # Create initial migration if none exist
        if not list(self.migrations_dir.glob("*.sql")):
            self.create_migration("initial_schema", """
-- Initial schema for Mermaid Render
CREATE TABLE IF NOT EXISTS cache_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    size INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(key);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at);

CREATE TABLE IF NOT EXISTS render_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_session_id ON render_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_id ON render_sessions(user_id);

CREATE TABLE IF NOT EXISTS render_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    diagram_type TEXT NOT NULL,
    diagram_content TEXT NOT NULL,
    output_format TEXT NOT NULL,
    render_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    FOREIGN KEY (session_id) REFERENCES render_sessions(session_id)
);

CREATE INDEX IF NOT EXISTS idx_history_session ON render_history(session_id);
CREATE INDEX IF NOT EXISTS idx_history_type ON render_history(diagram_type);
CREATE INDEX IF NOT EXISTS idx_history_created ON render_history(created_at);
            """)
        
        self.log("Migration system initialized", "SUCCESS")
        return True
    
    def create_migration(self, name: str, content: Optional[str] = None) -> str:
        """Create a new migration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"{timestamp}_{name}"
        filename = f"{version}.sql"
        migration_path = self.migrations_dir / filename
        
        if content is None:
            content = f"""-- Migration: {name}
-- Created: {datetime.now().isoformat()}

-- Add your migration SQL here
-- Example:
-- CREATE TABLE example (
--     id INTEGER PRIMARY KEY,
--     name TEXT NOT NULL
-- );

-- Rollback SQL (optional, add after -- ROLLBACK comment):
-- ROLLBACK
-- DROP TABLE IF EXISTS example;
"""
        
        migration_path.write_text(content)
        self.log(f"Created migration: {filename}", "SUCCESS")
        return version
    
    def get_migration_checksum(self, migration_path: Path) -> str:
        """Calculate checksum for a migration file."""
        content = migration_path.read_text()
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_pending_migrations(self) -> List[Tuple[str, Path]]:
        """Get list of pending migrations."""
        # Get applied migrations
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY version")
            applied = {row[0] for row in cursor.fetchall()}
        
        # Get all migration files
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        # Filter to pending migrations
        pending = []
        for migration_file in migration_files:
            version = migration_file.stem
            if version not in applied:
                pending.append((version, migration_file))
        
        return pending
    
    def apply_migration(self, version: str, migration_path: Path) -> bool:
        """Apply a single migration."""
        self.log(f"Applying migration: {version}")
        
        try:
            content = migration_path.read_text()
            checksum = self.get_migration_checksum(migration_path)
            
            # Split content at ROLLBACK comment if present
            sql_parts = content.split("-- ROLLBACK")
            migration_sql = sql_parts[0].strip()
            
            with self.get_connection() as conn:
                # Execute migration SQL
                conn.executescript(migration_sql)
                
                # Record migration
                conn.execute("""
                    INSERT INTO schema_migrations (version, name, checksum)
                    VALUES (?, ?, ?)
                """, (version, migration_path.name, checksum))
                
                conn.commit()
            
            self.log(f"Applied migration: {version}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to apply migration {version}: {e}", "ERROR")
            return False
    
    def migrate(self) -> bool:
        """Apply all pending migrations."""
        pending = self.get_pending_migrations()
        
        if not pending:
            self.log("No pending migrations", "INFO")
            return True
        
        self.log(f"Found {len(pending)} pending migrations")
        
        success_count = 0
        for version, migration_path in pending:
            if self.apply_migration(version, migration_path):
                success_count += 1
            else:
                break
        
        if success_count == len(pending):
            self.log(f"Successfully applied {success_count} migrations", "SUCCESS")
            return True
        else:
            self.log(f"Applied {success_count}/{len(pending)} migrations", "WARNING")
            return False
    
    def rollback_last_migration(self) -> bool:
        """Rollback the last applied migration."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT version, name FROM schema_migrations 
                ORDER BY applied_at DESC LIMIT 1
            """)
            result = cursor.fetchone()
            
            if not result:
                self.log("No migrations to rollback", "WARNING")
                return False
            
            version, name = result
            migration_path = self.migrations_dir / f"{version}.sql"
            
            if not migration_path.exists():
                self.log(f"Migration file not found: {migration_path}", "ERROR")
                return False
            
            try:
                content = migration_path.read_text()
                
                # Look for rollback SQL
                if "-- ROLLBACK" in content:
                    rollback_sql = content.split("-- ROLLBACK")[1].strip()
                    
                    if rollback_sql:
                        self.log(f"Rolling back migration: {version}")
                        conn.executescript(rollback_sql)
                        
                        # Remove from migrations table
                        conn.execute("DELETE FROM schema_migrations WHERE version = ?", (version,))
                        conn.commit()
                        
                        self.log(f"Rolled back migration: {version}", "SUCCESS")
                        return True
                    else:
                        self.log(f"No rollback SQL found for migration: {version}", "ERROR")
                        return False
                else:
                    self.log(f"No rollback section found for migration: {version}", "ERROR")
                    return False
                    
            except Exception as e:
                self.log(f"Failed to rollback migration {version}: {e}", "ERROR")
                return False
    
    def get_migration_status(self) -> Dict:
        """Get migration status."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT version, name, applied_at FROM schema_migrations 
                ORDER BY version
            """)
            applied = cursor.fetchall()
        
        pending = self.get_pending_migrations()
        
        return {
            "applied": applied,
            "pending": [(v, str(p)) for v, p in pending],
            "total_applied": len(applied),
            "total_pending": len(pending)
        }
    
    def reset_database(self, confirm: bool = False) -> bool:
        """Reset the database (DANGEROUS)."""
        if not confirm:
            self.log("Database reset requires confirmation. Use --confirm flag.", "WARNING")
            return False
        
        self.log("Resetting database...", "WARNING")
        
        try:
            # Remove database file
            if self.db_path.exists():
                self.db_path.unlink()
            
            # Reinitialize
            self.init_migration_system()
            self.migrate()
            
            self.log("Database reset completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to reset database: {e}", "ERROR")
            return False
    
    def seed_database(self) -> bool:
        """Seed database with test data."""
        self.log("Seeding database with test data...")
        
        try:
            with self.get_connection() as conn:
                # Add sample cache entries
                conn.execute("""
                    INSERT OR IGNORE INTO cache_entries (key, value, size)
                    VALUES 
                        ('test_diagram_1', '<svg>Test SVG 1</svg>', 100),
                        ('test_diagram_2', '<svg>Test SVG 2</svg>', 150),
                        ('test_diagram_3', '<svg>Test SVG 3</svg>', 200)
                """)
                
                # Add sample session
                conn.execute("""
                    INSERT OR IGNORE INTO render_sessions (session_id, user_id, metadata)
                    VALUES ('test_session_1', 'test_user', '{"browser": "chrome"}')
                """)
                
                # Add sample render history
                conn.execute("""
                    INSERT OR IGNORE INTO render_history 
                    (session_id, diagram_type, diagram_content, output_format, render_time_ms)
                    VALUES 
                        ('test_session_1', 'flowchart', 'flowchart TD\nA-->B', 'svg', 150),
                        ('test_session_1', 'sequence', 'sequenceDiagram\nA->>B: Hello', 'svg', 200)
                """)
                
                conn.commit()
            
            self.log("Database seeded successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to seed database: {e}", "ERROR")
            return False


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Database migration manager for Mermaid Render")
    
    parser.add_argument("command", choices=[
        "init", "create", "migrate", "rollback", "status", "reset", "seed"
    ], help="Migration command to run")
    
    parser.add_argument("--name", "-n", help="Migration name (for create command)")
    parser.add_argument("--db-url", help="Database URL")
    parser.add_argument("--confirm", action="store_true", help="Confirm dangerous operations")
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(db_url=args.db_url)
    
    if args.command == "init":
        success = migrator.init_migration_system()
    elif args.command == "create":
        if not args.name:
            print("Error: --name is required for create command")
            sys.exit(1)
        migrator.create_migration(args.name)
        success = True
    elif args.command == "migrate":
        success = migrator.migrate()
    elif args.command == "rollback":
        success = migrator.rollback_last_migration()
    elif args.command == "status":
        status = migrator.get_migration_status()
        print(f"\n📊 Migration Status:")
        print(f"  Applied: {status['total_applied']}")
        print(f"  Pending: {status['total_pending']}")
        
        if status['applied']:
            print(f"\n✅ Applied Migrations:")
            for version, name, applied_at in status['applied']:
                print(f"  {version}: {name} (applied: {applied_at})")
        
        if status['pending']:
            print(f"\n⏳ Pending Migrations:")
            for version, path in status['pending']:
                print(f"  {version}: {Path(path).name}")
        
        success = True
    elif args.command == "reset":
        success = migrator.reset_database(args.confirm)
    elif args.command == "seed":
        success = migrator.seed_database()
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
