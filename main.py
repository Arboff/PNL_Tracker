import os
import time
import pygame
import pygame.freetype
import threading
import requests
import json
import ctypes
import pyperclip

class SolanaTracker:
    def __init__(self, config_file="config.json", font_path="font.otf"):
        print("Initializing Solana Tracker...")
        pygame.freetype.init()
        self.load_config(config_file)
        self.initial_balance = self.read_initial_balance()
        self.current_balance = self.initial_balance if self.initial_balance is not None else 0.0
        self.running = True
        self.font = pygame.freetype.Font(font_path, 24)
        self.large_font = pygame.freetype.Font(font_path, int(24 * 1.5))
        self.screen_width = 900
        self.screen_height = 200
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Solana Tracker")
        self.clock = pygame.time.Clock()


        self.background_image = self.load_local_image(self.background_image_file)
        print(f"Background image loaded and scaled to: {self.background_image.get_size()}")


        self.balance_thread = threading.Thread(target=self.update_balance, daemon=True)
        self.balance_thread.start()

    def load_config(self, config_file):

        print("Loading configuration from config.json...")
        with open(config_file, 'r') as file:
            config = json.load(file)
            self.wallet_address = config.get("wallet_address", "")
            self.background_image_file = config.get("background_image_file", "bg.png")
        print("Configuration loaded successfully.")

    def load_local_image(self, file_path):

        print(f"Attempting to load image from {file_path}...")
        try:
            image = pygame.image.load(file_path).convert_alpha()  # Use convert_alpha() for transparency
            image = pygame.transform.scale(image, (self.screen_width, self.screen_height))  # Scale the image to match the screen size
            print(f"Image loaded successfully from {file_path}")
            return image
        except pygame.error as e:
            print(f"Error loading image: {e}")
            return pygame.Surface((self.screen_width, self.screen_height))  # Return a blank surface in case of error

    def get_solana_balance(self):

        print("Fetching Solana balance...")
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [self.wallet_address]
        }
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if "result" in data and "value" in data["result"]:
            balance_lamports = data["result"]["value"]
            return round(balance_lamports / 1_000_000_000, 3)
        return 0.0

    def save_initial_balance(self):

        with open("sol.arboff", "w") as file:
            file.write(str(self.initial_balance))

    def read_initial_balance(self):

        print("Checking for initial balance...")
        if os.path.exists("sol.arboff"):
            with open("sol.arboff", "r") as file:
                content = file.read().strip()
                if content:
                    return float(content)

        balance = self.get_solana_balance()
        with open("sol.arboff", "w") as file:
            file.write(str(balance))
        print(f"Initial balance saved: {balance} SOL")
        return balance

    def update_balance(self):
        while self.running:
            self.current_balance = self.get_solana_balance()
            if self.initial_balance is None:
                self.initial_balance = self.current_balance
                self.save_initial_balance()
            print(f"Current balance: {self.current_balance} SOL")
            time.sleep(10)

    def draw_ui(self):

        self.screen.blit(self.background_image, (0, 0))


        start_text = "START"
        current_text = f"{self.current_balance} SOL"
        pnl_value = round(self.current_balance - self.initial_balance, 3)
        pnl_text = f"{pnl_value} SOL" if pnl_value >= 0 else f"-{abs(pnl_value)} SOL"
        pnl_color = (0, 255, 0) if pnl_value >= 0 else (255, 0, 0)


        self.draw_rectangle(0, 0, 300, 200, (50, 50, 50, 100))
        self.draw_rectangle(300, 0, 300, 200, (50, 50, 50, 100))
        self.draw_rectangle(600, 0, 300, 200, (50, 50, 50, 100))


        self.render_centered_text_with_large_font(start_text, 0, 300, 50, (255, 255, 255), self.large_font)
        self.render_centered_text_with_large_font(f"{self.initial_balance} SOL", 0, 300, 120, (255, 255, 255), self.large_font)

        self.render_centered_text_with_large_font("CURRENT", 300, 300, 50, (255, 255, 255), self.large_font)
        self.render_centered_text_with_large_font(current_text, 300, 300, 120, (255, 255, 255), self.large_font)

        self.render_centered_text_with_large_font("PNL", 600, 300, 50, (255, 255, 255), self.large_font)
        self.render_centered_text_with_large_font(pnl_text, 600, 300, 120, pnl_color, self.large_font)


        pygame.display.flip()

    def draw_rectangle(self, x, y, width, height, color):

        transparent_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        transparent_surface.fill(color)

        self.screen.blit(transparent_surface, (x, y))

    def render_centered_text_with_large_font(self, text, x, width, y_offset, color, font):

        text_width, text_height = font.get_rect(text).size
        center_x = x + (width - text_width) // 2
        center_y = y_offset


        shadow_x = center_x + 2
        shadow_y = center_y + 2
        font.render_to(self.screen, (shadow_x, shadow_y), text, (0, 0, 0))


        font.render_to(self.screen, (center_x, center_y), text, color)

    def run(self):
        print("Starting Solana Tracker...")
        ctypes.windll.user32.MessageBoxW(0, "Hey there!\nThank you for using my PNL Tracker!\n\nIf you enjoy it, a small support will lead a long way!\nSOL: G4t6feP6sDiwvzB6v9n9719H7u8X5EetUpeSWCmmMsQW.\n\nIts automatically copied to your clipboard.\nMay the trench gods be with you today!", "Alert", 0)
        pyperclip.copy("G4t6feP6sDiwvzB6v9n9719H7u8X5EetUpeSWCmmMsQW")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.draw_ui()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    tracker = SolanaTracker()
    tracker.run()
