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

interface CaptureResult {
  captures: Region[];
  count: number;
  cancelled: boolean;
  description?: string;
  reason?: string;
}

/**
 * Generate a unique temporary file path for IPC
 */
function getTempOutputFile(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  return join(__dirname, `capture-result-${timestamp}-${random}.json`);
}

/**
 * Enhanced capture with description and multi-capture support
 */
export async function enhancedCaptureScreen(
  withDescription: boolean = true
): Promise<CaptureResult | null> {
  const outputFile = getTempOutputFile();
  const scriptPath = join(__dirname, "..", "enhanced-capture.py");

  const args = [scriptPath, outputFile];
  if (withDescription) {
    args.push("--with-description");
  }

  return new Promise((resolve, reject) => {
    const child = spawn("python", args, {
      stdio: "inherit",
      detached: false,
    });

    child.on("error", (error) => {
      console.error("Failed to launch enhanced capture:", error);
      reject(error);
    });

    child.on("exit", async (code) => {
      try {
        if (existsSync(outputFile)) {
          const data = await readFile(outputFile, "utf-8");
          const result = JSON.parse(data) as CaptureResult;

          // Clean up temp file
          try {
            await unlink(outputFile);
          } catch (e) {
            // Ignore cleanup errors
          }

          if (result.cancelled) {
            resolve(null);
          } else {
            resolve(result);
          }
        } else {
          resolve(null);
        }
      } catch (error) {
        console.error("Failed to read capture result:", error);
        reject(error);
      }
    });
  });
}

/**
 * Capture individual regions and return image buffers
 */
export async function captureRegions(
  regions: Region[]
): Promise<Buffer[]> {
  const fullScreenshot = await screenshot({ format: "png" });

  const images: Buffer[] = [];
  for (const region of regions) {
    const imageBuffer = await sharp(fullScreenshot)
      .extract({
        left: region.x,
        top: region.y,
        width: region.width,
        height: region.height,
      })
      .png()
      .toBuffer();

    images.push(imageBuffer);
  }

  return images;
}

/**
 * Merge multiple images using Python's image-merger
 */
export async function mergeImages(
  imageBuffers: Buffer[],
  method: "vertical" | "horizontal" | "grid" | "auto" = "auto",
  outputPath: string
): Promise<void> {
  // Save temporary image files
  const tempDir = __dirname;
  const tempFiles: string[] = [];

  for (let i = 0; i < imageBuffers.length; i++) {
    const tempFile = join(tempDir, `temp-merge-${Date.now()}-${i}.png`);
    await writeFile(tempFile, imageBuffers[i]);
    tempFiles.push(tempFile);
  }

  try {
    // Call Python merger script
    const mergerScript = join(__dirname, "..", "merge-images-cli.py");

    await new Promise<void>((resolve, reject) => {
      const args = [mergerScript, "--output", outputPath, "--method", method, ...tempFiles];
      const child = spawn("python", args, { stdio: "inherit" });

      child.on("error", reject);
      child.on("exit", (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Image merge failed with code ${code}`));
        }
      });
    });
  } finally {
    // Clean up temp files
    for (const tempFile of tempFiles) {
      try {
        await unlink(tempFile);
      } catch (e) {
        // Ignore cleanup errors
      }
    }
  }
}

/**
 * Show preview and ask if user wants to recapture
 */
async function showPreviewAndConfirm(
  imagePath: string,
  description: string,
  captureCount: number
): Promise<boolean> {
  const previewScript = join(__dirname, "..", "preview-and-confirm.py");

  return new Promise((resolve, reject) => {
    const child = spawn("python", [
      previewScript,
      imagePath,
      description || "Untitled",
      String(captureCount)
    ], {
      stdio: ["inherit", "pipe", "inherit"],
    });

    let output = "";
    child.stdout?.on("data", (data) => {
      output += data.toString();
    });

    child.on("error", (error) => {
      console.error("Failed to show preview:", error);
      resolve(false); // Default to not recapturing on error
    });

    child.on("exit", (code) => {
      try {
        if (code === 1) {
          // Exit code 1 means recapture
          resolve(true);
        } else {
          // Exit code 0 or anything else means keep
          resolve(false);
        }
      } catch (error) {
        console.error("Preview error:", error);
        resolve(false);
      }
    });
  });
}

/**
 * Complete enhanced capture workflow
 */
export async function enhancedCaptureWorkflow(
  outputDir: string,
  withDescription: boolean = true,
  showPreview: boolean = false
): Promise<{
  success: boolean;
  filepath?: string;
  description?: string;
  captureCount?: number;
  message?: string;
  recaptured?: number;
}> {
  let recaptureCount = 0;
  let savedDescription: string | undefined;

  try {
    while (true) {
      // Step 1: Get description and capture regions
      const result = await enhancedCaptureScreen(withDescription && !savedDescription);

      if (!result || result.cancelled) {
        return {
          success: false,
          message: "Capture cancelled by user",
        };
      }

      if (result.count === 0) {
        return {
          success: false,
          message: "No regions captured",
        };
      }

      // Save description for recaptures
      if (result.description && !savedDescription) {
        savedDescription = result.description;
      }

      console.error(`Captured ${result.count} region(s)`);
      if (savedDescription) {
        console.error(`Description: ${savedDescription}`);
      }

      // Step 2: Capture the actual screenshots
      const imageBuffers = await captureRegions(result.captures);

      // Step 3: Generate filename
      const timestamp = new Date();
      const year = timestamp.getFullYear();
      const month = String(timestamp.getMonth() + 1).padStart(2, "0");
      const day = String(timestamp.getDate()).padStart(2, "0");
      const hours = String(timestamp.getHours()).padStart(2, "0");
      const minutes = String(timestamp.getMinutes()).padStart(2, "0");
      const seconds = String(timestamp.getSeconds()).padStart(2, "0");
      const filename = `capture_${year}-${month}-${day}_${hours}${minutes}${seconds}.png`;
      const filepath = join(outputDir, filename);

      // Step 4: Save image(s)
      if (imageBuffers.length === 1) {
        // Single capture - just save it
        await writeFile(filepath, imageBuffers[0]);
      } else {
        // Multiple captures - merge them
        await mergeImages(imageBuffers, "auto", filepath);
      }

      // Step 5: Save metadata
      const metadataPath = filepath.replace(".png", ".json");
      const metadata = {
        description: savedDescription || "",
        timestamp: timestamp.toISOString(),
        captures: result.count,
        merged: result.count > 1,
        filepath: filepath,
        regions: result.captures,
        recapture_iteration: recaptureCount,
      };
      await writeFile(metadataPath, JSON.stringify(metadata, null, 2));

      console.error(`Saved to: ${filepath}`);
      if (result.count > 1) {
        console.error(`Merged ${result.count} captures into one image`);
      }

      // Step 6: Show preview and ask if user wants to recapture (if enabled)
      let shouldRecapture = false;

      if (showPreview) {
        shouldRecapture = await showPreviewAndConfirm(
          filepath,
          savedDescription || "",
          result.count
        );
      }

      if (!shouldRecapture) {
        // User is happy with the capture
        return {
          success: true,
          filepath,
          description: savedDescription,
          captureCount: result.count,
          recaptured: recaptureCount,
          message: `Successfully captured ${result.count} region(s)${savedDescription ? `: ${savedDescription}` : ""}${recaptureCount > 0 ? ` (recaptured ${recaptureCount} time${recaptureCount > 1 ? 's' : ''})` : ""}`,
        };
      }

      // User wants to recapture - delete the file and loop
      recaptureCount++;
      console.error(`User requested recapture (attempt #${recaptureCount + 1})...`);

      try {
        await unlink(filepath);
        await unlink(metadataPath);
      } catch (e) {
        // Ignore file deletion errors
      }

      // Continue the loop with same description
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error("Enhanced capture error:", errorMessage);

    return {
      success: false,
      message: `Failed: ${errorMessage}`,
    };
  }
}
