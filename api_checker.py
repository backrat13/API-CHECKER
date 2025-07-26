#!/usr/bin/env python3
import os
import sys
import socket
import psutil
import requests
from prettytable import PrettyTable
import inquirer
from inquirer.themes import load_theme_from_dict

def get_local_apis():
    """Identify locally running APIs by checking listening ports"""
    apis = []
    for conn in psutil.net_connections():
        if conn.status == 'LISTEN' and conn.laddr:
            port = conn.laddr.port
            try:
                # Skip system ports and common non-API ports
                if port < 1024 or port in [22, 25, 53, 80, 443, 3306, 5432, 6379, 27017]:
                    continue
                    
                # Try to identify the process
                proc = psutil.Process(conn.pid)
                proc_name = proc.name()
                cmd = " ".join(proc.cmdline())
                
                apis.append({
                    'type': 'LOCAL',
                    'port': port,
                    'pid': conn.pid,
                    'name': proc_name,
                    'cmd': cmd,
                    'status': 'Running'
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    return apis

def get_browser_apis():
    """Identify APIs being used in browser tabs"""
    # Note: This is a simplified version and might not catch all browser APIs
    browser_apis = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(browser in proc.info['name'].lower() for browser in ['chrome', 'firefox', 'edge', 'safari']):
                # This is a simplified check - in a real app, you'd want to use browser extensions
                # or other methods to detect actual API usage
                for conn in proc.connections():
                    if conn.raddr and conn.raddr.port in [80, 443, 3000, 5000, 8000, 8080, 8443]:
                        browser_apis.append({
                            'type': 'BROWSER',
                            'url': f"http{'s' if conn.raddr.port == 443 else ''}://{conn.raddr.ip}:{conn.raddr.port}",
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'status': 'Active in browser'
                        })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return browser_apis

def display_apis(apis):
    """Display the list of APIs in a table"""
    if not apis:
        print("\nNo APIs found!")
        return
    
    table = PrettyTable()
    table.field_names = ["#", "Type", "Port/URL", "PID", "Name", "Status"]
    
    for i, api in enumerate(apis, 1):
        port_or_url = api.get('url', api.get('port', 'N/A'))
        table.add_row([
            i,
            api['type'],
            port_or_url,
            api.get('pid', 'N/A'),
            api.get('name', 'Unknown')[:30],
            api.get('status', 'Unknown')
        ])
    
    print("\nDetected APIs:")
    print(table)

def terminate_api(api):
    """Terminate a running API process"""
    try:
        if api['type'] == 'LOCAL':
            proc = psutil.Process(api['pid'])
            proc.terminate()
            return f"Terminated process {api['pid']} ({api['name']}) on port {api['port']}"
        else:
            return "Cannot terminate browser-based APIs from this tool. Please close the browser tab manually."
    except Exception as e:
        return f"Error terminating process: {str(e)}"

def main():
    """Main function to run the API checker"""
    print("🚀 API Checker Tool - Detecting running APIs...\n")
    
    while True:
        # Get all APIs
        local_apis = get_local_apis()
        browser_apis = get_browser_apis()
        all_apis = local_apis + browser_apis
        
        # Display APIs
        display_apis(all_apis)
        
        # Ask user what to do
        questions = [
            inquirer.List('action',
                message="What would you like to do?",
                choices=['Refresh', 'Terminate an API', 'Exit']
            )
        ]
        
        try:
            answers = inquirer.prompt(questions, theme=load_theme_from_dict({
                'List': {
                    'selection_color': 'blue',
                    'selection_cursor': '➤',
                }
            }))
            
            if not answers:
                break
                
            if answers['action'] == 'Exit':
                print("\n👋 Exiting API Checker. Goodbye!")
                break
                
            elif answers['action'] == 'Terminate an API' and all_apis:
                api_choices = [
                    f"{i+1}. {api['type']} - {api.get('url', f"Port {api.get('port', 'N/A')}")} (PID: {api.get('pid', 'N/A')})" 
                    for i, api in enumerate(all_apis)
                ]
                api_choices.append("Cancel")
                
                terminate_questions = [
                    inquirer.List('api_choice',
                        message="Select an API to terminate:",
                        choices=api_choices
                    )
                ]
                
                terminate_answers = inquirer.prompt(terminate_questions, theme=load_theme_from_dict({
                    'List': {
                        'selection_color': 'red',
                        'selection_cursor': '❌',
                    }
                }))
                
                if terminate_answers and 'Cancel' not in terminate_answers['api_choice']:
                    selected_index = int(terminate_answers['api_choice'].split('.')[0]) - 1
                    if 0 <= selected_index < len(all_apis):
                        result = terminate_api(all_apis[selected_index])
                        print(f"\n{result}")
                        input("\nPress Enter to continue...")
            
            # Clear screen for next iteration
            os.system('cls' if os.name == 'nt' else 'clear')
            
        except KeyboardInterrupt:
            print("\n👋 Exiting API Checker. Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️  An error occurred: {str(e)}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Check if running as root (required for some operations on Linux)
    if os.name == 'posix' and os.geteuid() != 0:
        print("⚠️  Warning: Some features may require root privileges. Consider running with sudo.")
    
    # Check for required packages
    try:
        import psutil
        import inquirer
        from prettytable import PrettyTable
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "inquirer", "prettytable"])
        print("\n✅ Required packages installed. Please run the script again.")
        sys.exit(0)
    
    main()
