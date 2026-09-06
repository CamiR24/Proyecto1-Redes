# Academic AI Assistant

A console-based AI chatbot that connects to multiple **Model Context Protocol (MCP)**
servers — both official, self-developed, remote, and third-party (classmates') —
to help university students organize their academic responsibilities, plan study
sessions, and manage their coursework through natural language.

Built for **CC3067 Redes, Project 1: Uso de un protocolo existente** (Universidad
del Valle de Guatemala).

## Description

This project implements an MCP **host** (the chatbot) capable of connecting to
several MCP **servers** simultaneously, discovering their tools, and letting an
LLM (Claude, via the Anthropic API) decide when and how to use them to answer
the student's requests. It demonstrates the full MCP lifecycle: connection,
tool discovery, tool invocation, and logging — across local (stdio) and remote
(Streamable HTTP) transports.

The centerpiece is a custom-built **Academic Planner MCP server**, which
provides task management, priority calculation, workload analysis, study
scheduling, study-technique recommendations, and project decomposition —
backed by a persistent SQLite database.

## Features

- **LLM connection** via the Anthropic API (Claude), answering general
  knowledge questions from its training data.
- **Conversation memory**: the chatbot maintains context across turns within
  a session (e.g. a follow-up question correctly refers back to a previous
  answer).
- **MCP request/response logging**: every tool call to any connected MCP
  server is logged to both the console and `logs/mcp.log`, with timestamp,
  server, tool name, arguments, and result.
- **Official MCP servers**: Filesystem and Git servers from Anthropic,
  demonstrated together in a combined scenario (create a file, initialize a
  repo, commit).
- **Custom local MCP server** (Academic Planner): 8 tools covering task
  management, prioritization, scheduling, study techniques, and project
  decomposition, backed by SQLite persistence.
- **Classmates' MCP servers**: two additional local servers developed by
  other students (an HR management server and a hotel operations server),
  connected and demonstrated individually.
- **Remote MCP server**: a server deployed to Google Cloud Run, connected
  over Streamable HTTP.
- **Network analysis**: Wireshark capture of the TLS-encrypted traffic
  between the chatbot and the remote MCP server, decrypted using TLS key
  logging, identifying synchronization, request, and response messages.

## Architecture

```
                     ┌─────────────────────┐
                     │        User         │
                     └──────────┬──────────┘
                                │
                          Terminal / CLI
                                │
                     ┌──────────▼──────────┐
                     │    CHATBOT HOST     │
                     │       Python        │
                     │                     │
                     │ - Conversation      │
                     │   history           │
                     │ - MCP request/      │
                     │   response logs     │
                     │ - MCP Client        │
                     │   Manager           │
                     │ - LLM Client        │
                     └─────┬────────┬──────┘
                           │        │
                  API      │        │ MCP (stdio / HTTP)
              ┌────────────▼─┐      │
              │     Claude    │      │
              │  (Anthropic)  │      │
              └───────────────┘      │
                                     │
    ┌────────────────┬──────────────┼──────────────┬─────────────────┐
    │                 │              │              │                 │
    ▼                 ▼              ▼              ▼                 ▼
Filesystem MCP    Git MCP    Academic Planner   HR (classmate)   Hotel (classmate)
(official)       (official)      MCP (own)        MCP server        MCP server
                                     │
                                     ▼
                              SQLite database
                              (academic.db)

                                     +

                        Remote MCP Server (Google Cloud Run)
                                     │
                                Internet (HTTPS)
                                     │
                          Streamable HTTP transport
```

## Requirements

- Python 3.12+
- An Anthropic API key (with available credits)
- Node.js (required by the official Filesystem MCP server, run via `npx`)
- Internet connection (for the remote MCP server and the Anthropic API)

## Installation

```bash
git clone https://github.com/CamiR24/Proyecto1-Redes.git
cd academic-mcp-chatbot

python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Get a key at [console.anthropic.com](https://console.anthropic.com) →
API Keys → Create Key.

## Usage

Run the chatbot from the project root:

```bash
python src/main.py
```

Type your questions or requests in natural language. The LLM will decide
on its own when to call one of the available MCP tools. Type `exit`,
`quit`, or `salir` to end the session.

## MCP Servers

### Filesystem

Official Anthropic MCP server, launched via `npx`, restricted to a sandbox
directory. Provides file operations: read, write, create directories, list
directory contents, move files, search files, etc.

### Git

Official Anthropic MCP server (`mcp-server-git`), providing Git operations
(`git_status`, `git_add`, `git_commit`, `git_log`, `git_diff`, branching,
etc.) against a given repository path. Note: this version of the server does
not expose `git_init`; the repository is initialized once manually as a
setup step, after which the chatbot fully coordinates staging and commits.

### Academic Planner (own server, public repo)

Custom MCP server built for this project. Repository:
`https://github.com/CamiR24/academic-planner-mcp.git`.

8 tools, backed by a SQLite database (`academic.db`):

| Tool | Purpose |
|---|---|
| `add_academic_task` | Register a task, exam, or project with deadline, hours, difficulty, and importance |
| `get_upcoming_tasks` | List pending tasks ordered by priority score |
| `update_task_status` | Update a task's status (pendiente / en_progreso / completada) |
| `calculate_task_priority` | Return the full priority score breakdown for a task |
| `analyze_workload` | Compare hours needed vs. hours available in a date window |
| `generate_study_schedule` | Distribute available hours across pending tasks day by day, protecting tasks at risk of missing their deadline |
| `recommend_study_technique` | Recommend a study technique (spaced repetition, Feynman technique, deliberate practice) based on content type |
| `decompose_project` | Break a large project into phases with suggested sub-deadlines |

Priority formula:
```
priority_score = urgency + difficulty_weight + importance_weight + workload_weight

urgency           = min(10, max(0, 10 - days_remaining))
difficulty_weight = {"alta": 3, "media": 2, "baja": 1}[difficulty]
importance_weight = {"alta": 3, "media": 2, "baja": 1}[importance]
workload_weight   = min(estimated_hours / 2, 5)
```

Full specification, installation instructions, and usage examples are in
that repository's own README.

### Student Server 1 — HR Management (classmate)

Repository: `https://github.com/NESHGP04/mcp-server-rrhh-construccion`

HR tools for a fictional construction company: employee lookup, vacation
balances (with multi-year carry-over), overtime pay calculation (with
shift-type multipliers), payroll summaries, and employment history.

### Student Server 2 — Hotel Operations (classmate)

Repository: `https://github.com/JosFer720/hotel-mcp-server`

Hotel front-desk tools: room availability, reservation lookup, daily
summaries, room assignment (with cleaning-window validation), overbooking
risk calculation (Monte Carlo simulation), housekeeping scheduling, and
reservation creation/confirmation with printable receipts.

### Remote Server

Custom MCP server deployed to **Google Cloud Run**, connected over
**Streamable HTTP** (stateless mode, to avoid session-affinity issues across
Cloud Run instances). Exposes one tool:

| Tool | Purpose |
|---|---|
| `get_random_study_tip` | Returns a random study tip |

Repository: `https://github.com/CamiR24/academic-remote-mcp.git`
Deployed URL: `https://academic-remote-mcp-842046673187.us-central1.run.app/mcp`

## Running the Project

1. Activate the virtual environment: `source venv/bin/activate`
2. Make sure `.env` contains a valid `ANTHROPIC_API_KEY`
3. Run: `python src/main.py`
4. The chatbot connects to all configured MCP servers on startup and prints
   the list of available tools before accepting input.

## Logs

Every MCP request and response is logged to the console and to
`logs/mcp.log`, in the format:

```
[HH:MM:SS] MCP REQUEST
Server: <server-name>
Tool: <tool-name>

Arguments:
{ ... }

[HH:MM:SS] MCP RESPONSE
Server: <server-name>
Tool: <tool-name>
Status: success | error

Result:
<result>
```

## Examples

**Conversation memory:**
```
You > Who was Alan Turing?
Assistant > Alan Turing was ...
You > When was he born?
Assistant > He was born on ...
```

**Filesystem + Git (combined official servers):**
```
You > Create a directory called networks-project, create a README.md
      explaining it's a test repository, and commit it with git.
```

**Academic Planner:**
```
You > Add an exam for Networks on September 10, high difficulty, high
      importance, 4 estimated hours, course CC3067.
You > What tasks do I have pending?
You > Generate my study schedule for the next 5 days with 2 hours
      available per day.
```

**Remote server:**
```
You > Give me a study tip.
```

**Classmate servers:**
```
You > Show me all active employees.
You > How many rooms are available on September 10, 2026?
```

## Project Structure

```
academic-mcp-chatbot/
│
├── src/
│   ├── main.py
│   ├── chatbot/
│   │   ├── llm_client.py
│   │   ├── conversation.py
│   │   └── logger.py
│   │
│   └── mcp_local/
│       ├── client_manager.py
│       └── config.py
│
├── logs/
│   └── mcp.log
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```