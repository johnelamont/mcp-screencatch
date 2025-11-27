import screenshot from "screenshot-desktop";
import { writeFile, readdir, stat, mkdir } from "fs/promises";
import { join, resolve } from "path";
import { existsSync } from "fs";
import { selectRegionInteractive, captureRegion } from "./overlay.js";

let currentOutputDirectory = process.cwd();

export function setOutputDirectory(directory: string): void {
  currentOutputDirectory = directory;
}

/**
 * Generate a timestamped filename for captures
 */
function generateTimestampedFilename(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");

  return `capture_${year}-${month}-${day}_${hours}${minutes}${seconds}.png`;
}

/**
 * Ensure the output directory exists
 */
async function ensureOutputDirectory(directory: string): Promise<void> {
  if (!existsSync(directory)) {
    await mkdir(directory, { recursive: true });
  }
}

/**
 * Capture a region of the screen with interactive selection
 *
 * Opens a transparent overlay window that allows the user to select a region
 * by clicking and dragging. The selected region is then captured and saved.
 */
export async function captureScreenRegion(
  outputDir: string,
  promptContinue: boolean = true
): Promise<{
  success: boolean;
  filepath?: string;
  timestamp?: string;
  message?: string;
  continue_prompt?: boolean;
}> {
  try {
    await ensureOutputDirectory(outputDir);

    console.error("Opening region selection overlay...");

    // Show interactive overlay for region selection
    const region = await selectRegionInteractive();

    if (!region) {
      console.error("Screen capture cancelled by user");
      return {
        success: false,
        message: "Screen capture cancelled by user",
      };
    }

    // Generate filename with timestamp
    const filename = generateTimestampedFilename();
    const filepath = resolve(join(outputDir, filename));

    console.error(`Capturing region: ${region.width}x${region.height} at (${region.x}, ${region.y})`);

    // Capture the selected region
    await captureRegion(region, filepath);

    const timestamp = new Date().toISOString();

    console.error(`Screen captured: ${filepath}`);

    return {
      success: true,
      filepath,
      timestamp,
      message: `Screen captured successfully. Region: ${region.width}x${region.height}. File saved to: ${filepath}`,
      continue_prompt: promptContinue,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error("Capture error:", errorMessage);

    return {
      success: false,
      message: `Failed to capture screen: ${errorMessage}`,
    };
  }
}

/**
 * List all captures in the output directory, sorted by timestamp (newest first)
 */
export async function listCaptures(
  outputDir: string,
  limit: number = 10
): Promise<{
  captures: Array<{
    filename: string;
    filepath: string;
    timestamp: Date;
    size: number;
  }>;
  total: number;
}> {
  try {
    await ensureOutputDirectory(outputDir);

    const files = await readdir(outputDir);

    // Filter for capture files (matching our naming pattern)
    const captureFiles = files.filter((f) =>
      f.startsWith("capture_") && f.endsWith(".png")
    );

    // Get file stats for each capture
    const capturesWithStats = await Promise.all(
      captureFiles.map(async (filename) => {
        const filepath = join(outputDir, filename);
        const stats = await stat(filepath);

        return {
          filename,
          filepath: resolve(filepath),
          timestamp: stats.mtime,
          size: stats.size,
        };
      })
    );

    // Sort by timestamp (newest first)
    capturesWithStats.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

    // Apply limit
    const limitedCaptures = capturesWithStats.slice(0, limit);

    return {
      captures: limitedCaptures,
      total: capturesWithStats.length,
    };
  } catch (error) {
    console.error("Error listing captures:", error);
    return {
      captures: [],
      total: 0,
    };
  }
}

/**
 * Export the interactive region selection function
 * Implementation is in overlay.ts using Electron
 */
export { selectRegionInteractive as selectRegion };
