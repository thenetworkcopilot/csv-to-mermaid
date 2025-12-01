CSV to Mermaid Network Diagram Generator
A Python tool that converts network device connection data from CSV files into Mermaid diagram syntax, making it easy to visualize network topologies.
Features

🔄 Converts CSV network connection data to Mermaid diagram format
🎯 Automatically deduplicates bidirectional connections
🏷️ Intelligently assigns platform information to devices
📊 Includes interface labels on connections
🔧 Case-insensitive column matching
💾 Outputs to file or console

Requirements

Python 3.6 or higher
No external dependencies (uses only Python standard library)

Installation

Clone this repository:

bashgit clone https://github.com/yourusername/csv-to-mermaid.git
cd csv-to-mermaid

The script is ready to use - no installation required!

CSV Format

Example CSV
Queried_Device_Name,local_interface,Neighbor_Device_ID,Neighbor_Platform,Remote_Interface
isr1100,Gi0/1/1,eero,,0 (d88ed45b86e0)
sw-siteb,Gi1/0/48,isr1100,cisco C1111-4PWB,Gi0/1/0
sw-sitea,Gi1/0/48,isr1100,cisco C1111-4PWB,Gi0/1/3
isr1100,Gi0/1/0,sw-siteb,cisco WS-C2960X-48FPS-L,Gi1/0/48
isr1100,Gi0/1/3,sw-sitea,cisco WS-C2960X-48FPS-L,Gi1/0/48
isr1100,Wl0/1/4,ap3c57,cisco ISR-AP1100AC-B,Gi0

This will:

Read the CSV file
Generate a Mermaid diagram
Save it to network_diagram.md
Print the diagram to console

Viewing the Diagram
After generating the Mermaid script, you can visualize it using:

Mermaid Live Editor: https://mermaid.live

Copy and paste the generated script
Instant visualization in your browser


Example Output
Input CSV data will be converted to Mermaid syntax like this:
mermaidgraph TD;

graph TD;

    %% Node Definitions
    isr1100["isr1100<br/><i>cisco C1111-4PWB</i>"];
    eero["eero"];
    sw_siteb["sw-siteb<br/><i>cisco WS-C2960X-48FPS-L</i>"];
    sw_sitea["sw-sitea<br/><i>cisco WS-C2960X-48FPS-L</i>"];
    ap3c57["ap3c57<br/><i>cisco ISR-AP1100AC-B</i>"];

    %% Edge Definitions (Connections)
    isr1100 ---|"Gi0/1/1 -- 0 (d88ed45b86e0)"| eero;
    sw_siteb ---|"Gi1/0/48 -- Gi0/1/0"| isr1100;
    sw_sitea ---|"Gi1/0/48 -- Gi0/1/3"| isr1100;
    isr1100 ---|"Wl0/1/4 -- Gi0"| ap3c57;


How It Works

Reads CSV: Parses your network connection data
Deduplicates: Removes duplicate connections (A→B is same as B→A)
Assigns Platforms: Uses the most specific platform information available
Sanitizes Names: Converts device names to valid Mermaid node IDs
Generates Script: Creates Mermaid diagram syntax
Outputs: Saves to file and/or prints to console
