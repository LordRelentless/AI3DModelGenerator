#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import argparse

# Add project root to sys.path to ensure absolute imports work
PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import Config
from backend.api.app import run_server

def main():
    parser = argparse.ArgumentParser(description='AI 3D Model Generator')
    parser.add_argument('--mode', choices=['api', 'gui', 'web'], default='api',
                       help='Run mode: api (server only), gui (desktop app), web (web viewer)')
    parser.add_argument('--host', default=None, help='API host')
    parser.add_argument('--port', type=int, default=None, help='API port')
    
    args = parser.parse_args()
    
    if args.host:
        Config.API_HOST = args.host
    if args.port:
        Config.API_PORT = args.port
    
    print("=" * 60)
    print("AI 3D Model Generator")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Device: Config.DEVICE = 'auto'")
    print(f"Server bind: {Config.SERVER_HOST}:{Config.API_PORT}")
    print(f"Client connects to: {Config.API_HOST}:{Config.API_PORT}")
    print(f"Output directory: {Config.OUTPUT_DIR}")
    print(f"Models directory: {Config.MODELS_DIR}")
    print("=" * 60)
    
    if args.mode == 'api':
        print("Starting API server only...")
        run_server()
    
    elif args.mode == 'gui':
        print("Starting GUI application...")
        
        import threading
        
        def run_api_thread():
            run_server()
        
        api_thread = threading.Thread(target=run_api_thread, daemon=True)
        api_thread.start()
        
        import time
        time.sleep(2)
        
        from frontend.gui.main import main as gui_main
        gui_main()
    
    elif args.mode == 'web':
        print("Starting web interface...")
        
        import threading
        
        def run_api_thread():
            run_server()
        
        api_thread = threading.Thread(target=run_api_thread, daemon=True)
        api_thread.start()
        
        import time
        time.sleep(2)
        
        print(f"\nWeb interface available at: http://{Config.API_HOST}:{Config.API_PORT}/")
        print("Press Ctrl+C to stop the server\n")
        
        try:
            api_thread.join()
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == '__main__':
    main()
