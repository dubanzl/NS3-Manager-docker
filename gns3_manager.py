#!/usr/bin/env python3
"""
GNS3 Manager - Console application to manage GNS3 server and QEMU versions
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class GNS3Manager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.compose_file = Path("docker-compose.yml")
        self.template_file = Path("docker-compose.template.yml")

    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            print(f"Error: Config file {self.config_path} not found!")
            sys.exit(1)
        
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_defaults(self) -> Dict[str, str]:
        """Get default versions from config"""
        return self.config.get("defaults", {})

    def get_available_versions(self) -> Dict[str, list]:
        """Get available versions from config"""
        return self.config.get("available_versions", {})

    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("GNS3 Manager - Version Selection")
        print("="*50)
        defaults = self.get_defaults()
        print(f"\nCurrent defaults:")
        print(f"  GNS3 Server: {defaults.get('gns3_server_version', 'N/A')}")
        print(f"  QEMU: {defaults.get('qemu_version', 'N/A')}")
        print("\nOptions:")
        print("  1. Select GNS3 Server version")
        print("  2. Select QEMU version")
        print("  3. Use defaults and generate docker-compose.yml")
        print("  4. Build Docker image")
        print("  5. Start services (docker-compose up)")
        print("  6. Stop services (docker-compose down)")
        print("  7. View logs")
        print("  8. Exit")
        print("="*50)

    def select_version(self, component: str) -> Optional[str]:
        """Interactive version selection"""
        available = self.get_available_versions()
        versions = available.get(component, [])
        
        if not versions:
            print(f"No versions available for {component}")
            return None

        print(f"\nAvailable {component} versions:")
        for i, version in enumerate(versions, 1):
            print(f"  {i}. {version}")
        
        while True:
            try:
                choice = input(f"\nSelect {component} version (1-{len(versions)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(versions):
                    selected = versions[idx]
                    print(f"Selected: {selected}")
                    return selected
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(versions)}")
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nCancelled.")
                return None

    def update_default(self, component: str, version: str):
        """Update default version in config"""
        if "defaults" not in self.config:
            self.config["defaults"] = {}
        
        key = f"{component}_version" if component == "gns3_server" else f"{component}_version"
        self.config["defaults"][key] = version
        self.save_config()
        print(f"Updated default {component} version to {version}")

    def generate_compose_file(self):
        """Generate docker-compose.yml from template with current defaults"""
        defaults = self.get_defaults()
        qemu_version = defaults.get("qemu_version", "4.2.1")
        gns3_version = defaults.get("gns3_server_version", "2.2.40")

        if not self.template_file.exists():
            print(f"Error: Template file {self.template_file} not found!")
            return False

        # Read template
        with open(self.template_file, 'r') as f:
            content = f.read()

        # Replace placeholders
        content = content.replace("${QEMU_VERSION}", qemu_version)
        content = content.replace("${GNS3_SERVER_VERSION}", gns3_version)

        # Write docker-compose.yml
        with open(self.compose_file, 'w') as f:
            f.write(content)

        print(f"\nGenerated {self.compose_file} with:")
        print(f"  QEMU version: {qemu_version}")
        print(f"  GNS3 Server version: {gns3_version}")
        return True

    def build_image(self):
        """Build Docker image with selected versions"""
        defaults = self.get_defaults()
        qemu_version = defaults.get("qemu_version", "4.2.1")
        gns3_version = defaults.get("gns3_server_version", "2.2.40")

        image_name = f"gns3-qemu:{qemu_version}-server-{gns3_version}"
        
        print(f"\nBuilding Docker image: {image_name}")
        print(f"  QEMU: {qemu_version}")
        print(f"  GNS3 Server: {gns3_version}")
        
        cmd = [
            "docker", "build",
            "--build-arg", f"QEMU_VERSION={qemu_version}",
            "--build-arg", f"GNS3_SERVER_VERSION={gns3_version}",
            "-t", image_name,
            "."
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"\n✓ Successfully built {image_name}")
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Build failed: {e}")
            return False
        except FileNotFoundError:
            print("\n✗ Error: Docker not found. Please install Docker.")
            return False
        
        return True

    def docker_compose(self, action: str):
        """Run docker-compose commands"""
        if not self.compose_file.exists():
            print(f"Error: {self.compose_file} not found. Generate it first (option 3).")
            return False

        actions = {
            "up": ["docker-compose", "up", "-d"],
            "down": ["docker-compose", "down"],
            "logs": ["docker-compose", "logs", "-f"]
        }

        if action not in actions:
            print(f"Unknown action: {action}")
            return False

        try:
            if action == "logs":
                subprocess.run(actions[action])
            else:
                subprocess.run(actions[action], check=True)
                if action == "up":
                    print("\n✓ Services started successfully")
                elif action == "down":
                    print("\n✓ Services stopped successfully")
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Command failed: {e}")
            return False
        except FileNotFoundError:
            print("\n✗ Error: docker-compose not found. Please install docker-compose.")
            return False
        except KeyboardInterrupt:
            if action == "logs":
                print("\nStopped viewing logs.")
            return True

        return True

    def run(self):
        """Main application loop"""
        while True:
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice: ").strip()
                
                if choice == "1":
                    version = self.select_version("gns3_server")
                    if version:
                        self.update_default("gns3_server", version)
                
                elif choice == "2":
                    version = self.select_version("qemu")
                    if version:
                        self.update_default("qemu", version)
                
                elif choice == "3":
                    self.generate_compose_file()
                
                elif choice == "4":
                    self.build_image()
                
                elif choice == "5":
                    self.docker_compose("up")
                
                elif choice == "6":
                    self.docker_compose("down")
                
                elif choice == "7":
                    self.docker_compose("logs")
                
                elif choice == "8":
                    print("\nGoodbye!")
                    break
                
                else:
                    print("\nInvalid choice. Please try again.")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")


def main():
    manager = GNS3Manager()
    manager.run()


if __name__ == "__main__":
    main()
