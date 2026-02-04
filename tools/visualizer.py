import pygame
import json
import sys
import time
from config import WORLD_WIDTH, WORLD_HEIGHT

# Constants
CELL_SIZE = 10 # Slightly larger
WINDOW_WIDTH = WORLD_WIDTH * CELL_SIZE
WINDOW_HEIGHT = WORLD_HEIGHT * CELL_SIZE
UI_PANEL_WIDTH = 300
FULL_WIDTH = WINDOW_WIDTH + UI_PANEL_WIDTH

BG_COLOR = (20, 20, 20)
GRID_COLOR = (40, 40, 40)
UI_BG_COLOR = (30, 30, 40)
TEXT_COLOR = (220, 220, 220)

AGENT_COLOR = (0, 255, 100)
DEATH_COLOR = (255, 50, 50)

class Visualizer:
    def __init__(self, log_file):
        pygame.init()
        self.screen = pygame.display.set_mode((FULL_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ananke: Live Simulation Observer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 14)
        self.large_font = pygame.font.SysFont("Consolas", 18, bold=True)
        
        self.log_file = log_file
        self.file_handle = open(self.log_file, "r")
        
        self.events = []
        self.agents = {} # id -> {x, y, energy, genome, ...}
        # For smooth animation, we track 'target_x', 'target_y' and 'render_x', 'render_y'
        
        self.paused = False
        self.live_mode = True
        self.event_idx = 0
        self.speed = 10 # events per frame in replay mode
        
        self.selected_agent_id = None

    def read_new_logs(self):
        """Reads any new lines from the file."""
        lines = self.file_handle.readlines()
        new_count = 0
        for line in lines:
            if line.strip():
                try:
                    self.events.append(json.loads(line))
                    new_count += 1
                except json.JSONDecodeError:
                    pass
        return new_count

    def process_event(self, event):
        """Updates internal state based on event."""
        etype = event['type']
        details = event['details']
        
        if etype == "agent_spawn":
            aid = details['id']
            self.agents[aid] = {
                'id': aid,
                'x': details['x'],
                'y': details['y'],
                'render_x': details['x'],
                'render_y': details['y'],
                'energy': 100, # Initial guess
                'genome': details.get('genome', {}),
                'last_action': 'born',
                'age': 0
            }
        
        elif etype == "agent_action":
            aid = details['id']
            if aid in self.agents:
                agent = self.agents[aid]
                agent['energy'] = details.get('energy_after', agent['energy'])
                agent['last_action'] = details['action']
                agent['age'] += 1
                
                # Update Position
                if 'x' in details and 'y' in details:
                    agent['x'] = details['x']
                    agent['y'] = details['y']
                    # We don't snap render_x/y instantly here to allow interpolation in draw loop if we wanted
                    # But for simple "event stream" visualization, snapping is safer to avoid desync
                    # Improving animation: simpler approach -> just move towards target in draw loop
        
        elif etype == "agent_death":
            aid = details['id']
            if aid in self.agents:
                del self.agents[aid]
                if self.selected_agent_id == aid:
                    self.selected_agent_id = None

    def draw_ui(self):
        # Draw Panel Background
        pygame.draw.rect(self.screen, UI_BG_COLOR, (WINDOW_WIDTH, 0, UI_PANEL_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, (100, 100, 100), (WINDOW_WIDTH, 0), (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Stats
        y = 10
        status = "LIVE" if self.live_mode else "REPLAY"
        if self.paused: status += " (PAUSED)"
        
        self._draw_text(f"Status: {status}", (WINDOW_WIDTH + 10, y), self.large_font)
        y += 25
        self._draw_text(f"Events: {self.event_idx}/{len(self.events)}", (WINDOW_WIDTH + 10, y))
        y += 20
        self._draw_text(f"Agents: {len(self.agents)}", (WINDOW_WIDTH + 10, y))
        y += 30
        
        # Selected Agent Info
        if self.selected_agent_id and self.selected_agent_id in self.agents:
            agent = self.agents[self.selected_agent_id]
            self._draw_text(f"AGENT INSPECTOR", (WINDOW_WIDTH + 10, y), self.large_font, (0, 200, 255))
            y += 25
            self._draw_text(f"ID: {agent['id'][:8]}...", (WINDOW_WIDTH + 10, y))
            y += 20
            self._draw_text(f"Pos: ({agent['x']}, {agent['y']})", (WINDOW_WIDTH + 10, y))
            y += 20
            
            # Energy Bar
            e_pct = max(0, min(100, agent['energy'])) / 200.0 # Assuming Max 200
            pygame.draw.rect(self.screen, (50, 0, 0), (WINDOW_WIDTH + 10, y, 200, 15))
            pygame.draw.rect(self.screen, (255, 0, 0) if e_pct < 0.2 else (0, 255, 0), (WINDOW_WIDTH + 10, y, 200 * e_pct, 15))
            self._draw_text(f"Energy: {agent['energy']}", (WINDOW_WIDTH + 15, y+1), color=(255,255,255))
            y += 25
            
            self._draw_text(f"Last Action: {agent['last_action']}", (WINDOW_WIDTH + 10, y))
            y += 30
            
            self._draw_text("Genome Traits:", (WINDOW_WIDTH + 10, y), color=(150, 150, 255))
            y += 20
            for k, v in agent['genome'].items():
                val_str = f"{v:.2f}" if isinstance(v, float) else str(v)
                self._draw_text(f"{k}: {val_str}", (WINDOW_WIDTH + 20, y))
                y += 18
        else:
            self._draw_text("Hover over an agent", (WINDOW_WIDTH + 10, y), color=(100, 100, 100))

    def _draw_text(self, text, pos, font=None, color=TEXT_COLOR):
        if font is None: font = self.font
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

    def run(self):
        print("Starting Visualizer. Press SPACE to Pause, L to toggle Live Mode.")
        running = True
        
        while running:
            # 1. Input Handling
            mouse_pos = pygame.mouse.get_pos()
            hover_cell = (mouse_pos[0] // CELL_SIZE, mouse_pos[1] // CELL_SIZE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_l:
                        self.live_mode = not self.live_mode
                        if self.live_mode:
                            # Jump to end
                            self.paused = False
                elif event.type == pygame.MOUSEMOTION:
                    # Simple Hover Check
                    found_hover = False
                    if mouse_pos[0] < WINDOW_WIDTH:
                        for aid, a in self.agents.items():
                            if int(a['render_x']) == hover_cell[0] and int(a['render_y']) == hover_cell[1]:
                                self.selected_agent_id = aid
                                found_hover = True
                                break
                    if not found_hover:
                        self.selected_agent_id = None
            
            # 2. Data Update
            if self.live_mode:
                self.read_new_logs()
                # fast forward to end
                while self.event_idx < len(self.events):
                    self.process_event(self.events[self.event_idx])
                    self.event_idx += 1
            else:
                if not self.paused and self.event_idx < len(self.events):
                    # Replay speed
                    for _ in range(self.speed):
                        if self.event_idx < len(self.events):
                            self.process_event(self.events[self.event_idx])
                            self.event_idx += 1
            
            # 3. Animation Smoothing (Lerp)
            for aid, agent in self.agents.items():
                agent['render_x'] += (agent['x'] - agent['render_x']) * 0.2
                agent['render_y'] += (agent['y'] - agent['render_y']) * 0.2

            # 4. Rendering
            self.screen.fill(BG_COLOR)
            
            # Draw Agents
            for aid, agent in self.agents.items():
                rx = agent['render_x'] * CELL_SIZE
                ry = agent['render_y'] * CELL_SIZE
                
                # Color based on energy? or unique hash?
                # Color by Genome Risk Tolerance? (Red = Aggressive, Blue = Safe)
                risk = agent['genome'].get('risk_tolerance', 0.5)
                # Simple Green to Red gradient if energy low?
                color = AGENT_COLOR
                if agent['energy'] < 50:
                    color = (255, 100, 0)
                
                pygame.draw.rect(self.screen, color, (rx, ry, CELL_SIZE-1, CELL_SIZE-1))
                
                # Selection Highlight
                if self.selected_agent_id == aid:
                    pygame.draw.rect(self.screen, (255, 255, 255), (rx-1, ry-1, CELL_SIZE+1, CELL_SIZE+1), 1)

            # UI Panel
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        self.file_handle.close()

if __name__ == "__main__":
    vis = Visualizer("simulation_telemetry.jsonl")
    vis.run()
