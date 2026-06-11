#!/usr/bin/env python3
"""
SpectraLens - WiFi Frequency Visualization Tool
================================================
Mengubah frekuensi WiFi menjadi representasi visual (2D/3D).

Usage:
    python main.py scan                          # Scan WiFi networks
    python main.py visualize <input.csv>         # Visualize from CSV data
    python main.py interactive                   # Interactive mode

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
License : MIT
"""

import argparse
import sys
import os
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

VERSION = "1.0.0"


def print_banner():
    """Display SpectraLens ASCII banner."""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
   +----------------------------------------------+
   |     ########  ######  ########  ######  ########|
   |     ##      ##      ##      ##      ##      |
   |     ######## ##      ######   ##      ######   |
   |          ## ##      ##      ##      ##      |
   |     ########  ######  ########  ######  ########|
   +----------------------------------------------+
{Fore.YELLOW}
   [*] SpectraLens v{VERSION}
   [*] WiFi Frequency Visualization Tool
   [*] "Making the invisible visible, one frequency at a time."
{Style.RESET_ALL}
    """
    print(banner)


def cmd_scan(args):
    """Command: Scan WiFi networks and display RSSI data."""
    print(f"{Fore.CYAN}[*] Initializing WiFi scanner...{Style.RESET_ALL}")
    try:
        from scanner.wifi_scanner import WiFiScanner
        scanner = WiFiScanner()
        networks = scanner.scan()
        
        if not networks:
            print(f"{Fore.YELLOW}[!] No WiFi networks found.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}[+] Found {len(networks)} networks:{Style.RESET_ALL}")
        print(f"{'SSID':<30} {'BSSID':<20} {'Signal (dBm)':<15} {'Channel':<10}")
        print("-" * 75)
        for net in networks:
            print(f"{net['ssid']:<30} {net['bssid']:<20} {net['rssi']:<15} {net['channel']:<10}")
            
    except ImportError as e:
        print(f"{Fore.RED}[!] Scanner module not available: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Try installing dependencies: pip install -r requirements.txt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Scan failed: {e}{Style.RESET_ALL}")


def cmd_visualize(args):
    """Command: Visualize WiFi signal data from CSV file."""
    if not os.path.exists(args.input):
        print(f"{Fore.RED}[!] File not found: {args.input}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}[*] Loading data from: {args.input}{Style.RESET_ALL}")
    try:
        import pandas as pd
        data = pd.read_csv(args.input)
        
        required_cols = ['x', 'y', 'rssi']
        if not all(col in data.columns for col in required_cols):
            print(f"{Fore.RED}[!] CSV must contain columns: {', '.join(required_cols)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Found columns: {', '.join(data.columns)}{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[+] Loaded {len(data)} data points{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Generating visualizations...{Style.RESET_ALL}")
        
        # Run interpolation
        from interpolation.idw import IDWInterpolator
        from interpolation.grid_builder import GridBuilder
        
        points = data[['x', 'y']].values
        values = data['rssi'].values
        
        interpolator = IDWInterpolator(power=2, k=5)
        interpolator.fit(points, values)
        
        grid = GridBuilder(points)
        grid_x, grid_y = grid.create_grid(resolution=50)
        grid_z = interpolator.interpolate(grid_x, grid_y)
        
        # Generate visualizations
        from visualization.heatmap_2d import Heatmap2D
        from visualization.surface_3d import Surface3D
        
        heatmap = Heatmap2D()
        heatmap.plot(points, values, grid_x, grid_y, grid_z, 
                    title=f"WiFi Signal Heatmap - {args.ssid if args.ssid else 'Unknown'}")
        
        surface = Surface3D()
        surface.plot(grid_x, grid_y, grid_z,
                    title=f"WiFi Signal 3D Surface - {args.ssid if args.ssid else 'Unknown'}")
        
        print(f"{Fore.GREEN}[+] Visualizations generated successfully!{Style.RESET_ALL}")
        
    except ImportError as e:
        print(f"{Fore.RED}[!] Module import failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Try installing dependencies: pip install -r requirements.txt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Visualization failed: {e}{Style.RESET_ALL}")


def cmd_gui(args):
    """Command: Launch the SpectraLens GUI application."""
    print(f"{Fore.CYAN}[*] Launching SpectraLens GUI...{Style.RESET_ALL}")
    try:
        from gui.app import run_app
        run_app()
    except ImportError as e:
        print(f"{Fore.RED}[!] GUI module not available: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Try installing dependencies: pip install -r requirements.txt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] GUI launch failed: {e}{Style.RESET_ALL}")


def cmd_realtime(args):
    """Command: Real-time WiFi signal visualization."""
    print(f"{Fore.CYAN}[*] Starting realtime WiFi monitor...{Style.RESET_ALL}")
    try:
        if args.terminal:
            from visualization.realtime import SimpleBarVisualizer
            viz = SimpleBarVisualizer()
            viz.display(count=0, interval=args.interval)
        else:
            from visualization.realtime import RealtimeVisualizer
            viz = RealtimeVisualizer(interval=args.interval)
            viz.start()
    except ImportError as e:
        print(f"{Fore.RED}[!] Module import failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Try installing dependencies: pip install -r requirements.txt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Realtime visualization failed: {e}{Style.RESET_ALL}")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="SpectraLens - WiFi Frequency Visualization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scan
  python main.py visualize data/measurements.csv --ssid MyWiFi
  python main.py realtime
  python main.py realtime --terminal
  python main.py realtime --interval 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan WiFi networks')
    
    # Visualize command
    vis_parser = subparsers.add_parser('visualize', help='Visualize signal data from CSV')
    vis_parser.add_argument('input', help='Path to CSV file (columns: x, y, rssi)')
    vis_parser.add_argument('--ssid', default='Unknown', help='SSID name for display')
    vis_parser.add_argument('--resolution', type=int, default=50, help='Grid resolution (default: 50)')
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Launch SpectraLens GUI application')
    
    # Realtime command
    rt_parser = subparsers.add_parser('realtime', help='Real-time WiFi signal visualization')
    rt_parser.add_argument('--terminal', action='store_true', help='Use terminal-based display (no GUI)')
    rt_parser.add_argument('--interval', type=int, default=3, help='Refresh interval in seconds (default: 3)')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Route commands
    if args.command == 'scan':
        cmd_scan(args)
    elif args.command == 'visualize':
        cmd_visualize(args)
    elif args.command == 'gui':
        cmd_gui(args)
    elif args.command == 'realtime':
        cmd_realtime(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
