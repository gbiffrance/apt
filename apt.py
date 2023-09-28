import apt.defaultserver as apt_default_server
import apt.services.config as CONFIG
import sys

if __name__ == '__main__':
    
    if CONFIG.has_required_parameters():
        CONFIG.display_banner()
        print("Create default server", flush=True)
        apt_default_server.create_server(__name__, "8080")
    else:
        sys.exit(1)