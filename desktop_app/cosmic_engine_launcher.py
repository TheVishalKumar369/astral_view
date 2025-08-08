#!/usr/bin/env python3
"""
Cosmic Engine Launcher - Unified Interface for Multiple 3D Engines
Allows seamless switching between Ursina, Panda3D, and future engines
"""

import sys
import subprocess
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import json
import webbrowser

class CosmicEngineLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cosmic Engine Launcher - Choose Your 3D Engine")
        self.root.geometry("800x600")
        self.root.configure(bg='#0a0a0a')
        
        # Project paths
        self.project_root = Path(__file__).parent.parent
        self.engines_config = self.load_engines_config()
        
        self.setup_ui()
        
    def load_engines_config(self):
        """Load engine configurations from organized structure"""
        # Load configurations from JSON files where available
        engines = {}
        
        # Desktop Engines - Ursina
        try:
            ursina_config_path = self.project_root / "desktop_app" / "engines" / "ursina" / "engine_info.json"
            if ursina_config_path.exists():
                with open(ursina_config_path, 'r') as f:
                    ursina_config = json.load(f)
                    
                for variant_id, variant in ursina_config['variants'].items():
                    engines[f'ursina_{variant_id}'] = {
                        'name': variant['name'],
                        'description': variant['description'],
                        'file': f'desktop_app/engines/ursina/{variant["file"]}',
                        'requirements': variant['requirements'],
                        'pros': [f'• {pro}' for pro in variant['pros']],
                        'cons': [f'• {con}' for con in variant['cons']],
                        'status': 'Ready',
                        'category': 'desktop',
                        'engine_type': 'ursina'
                    }
        except Exception as e:
            print(f"Error loading Ursina config: {e}")
            
        # Desktop Engines - Panda3D
        try:
            panda3d_config_path = self.project_root / "desktop_app" / "engines" / "panda3d" / "engine_info.json"
            if panda3d_config_path.exists():
                with open(panda3d_config_path, 'r') as f:
                    panda3d_config = json.load(f)
                    
                for variant_id, variant in panda3d_config['variants'].items():
                    engines[f'panda3d_{variant_id}'] = {
                        'name': variant['name'],
                        'description': variant['description'],
                        'file': f'desktop_app/engines/panda3d/{variant["file"]}',
                        'requirements': variant['requirements'],
                        'pros': [f'• {pro}' for pro in variant['pros']],
                        'cons': [f'• {con}' for con in variant['cons']],
                        'status': 'Ready',
                        'category': 'desktop',
                        'engine_type': 'panda3d'
                    }
        except Exception as e:
            print(f"Error loading Panda3D config: {e}")
            
        # Web Engines
        try:
            web_config_path = self.project_root / "web_portal" / "engines" / "web_engines.json"
            if web_config_path.exists():
                with open(web_config_path, 'r') as f:
                    web_config = json.load(f)
                    
                for engine_id, engine_info in web_config['web_engines'].items():
                    if engine_info['status'] in ['available', 'ready']:
                        engines[f'web_{engine_id}'] = {
                            'name': engine_info['name'],
                            'description': engine_info['description'],
                            'file': f'web_portal/engines/{engine_info.get("main_file", "index.html")}',
                            'requirements': engine_info.get('technologies', ['Modern web browser']),
                            'pros': [f'• {pro}' for pro in engine_info['pros']],
                            'cons': [f'• {con}' for con in engine_info['cons']],
                            'status': 'Available' if engine_info['status'] == 'available' else 'Ready',
                            'category': 'web',
                            'engine_type': engine_id
                        }
        except Exception as e:
            print(f"Error loading web engines config: {e}")
            
        # Future Engines
        try:
            future_config_path = self.project_root / "desktop_app" / "engines" / "future" / "planned_engines.json"
            if future_config_path.exists():
                with open(future_config_path, 'r') as f:
                    future_config = json.load(f)
                    
                for engine_id, engine_info in future_config['planned_engines'].items():
                    engines[f'future_{engine_id}'] = {
                        'name': f"{engine_info['name']} (Future)",
                        'description': f"{engine_info['description']} - ETA: {engine_info.get('estimated_completion', 'TBD')}",
                        'file': f'desktop_app/engines/future/{engine_id}/',
                        'requirements': [f"{engine_info['name']} {engine_info.get('version', '')})"],
                        'pros': [f'• {pro}' for pro in engine_info['pros']],
                        'cons': [f'• {con}' for con in engine_info['cons']],
                        'status': 'Planned',
                        'category': 'future',
                        'engine_type': engine_id
                    }
        except Exception as e:
            print(f"Error loading future engines config: {e}")
            
        # Fallback configurations if JSON files are missing
        if not engines:
            print("Warning: No engine configs found, using fallback configurations")
            return self._get_fallback_configs()
            
        return engines
        
    def _get_fallback_configs(self):
        """Fallback configurations if JSON files are not available"""
        return {
            'ursina_simple': {
                'name': 'Ursina Engine - Simple Explorer',
                'description': 'Lightweight, easy-to-use 3D engine with simple controls',
                'file': 'desktop_app/engines/ursina/cosmic_explorer_simple.py',
                'requirements': ['ursina', 'numpy'],
                'pros': ['• Fast startup', '• Simple controls', '• Lightweight', '• Good for beginners'],
                'cons': ['• Limited physics', '• Basic graphics', '• Fewer features'],
                'status': 'Ready',
                'category': 'desktop'
            },
            'ursina_enhanced': {
                'name': 'Ursina Engine - Enhanced Explorer',
                'description': 'Enhanced Ursina with improved graphics and controls',
                'file': 'desktop_app/engines/ursina/cosmic_explorer_fixed.py',
                'requirements': ['ursina', 'numpy'],
                'pros': ['• Enhanced graphics', '• Better controls', '• More objects', '• Stable performance'],
                'cons': ['• Still limited physics', '• Basic materials'],
                'status': 'Ready',
                'category': 'desktop'
            },
            'panda3d_advanced': {
                'name': 'Panda3D Engine - Advanced Simulation',
                'description': 'Professional-grade 3D engine with realistic physics and graphics',
                'file': 'desktop_app/engines/panda3d/main.py',
                'requirements': ['panda3d', 'numpy', 'scipy', 'astropy', 'pybullet', 'pillow'],
                'pros': ['• Photorealistic graphics', '• Real physics simulation', '• Advanced lighting', '• Professional features'],
                'cons': ['• Complex setup', '• Higher system requirements', '• Steeper learning curve'],
                'status': 'Ready',
                'category': 'desktop'
            }
        }
    
    def setup_ui(self):
        """Setup the launcher UI"""
        # Title
        title_frame = tk.Frame(self.root, bg='#0a0a0a')
        title_frame.pack(pady=20)
        
        title = tk.Label(
            title_frame,
            text="🚀 COSMIC ENGINE LAUNCHER 🌌",
            font=('Arial', 24, 'bold'),
            fg='#00ffff',
            bg='#0a0a0a'
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Choose your preferred 3D engine for cosmic exploration",
            font=('Arial', 12),
            fg='#ffffff',
            bg='#0a0a0a'
        )
        subtitle.pack(pady=5)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Engine selection frame
        selection_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='raised', bd=2)
        selection_frame.pack(fill='both', expand=True)
        
        # Create engine cards
        self.create_engine_cards(selection_frame)
        
        # Bottom button frame
        button_frame = tk.Frame(self.root, bg='#0a0a0a')
        button_frame.pack(pady=20)
        
        # Launch button
        self.launch_button = tk.Button(
            button_frame,
            text="🚀 LAUNCH SELECTED ENGINE",
            font=('Arial', 14, 'bold'),
            bg='#00aa00',
            fg='white',
            command=self.launch_selected_engine,
            state='disabled',
            width=25
        )
        self.launch_button.pack(side='left', padx=10)
        
        # Install dependencies button
        deps_button = tk.Button(
            button_frame,
            text="📦 Install Dependencies",
            font=('Arial', 12),
            bg='#0066cc',
            fg='white',
            command=self.install_dependencies,
            width=20
        )
        deps_button.pack(side='left', padx=10)
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="❌ Exit",
            font=('Arial', 12),
            bg='#cc0000',
            fg='white',
            command=self.root.quit,
            width=10
        )
        exit_button.pack(side='left', padx=10)
        
        self.selected_engine = None
    
    def create_engine_cards(self, parent):
        """Create cards for each engine option"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg='#1a1a1a', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create engine cards
        for engine_id, config in self.engines_config.items():
            self.create_engine_card(scrollable_frame, engine_id, config)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_engine_card(self, parent, engine_id, config):
        """Create an individual engine card"""
        # Main card frame
        card_frame = tk.Frame(parent, bg='#2a2a2a', relief='ridge', bd=2)
        card_frame.pack(fill='x', padx=10, pady=5)
        
        # Header with engine name and status
        header_frame = tk.Frame(card_frame, bg='#2a2a2a')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Radio button for selection
        radio_var = tk.IntVar()
        radio_button = tk.Radiobutton(
            header_frame,
            text=config['name'],
            font=('Arial', 14, 'bold'),
            fg='#ffffff',
            bg='#2a2a2a',
            selectcolor='#2a2a2a',
            activebackground='#2a2a2a',
            command=lambda: self.select_engine(engine_id),
            value=1,
            variable=radio_var
        )
        radio_button.pack(side='left')
        
        # Status indicator
        status_color = {
            'Ready': '#00aa00',
            'Available': '#ffaa00',
            'Planned': '#cc0000'
        }.get(config['status'], '#666666')
        
        status_label = tk.Label(
            header_frame,
            text=f"[{config['status']}]",
            font=('Arial', 10, 'bold'),
            fg=status_color,
            bg='#2a2a2a'
        )
        status_label.pack(side='right')
        
        # Description
        desc_label = tk.Label(
            card_frame,
            text=config['description'],
            font=('Arial', 11),
            fg='#cccccc',
            bg='#2a2a2a',
            wraplength=700,
            justify='left'
        )
        desc_label.pack(fill='x', padx=10, pady=(0, 5))
        
        # Pros and Cons
        details_frame = tk.Frame(card_frame, bg='#2a2a2a')
        details_frame.pack(fill='x', padx=10, pady=5)
        
        # Pros
        pros_frame = tk.Frame(details_frame, bg='#2a2a2a')
        pros_frame.pack(side='left', fill='both', expand=True)
        
        pros_title = tk.Label(
            pros_frame,
            text="✅ PROS:",
            font=('Arial', 10, 'bold'),
            fg='#00aa00',
            bg='#2a2a2a'
        )
        pros_title.pack(anchor='w')
        
        for pro in config['pros']:
            pro_label = tk.Label(
                pros_frame,
                text=pro,
                font=('Arial', 9),
                fg='#aaffaa',
                bg='#2a2a2a',
                justify='left'
            )
            pro_label.pack(anchor='w')
        
        # Cons
        cons_frame = tk.Frame(details_frame, bg='#2a2a2a')
        cons_frame.pack(side='right', fill='both', expand=True)
        
        cons_title = tk.Label(
            cons_frame,
            text="⚠️ CONS:",
            font=('Arial', 10, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        )
        cons_title.pack(anchor='w')
        
        for con in config['cons']:
            con_label = tk.Label(
                cons_frame,
                text=con,
                font=('Arial', 9),
                fg='#ffccaa',
                bg='#2a2a2a',
                justify='left'
            )
            con_label.pack(anchor='w')
        
        # Store radio button for later access
        setattr(self, f'radio_{engine_id}', radio_var)
    
    def select_engine(self, engine_id):
        """Select an engine"""
        # Clear all other selections
        for other_id in self.engines_config.keys():
            if other_id != engine_id:
                radio_var = getattr(self, f'radio_{other_id}', None)
                if radio_var:
                    radio_var.set(0)
        
        self.selected_engine = engine_id
        
        # Enable launch button if engine is ready
        status = self.engines_config[engine_id]['status']
        if status in ['Ready', 'Available']:
            self.launch_button.config(state='normal')
        else:
            self.launch_button.config(state='disabled')
            messagebox.showinfo("Engine Status", f"This engine is {status.lower()} and cannot be launched yet.")
    
    def launch_selected_engine(self):
        """Launch the selected engine"""
        if not self.selected_engine:
            messagebox.showwarning("No Selection", "Please select an engine to launch.")
            return
        
        config = self.engines_config[self.selected_engine]
        engine_file = self.project_root / config['file']
        
        if not engine_file.exists():
            messagebox.showerror("File Not Found", f"Engine file not found: {engine_file}")
            return
        
        try:
            if self.selected_engine == 'three_js_web':
                # Open web browser for Three.js
                webbrowser.open(f"file://{engine_file.absolute()}")
            else:
                # Launch Python-based engines
                subprocess.Popen([sys.executable, str(engine_file)])
            
            # Close launcher
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch engine:\n{str(e)}")
    
    def install_dependencies(self):
        """Install dependencies for selected engine"""
        if not self.selected_engine:
            messagebox.showwarning("No Selection", "Please select an engine first.")
            return
        
        config = self.engines_config[self.selected_engine]
        requirements = config['requirements']
        
        # Show installation dialog
        install_dialog = tk.Toplevel(self.root)
        install_dialog.title("Install Dependencies")
        install_dialog.geometry("600x400")
        install_dialog.configure(bg='#1a1a1a')
        
        # Instructions
        tk.Label(
            install_dialog,
            text=f"Dependencies for {config['name']}:",
            font=('Arial', 14, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Requirements list
        req_frame = tk.Frame(install_dialog, bg='#2a2a2a', relief='sunken', bd=2)
        req_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        for req in requirements:
            tk.Label(
                req_frame,
                text=f"• {req}",
                font=('Arial', 12),
                fg='#cccccc',
                bg='#2a2a2a',
                anchor='w'
            ).pack(fill='x', padx=10, pady=2)
        
        # Install command
        install_cmd = f"pip install {' '.join(req for req in requirements if not req.startswith('Web'))}"
        
        tk.Label(
            install_dialog,
            text="Run this command in your terminal:",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a'
        ).pack(pady=(10, 5))
        
        cmd_entry = tk.Entry(
            install_dialog,
            font=('Courier', 11),
            bg='#000000',
            fg='#00ff00',
            width=60
        )
        cmd_entry.pack(pady=5)
        cmd_entry.insert(0, install_cmd)
        cmd_entry.config(state='readonly')
        
        # Copy button
        def copy_command():
            install_dialog.clipboard_clear()
            install_dialog.clipboard_append(install_cmd)
            messagebox.showinfo("Copied", "Command copied to clipboard!")
        
        tk.Button(
            install_dialog,
            text="📋 Copy Command",
            bg='#0066cc',
            fg='white',
            command=copy_command
        ).pack(pady=10)
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

if __name__ == "__main__":
    launcher = CosmicEngineLauncher()
    launcher.run()
