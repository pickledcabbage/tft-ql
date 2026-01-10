# TFT-QL Codebase Summary

## Project Overview

TFT-QL is a full-stack web application that provides a custom query language for analyzing competitive Teamfight Tactics (TFT) game data. It enables players to query team compositions, champion statistics, items, traits, and receive strategic recommendations through both a CLI and web interface.

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Web Framework**: Flask (REST API) with CORS support
- **Database**: MongoDB (local via Atlas CLI)
- **Data Sources**: MetaTFT API
- **Libraries**: Pandas, Requests, PyYAML, Attrs

### Frontend
- **Framework**: React 18.3.1 with TypeScript
- **UI Components**: Material-UI (MUI) v6
- **HTTP Client**: Axios
- **State Management**: React hooks
- **Layout**: react-reflex (resizable panes)
- **Build Tool**: React Scripts

## Available Commands

1. **`top`** - Find top competitive team compositions matching given champions (filterable by level/cluster)
2. **`match`** - Match current champions to optimal endgame compositions at specific levels
3. **`comp`** - Display detailed statistics about a specific composition (augments, rerolls, levels)
4. **`trait`** - Show all champions sharing a specific trait with their costs
5. **`bi`** - Return 10 most popular items for a given champion
6. **`bis`** - Find most popular 3-item builds for a champion given component items
7. **`craft`** - Show item crafting recipes (what items craft into or components needed)
8. **`help`** - Display available commands and descriptions
9. **`warm`** - Preload all data caches for faster queries

## Architecture

```
Frontend (React/TypeScript)
    ↓ HTTP Requests
REST API Server (Flask)
    ↓
Command Interpreter + Validation Layer
    ↓
Query Language Layer (Custom QL with transforms)
    ↓
Data Query Builders (Domain-specific)
    ↓
Data Client (MetaTFT APIs + Cache)
    ↓
MongoDB (Session/Event Storage)
```

## Key Backend Components

### Core Modules

**`tft/interpreter/`** - Command execution engine
- `server.py` - Flask REST API server handling HTTP requests and session management
- `core.py` - Interactive CLI interpreter for local command execution
- `commands/` - Command implementations (12+ registered commands)
- `registry.py` - Command registration system using decorators
- `validation.py` - Input validation framework for parsing user commands

**`tft/ql/`** - Custom Query Language
- `expr.py` - Expression evaluator and query builder with transforms (Index, Map, Filter, Sort, etc.)
- `table.py` - Table rendering and field formatting for CLI output
- `util.py` - Utility functions (avg_place calculation, match scoring, trait padding)

**`tft/client/`** - Data client
- `meta.py` - MetaTFT API client with caching, multiprocessing for parallel data fetching

**`tft/queries/`** - Query builders for specific domains
- `comps.py` - Team composition queries
- `champs.py` - Champion data queries
- `items.py` - Item and crafting recipe queries
- `traits.py` - Trait data queries
- `augs.py` - Augment (ability modifier) queries
- `aliases.py` - Alias mapping from user input to API names

**`tft/config.py`** - Configuration loader for database connection, server IP/port, and file paths

## Key Frontend Components

1. **`Workspace.tsx`** - Main workspace layout with resizable panes and tool management
2. **`QLToolContainer.tsx`** - Container managing different tool views
3. **`QLToolHome.tsx`** - Session management (create/join sessions with join codes)
4. **`QLTool.tsx`** - Tool enumeration (Query, Home, Session Events)
5. **`QLToolRaw.tsx`** - Raw query execution interface
6. **`QLToolStreamer.tsx`** - Session events viewer showing user interactions
7. **`TftSet.tsx`** - TFT set information management
8. **`Config.tsx`** - Backend endpoint configuration
9. **`SessionData.tsx`** - Session state management

## Data Flow

1. User inputs query in frontend
2. Frontend sends HTTP request to Flask backend
3. Backend validates input using validation framework
4. Command is executed against cached MetaTFT API data
5. Results are rendered as formatted tables/text
6. Session events are stored in MongoDB
7. Results returned to frontend for display

## Key Design Patterns

- **Command Pattern**: Commands registered in a registry, validated and executed
- **Fluent Interface**: Query language uses method chaining (filter, map, sort, etc.)
- **Caching**: Multi-level caching (in-memory cache, local file cache, MongoDB)
- **Validation Chain**: Multiple validation classes for different entity types
- **Alias System**: CSV-based alias mapping for user-friendly input

## Session Management

- Users can create/join sessions with 4-digit join codes
- Session lifetime: 24 hours
- User actions logged to MongoDB with timestamps
- Support for anonymous and identified users

## Configuration

- YAML-based configuration (backend IP, port, database connection)
- CSV alias files for champions, items, and traits
- Configurable MetaTFT API endpoints
- Local development cache support

## Project Purpose

This is a well-structured full-stack application designed for competitive TFT players to access and analyze game statistics through an intuitive query interface. The custom query language provides flexibility in data manipulation while the Flask backend handles API coordination and session management.
