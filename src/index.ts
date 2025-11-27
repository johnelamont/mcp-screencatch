#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { captureScreenRegion, listCaptures, setOutputDirectory } from "./capture.js";

// Default output directory
let outputDirectory = process.env.SCREENCATCH_OUTPUT_DIR || process.cwd();

// Define available tools
const tools: Tool[] = [
  {
    name: "capture_screen",
    description: "Initiates an interactive screen capture interface. Allows user to select a region of their screen, capture it, and save with timestamp. Returns the path to the saved file.",
    inputSchema: {
      type: "object",
      properties: {
        prompt_continue: {
          type: "boolean",
          description: "Whether to prompt for another capture after this one",
          default: true,
        },
      },
    },
  },
  {
    name: "set_output_directory",
    description: "Set the directory where screen captures will be saved",
    inputSchema: {
      type: "object",
      properties: {
        directory: {
          type: "string",
          description: "Absolute path to the output directory",
        },
      },
      required: ["directory"],
    },
  },
  {
    name: "list_captures",
    description: "List all screen captures in the output directory, sorted by timestamp",
    inputSchema: {
      type: "object",
      properties: {
        limit: {
          type: "number",
          description: "Maximum number of captures to return (default: 10)",
          default: 10,
        },
      },
    },
  },
];

// Create server instance
const server = new Server(
  {
    name: "mcp-screencatch",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools,
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "capture_screen": {
        const promptContinue = typeof args?.prompt_continue === 'boolean' ? args.prompt_continue : true;
        const result = await captureScreenRegion(outputDirectory, promptContinue);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "set_output_directory": {
        const directory = args?.directory as string;
        if (!directory) {
          throw new Error("directory parameter is required");
        }
        outputDirectory = directory;
        setOutputDirectory(directory);
        return {
          content: [
            {
              type: "text",
              text: `Output directory set to: ${directory}`,
            },
          ],
        };
      }

      case "list_captures": {
        const limit = (args?.limit as number) ?? 10;
        const captures = await listCaptures(outputDirectory, limit);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(captures, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: `Error: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP ScreenCatch server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
