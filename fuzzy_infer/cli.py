"""
Command-line interface for FuzzyInfer.

Provides an interactive CLI for working with fuzzy inference systems.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Optional

try:
    import typer
    from rich import print
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
except ImportError:
    print("CLI dependencies not installed. Install with: pip install fuzzy-infer[cli]")
    sys.exit(1)

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    USE_PROMPT_TOOLKIT = True
except ImportError:
    USE_PROMPT_TOOLKIT = False

from fuzzy_infer import Fact, FuzzyInfer, Rule
from fuzzy_infer.serialization import FuzzyInferSerializer
from fuzzy_infer.merge import KnowledgeBaseMerger, MergeStrategy

app = typer.Typer(
    name="fuzzy-infer",
    help="FuzzyInfer - A Fuzzy Forward-Chaining Production Rule System",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    knowledge_base: Path = typer.Argument(
        ...,
        help="Path to knowledge base file (JSON or YAML)",
        exists=True,
    ),
    query_predicate: Optional[str] = typer.Option(
        None, "--query", "-q", help="Query predicate to search for after inference"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    Run inference on a knowledge base and optionally query results.
    """
    console.print(f"[cyan]Loading knowledge base from:[/cyan] {knowledge_base}")

    try:
        inf = FuzzyInferSerializer.load_from_file(knowledge_base)
        console.print(f"[green]✓[/green] Loaded {len(inf.facts)} facts and {len(inf.rules)} rules")
    except Exception as e:
        console.print(f"[red]Error loading knowledge base:[/red] {e}")
        raise typer.Exit(1)

    # Run inference
    console.print("[cyan]Running inference...[/cyan]")
    initial_facts = len(inf.facts)

    try:
        inf.run()
        new_facts = len(inf.facts) - initial_facts
        console.print(f"[green]✓[/green] Inference complete. Generated {new_facts} new facts.")
    except Exception as e:
        console.print(f"[red]Error during inference:[/red] {e}")
        raise typer.Exit(1)

    # Query if requested
    if query_predicate:
        results = inf.query(query_predicate)

        if results:
            table = Table(title=f"Query Results: {query_predicate}")
            table.add_column("Arguments", style="cyan")
            table.add_column("Degree", style="magenta")

            for fact in results:
                args_str = str(fact.args)
                degree_str = f"{fact.degree:.3f}"
                table.add_row(args_str, degree_str)

            console.print(table)
        else:
            console.print(f"[yellow]No facts found for predicate:[/yellow] {query_predicate}")

    # Save output if requested
    if output:
        try:
            FuzzyInferSerializer.save_to_file(inf, output)
            console.print(f"[green]✓[/green] Results saved to: {output}")
        except Exception as e:
            console.print(f"[red]Error saving results:[/red] {e}")
            raise typer.Exit(1)


@app.command()
def interactive():
    """
    Start an interactive fuzzy inference session.
    """
    console.print(
        Panel.fit(
            "[bold cyan]FuzzyInfer Interactive Session[/bold cyan]\n"
            "Type 'help' for available commands or 'exit' to quit.",
            border_style="cyan",
        )
    )

    inf = FuzzyInfer()
    
    # Initialize command history
    command_history = []
    
    # Setup prompt session with history and auto-suggestions if available
    if USE_PROMPT_TOOLKIT:
        # Create history file in user's home directory
        history_file = Path.home() / ".fuzzy_infer_history"
        
        # Define completions for common commands
        commands = [
            'fact', 'facts', 'rule', 'rules', 'query', 'run', 'clear',
            'save', 'load', 'help', 'exit', 'quit', 'cd', 'ls', 'pwd', 'history'
        ]
        completer = WordCompleter(commands, ignore_case=True)
        
        session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=completer,
        )
    else:
        session = None

    while True:
        try:
            # Get current working directory for prompt
            cwd = os.getcwd()
            short_cwd = Path(cwd).name or cwd
            
            if USE_PROMPT_TOOLKIT and session:
                prompt_text = f"[{short_cwd}] fuzzy> "
                command = session.prompt(prompt_text).strip()
            else:
                command = console.input(f"[bold cyan][{short_cwd}] fuzzy>[/bold cyan] ").strip()
            
            if not command:
                continue
            
            # Add to command history
            command_history.append(command)

            if command.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if command.lower() == "help":
                _show_help()
                continue
            
            # Handle file system commands
            if command.lower() == "pwd":
                console.print(f"[cyan]Current directory:[/cyan] {os.getcwd()}")
                continue
            
            if command.lower().startswith("cd "):
                path = command[3:].strip()
                _change_directory(path)
                continue
            
            if command.lower() in ["ls", "dir"]:
                _list_directory()
                continue
            
            if command.lower().startswith("ls "):
                path = command[3:].strip()
                _list_directory(path)
                continue
            
            if command.lower() == "history":
                _show_history(command_history)
                continue

            _process_command(inf, command)

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def _change_directory(path: str):
    """Change the current working directory."""
    try:
        # Expand ~ to home directory
        path = os.path.expanduser(path)
        # Convert to absolute path
        path = os.path.abspath(path)
        os.chdir(path)
        console.print(f"[green]✓[/green] Changed to: {os.getcwd()}")
    except FileNotFoundError:
        console.print(f"[red]Directory not found:[/red] {path}")
    except PermissionError:
        console.print(f"[red]Permission denied:[/red] {path}")
    except Exception as e:
        console.print(f"[red]Error changing directory:[/red] {e}")


def _list_directory(path: str = "."):
    """List contents of a directory."""
    try:
        # Expand ~ and convert to Path
        path = os.path.expanduser(path)
        path_obj = Path(path)
        
        if not path_obj.exists():
            console.print(f"[red]Path does not exist:[/red] {path}")
            return
        
        if not path_obj.is_dir():
            console.print(f"[red]Not a directory:[/red] {path}")
            return
        
        # Get directory contents
        items = sorted(path_obj.iterdir())
        
        if not items:
            console.print("[yellow]Empty directory[/yellow]")
            return
        
        # Separate directories and files
        dirs = []
        files = []
        
        for item in items:
            if item.is_dir():
                dirs.append(f"[bold blue]{item.name}/[/bold blue]")
            else:
                # Color code by extension
                if item.suffix in [".json", ".yaml", ".yml"]:
                    files.append(f"[green]{item.name}[/green]")
                elif item.suffix in [".py"]:
                    files.append(f"[yellow]{item.name}[/yellow]")
                else:
                    files.append(item.name)
        
        # Print directories first, then files
        all_items = dirs + files
        
        # Print in columns
        if all_items:
            # Calculate column width
            max_len = max(len(item.replace("[bold blue]", "").replace("[/bold blue]", "")
                             .replace("[green]", "").replace("[/green]", "")
                             .replace("[yellow]", "").replace("[/yellow]", "")
                             .replace("/", "")) for item in all_items)
            cols = min(4, max(1, 80 // (max_len + 2)))
            
            for i in range(0, len(all_items), cols):
                row = all_items[i:i+cols]
                console.print("  ".join(row))
                
    except PermissionError:
        console.print(f"[red]Permission denied:[/red] {path}")
    except Exception as e:
        console.print(f"[red]Error listing directory:[/red] {e}")


def _show_history(command_history: List[str]):
    """Show command history."""
    if not command_history:
        console.print("[yellow]No commands in history.[/yellow]")
        return
    
    console.print("[bold cyan]Command History:[/bold cyan]")
    for i, cmd in enumerate(command_history[-20:], 1):  # Show last 20 commands
        console.print(f"  {i:3d}. {cmd}")


def _show_help():
    """Show help for interactive commands."""
    help_text = """
[bold cyan]Available Commands:[/bold cyan]

[yellow]Facts & Rules:[/yellow]
  fact <predicate> <args...> [degree]  - Add a fact
  facts                                 - List all facts
  query <predicate> [args...]          - Query facts
  rule <json>                          - Add a rule (JSON format)
  rules                                - List all rules

[yellow]Inference:[/yellow]
  run                                  - Run inference
  clear                                - Clear all facts and rules

[yellow]File Operations:[/yellow]
  load <file>                          - Load knowledge base
  save <file>                          - Save knowledge base
  merge <file> [strategy]              - Merge another KB (union/smart/override)

[yellow]File System:[/yellow]
  pwd                                  - Show current directory
  cd <path>                           - Change directory
  ls [path]                           - List directory contents

[yellow]Session:[/yellow]
  history                             - Show command history
  help                                - Show this help
  exit/quit                           - Exit the session
"""
    console.print(help_text)


def _process_command(inf: FuzzyInfer, command: str):
    """Process a single command."""
    parts = command.split()
    cmd = parts[0].lower()

    if cmd == "fact":
        _add_fact(inf, parts[1:])
    elif cmd == "facts":
        _list_facts(inf)
    elif cmd == "query":
        _query_facts(inf, parts[1:])
    elif cmd == "rule":
        _add_rule(inf, " ".join(parts[1:]))
    elif cmd == "rules":
        _list_rules(inf)
    elif cmd == "run":
        _run_inference(inf)
    elif cmd == "clear":
        inf.clear()
        console.print("[green]✓[/green] Knowledge base cleared.")
    elif cmd == "load":
        if len(parts) > 1:
            _load_kb(inf, parts[1])
        else:
            console.print("[red]Usage: load <file>[/red]")
    elif cmd == "save":
        if len(parts) > 1:
            _save_kb(inf, parts[1])
        else:
            console.print("[red]Usage: save <file>[/red]")
    elif cmd == "merge":
        if len(parts) > 1:
            strategy = parts[2] if len(parts) > 2 else "union"
            _merge_kb(inf, parts[1], strategy)
        else:
            console.print("[red]Usage: merge <file> [strategy][/red]")
            console.print("Strategies: union, smart, override, complement, weighted")
    else:
        console.print(f"[red]Unknown command:[/red] {cmd}")


def _add_fact(inf: FuzzyInfer, args: List[str]):
    """Add a fact to the knowledge base."""
    if len(args) < 2:
        console.print("[red]Usage: fact <predicate> <args...> [degree][/red]")
        return

    predicate = args[0]

    # Check if last argument is a degree
    degree = 1.0
    fact_args = args[1:]

    if fact_args:
        try:
            degree = float(fact_args[-1])
            if 0.0 <= degree <= 1.0:
                fact_args = fact_args[:-1]
            else:
                degree = 1.0
        except ValueError:
            pass

    fact = Fact(predicate, fact_args, degree)
    inf.add_fact(fact)
    console.print(f"[green]✓[/green] Added fact: {predicate}{fact_args} [degree={degree:.3f}]")


def _list_facts(inf: FuzzyInfer):
    """List all facts in the knowledge base."""
    facts = inf.get_facts()

    if not facts:
        console.print("[yellow]No facts in knowledge base.[/yellow]")
        return

    table = Table(title="Facts in Knowledge Base")
    table.add_column("Predicate", style="cyan")
    table.add_column("Arguments", style="white")
    table.add_column("Degree", style="magenta")

    for fact in facts:
        table.add_row(fact.predicate, str(fact.args), f"{fact.degree:.3f}")

    console.print(table)


def _query_facts(inf: FuzzyInfer, args: List[str]):
    """Query facts from the knowledge base."""
    if not args:
        console.print("[red]Usage: query <predicate> [args...][/red]")
        return

    predicate = args[0]
    query_args = args[1:] if len(args) > 1 else None

    results = inf.query(predicate, query_args)

    if results:
        table = Table(title=f"Query Results: {predicate}")
        table.add_column("Arguments", style="cyan")
        table.add_column("Degree", style="magenta")

        for fact in results:
            table.add_row(str(fact.args), f"{fact.degree:.3f}")

        console.print(table)
    else:
        console.print("[yellow]No facts found for query.[/yellow]")


def _add_rule(inf: FuzzyInfer, rule_json: str):
    """Add a rule from JSON format."""
    try:
        rule_dict = json.loads(rule_json)
        rule = Rule.from_dict(rule_dict)
        inf.add_rule(rule)
        console.print("[green]✓[/green] Rule added successfully.")
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON format for rule.[/red]")
    except Exception as e:
        console.print(f"[red]Error adding rule:[/red] {e}")


def _list_rules(inf: FuzzyInfer):
    """List all rules in the knowledge base."""
    rules = inf.get_rules()

    if not rules:
        console.print("[yellow]No rules in knowledge base.[/yellow]")
        return

    for i, rule in enumerate(rules, 1):
        rule_json = json.dumps(rule.to_dict(), indent=2)
        syntax = Syntax(rule_json, "json", theme="monokai", line_numbers=False)

        panel = Panel(
            syntax,
            title=f"Rule {i}" + (f" - {rule.name}" if rule.name else ""),
            border_style="cyan",
        )
        console.print(panel)


def _run_inference(inf: FuzzyInfer):
    """Run the inference engine."""
    initial_facts = len(inf.facts)
    console.print("[cyan]Running inference...[/cyan]")

    try:
        inf.run()
        new_facts = len(inf.facts) - initial_facts
        console.print(f"[green]✓[/green] Inference complete. Generated {new_facts} new facts.")
    except Exception as e:
        console.print(f"[red]Error during inference:[/red] {e}")


def _load_kb(inf: FuzzyInfer, filepath: str):
    """Load knowledge base from file."""
    try:
        loaded_inf = FuzzyInferSerializer.load_from_file(filepath)
        inf.facts = loaded_inf.facts
        inf.rules = loaded_inf.rules
        console.print(
            f"[green]✓[/green] Loaded {len(inf.facts)} facts and {len(inf.rules)} rules from {filepath}"
        )
    except Exception as e:
        console.print(f"[red]Error loading file:[/red] {e}")


def _save_kb(inf: FuzzyInfer, filepath: str):
    """Save knowledge base to file."""
    try:
        FuzzyInferSerializer.save_to_file(inf, filepath)
        console.print(f"[green]✓[/green] Saved knowledge base to {filepath}")
    except Exception as e:
        console.print(f"[red]Error saving file:[/red] {e}")


def _merge_kb(inf: FuzzyInfer, filepath: str, strategy_name: str):
    """Merge another knowledge base into current one."""
    try:
        # Load the other KB
        other_kb = FuzzyInferSerializer.load_from_file(filepath)
        
        # Parse strategy
        try:
            strategy = MergeStrategy[strategy_name.upper()]
        except KeyError:
            console.print(f"[red]Unknown strategy:[/red] {strategy_name}")
            console.print("Available: union, smart, override, complement, weighted")
            return
        
        # Perform merge
        merger = KnowledgeBaseMerger(threshold=0.5)
        
        if strategy == MergeStrategy.WEIGHTED:
            # For weighted, use equal weights by default
            merged = merger.merge(inf, other_kb, strategy, weights=(0.5, 0.5))
        else:
            merged = merger.merge(inf, other_kb, strategy, auto_resolve=True)
        
        # Show conflict report for smart merge
        if strategy == MergeStrategy.SMART and merger.conflicts:
            console.print("\n[yellow]Conflict Report:[/yellow]")
            report = merger.get_conflict_report()
            console.print(report)
        
        # Update current KB with merged result
        inf.clear()
        for fact in merged.get_facts():
            inf.add_fact(fact)
        for rule in merged.get_rules():
            inf.add_rule(rule)
        
        console.print(f"[green]✓[/green] Merged {filepath} using {strategy_name} strategy")
        console.print(f"  Facts: {len(inf.get_facts())}, Rules: {len(inf.get_rules())}")
        
    except FileNotFoundError:
        console.print(f"[red]File not found:[/red] {filepath}")
    except Exception as e:
        console.print(f"[red]Error merging knowledge base:[/red] {e}")


@app.command()
def validate(
    knowledge_base: Path = typer.Argument(
        ...,
        help="Path to knowledge base file to validate",
        exists=True,
    ),
):
    """
    Validate a knowledge base file for syntax and consistency.
    """
    console.print(f"[cyan]Validating:[/cyan] {knowledge_base}")

    try:
        inf = FuzzyInferSerializer.load_from_file(knowledge_base)

        # Validation checks
        issues = []

        # Check for empty KB
        if len(inf.facts) == 0 and len(inf.rules) == 0:
            issues.append("Knowledge base is empty")

        # Check for rules without conditions
        for i, rule in enumerate(inf.get_rules()):
            if not rule.conditions:
                issues.append(f"Rule {i+1} has no conditions")
            if not rule.actions:
                issues.append(f"Rule {i+1} has no actions")

        # Check for invalid degrees
        for fact in inf.get_facts():
            if not (0.0 <= fact.degree <= 1.0):
                issues.append(f"Fact {fact.predicate}{fact.args} has invalid degree: {fact.degree}")

        if issues:
            console.print("[yellow]Validation issues found:[/yellow]")
            for issue in issues:
                console.print(f"  [yellow]⚠[/yellow] {issue}")
        else:
            console.print("[green]✓[/green] Knowledge base is valid!")
            console.print(f"  - Facts: {len(inf.facts)}")
            console.print(f"  - Rules: {len(inf.rules)}")

    except Exception as e:
        console.print(f"[red]✗ Validation failed:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
