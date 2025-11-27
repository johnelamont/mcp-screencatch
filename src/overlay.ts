import { spawn } from "child_process";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { readFile, unlink, writeFile } from "fs/promises";
import { existsSync } from "fs";
import screenshot from "screenshot-desktop";
import sharp from "sharp";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface Region {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Generate a unique temporary file path for IPC
 */
function getTempOutputFile(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  return join(__dirname, `region-output-${timestamp}-${random}.json`);
}

/**
 * Show the overlay and wait for user to select a region
 * Uses Python/tkinter for more reliable GUI on Windows
 */
export async function selectRegionInteractive(): Promise<Region | null> {
  const outputFile = getTempOutputFile();
  const overlayScriptPath = join(__dirname, "..", "overlay.py");

  return new Promise((resolve, reject) => {
    // Spawn the Python overlay script
    const child = spawn("python", [overlayScriptPath, outputFile], {
      stdio: "ignore",
      detached: false,
    });

    child.on("error", (error) => {
      console.error("Failed to launch overlay (is Python installed?):", error);
      reject(error);
    });

    child.on("exit", async (code) => {
      try {
        // Read the result from the output file
        if (existsSync(outputFile)) {
          const data = await readFile(outputFile, "utf-8");
          const result = JSON.parse(data);

          // Clean up the temp file
          try {
            await unlink(outputFile);
          } catch (e) {
            // Ignore cleanup errors
          }

          if (result.cancelled) {
            resolve(null);
          } else {
            resolve(result.region);
          }
        } else {
          // No output file means the app was closed without selection
          resolve(null);
        }
      } catch (error) {
        console.error("Failed to read overlay result:", error);
        reject(error);
      }
    });
  });
}

/**
 * Capture a specific region of the screen
 */
export async function captureRegion(
  region: Region,
  outputPath: string
): Promise<void> {
  // Capture the full screen
  const fullScreenshot = await screenshot({ format: "png" });

  // Crop to the selected region using sharp
  await sharp(fullScreenshot)
    .extract({
      left: region.x,
      top: region.y,
      width: region.width,
      height: region.height,
    })
    .toFile(outputPath);
}

/**
 * Clean up any temporary files (no-op, cleanup handled in selectRegionInteractive)
 */
export function cleanup(): void {
  // No cleanup needed, handled inline
}
