from utils.settings_loader import load_settings
from rich.console import Console
from rich import box
from rich.panel import Panel
import sys
from pyfiglet import Figlet

from handler.CommandHandler import CommandHandler as handler

console = Console()

fig = Figlet()
BANNER = fig.renderText('Trade Byte')

def show_banner():
    console.print(
        Panel.fit(
            BANNER,
            title="LAUNCH SYSTEM",
            border_style="magenta",
            padding=(1, 2)
        )
    )


def main():
    for _ in range(300):
        print(' ')
    show_banner()
    
    try:
        settings = load_settings('program.*')
    except FileNotFoundError:
        console.print("[bold red]✘ ERROR[/bold red]: No configuration files found!", style="bold red", justify="left")
        sys.exit(1)
    
    if not all(key in settings for key in ("name", "version")):
        console.print("[bold yellow]⚠ WARNING[/bold yellow]: Incomplete configuration - missing name or version", style="bold yellow")
        sys.exit(2)

    console.print(f"Console Mode.", justify="left")
    console.print(f"⚡ Initializing [bold cyan]{settings['name']}[/bold cyan]", justify="left")
    console.print(f"🌌 Running cosmic edition [bold purple]v{settings['version']}[/bold purple]\n", justify="left")
    
    console.rule("[bold green]SYSTEM ONLINE[/bold green]", style="bold green")

    handle = handler()

    while True:
        print('')
        handle.handle(input('TradeByte > '))

if __name__ == "__main__":
    main()
