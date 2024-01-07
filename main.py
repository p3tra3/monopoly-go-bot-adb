import sys
import time
import glob
import PIL.Image
import pynput
import numpy as np
import cv2
import subprocess
import io
from colorama import Fore

class Monopoly:
    cache: dict[str, PIL.Image.Image] = {}

    def __init__(self, delay: float) -> None:
        self.PrintBanner()
        while True:
            self.LoopImages()
            time.sleep(delay)

    def PrintBanner(self) -> None:
        print("Monopoly Go! Bot")

    def LoopImages(self) -> None:
        image_paths = sorted(glob.glob(pathname="*.png", root_dir="images"))
        images = [self.LoadImage(path) for path in image_paths]
        self.find_and_process(images, image_paths)

    def LoadImage(self, path: str) -> PIL.Image.Image:
        image = self.cache.get(path)
        if image is None:
            image = self.cache[path] = PIL.Image.open(f"images/{path}")
        return image

    def find_and_process(self, images: list[PIL.Image.Image], paths: list[str]) -> None:
        # Capture the screen once for all images
        result = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
        screen_np = np.array(PIL.Image.open(io.BytesIO(result.stdout)))

        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

        for image, path in zip(images, paths):
            print(f"Processing image: {path}")
            match_found = self.find(screen_gray, image)
            if path == "0.png":
                print(f"{Fore.BLUE}ZZZZZZZZZZZ")
                time.sleep(1200)
            
            
    def find(self, screen_gray: np.ndarray, image: PIL.Image.Image) -> bool:
        image_np = np.array(image)
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screen_gray, image_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        threshold = 0.8
        if max_val < threshold:
            print(f"{Fore.RED}No match found.")
            return False

        top_left = max_loc
        print(f"{Fore.GREEN}match found.")
        h, w = image_gray.shape[:2]
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        subprocess.run(["adb", "exec-out", "input", "tap", str(center_x), str(center_y)])
        return True

try:
    Monopoly(delay=0.1)
except KeyboardInterrupt:
    sys.exit()
