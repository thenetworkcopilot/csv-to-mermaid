import csv
import re
import sys
import argparse

def sanitize_for_mermaid_id(device_name):
    """Sanitizes a device name to be a valid Mermaid node ID."""
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", device_name.lower())
    return sanitized

def generate_mermaid_from_csv(csv_filepath, output_file=None):
    """
    Generates a Mermaid graph script from a CSV file of network connections,
    intelligently assigning the most specific platform information available.
    
    Args:
        csv_filepath: Path to the input CSV file
        output_file: Optional path to save the Mermaid script (default: network_diagram.md)
    
    Returns:
        String containing the Mermaid diagram script, or None if an error occurred
    """
    nodes = {}
    edges = []
    
    # Set to track links we have already processed (prevents duplicates)
    processed_links = set()

    try:
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Use a case-insensitive method to find column names
            def find_col(name):
                return next((col for col in reader.fieldnames if col.lower() == name.lower()), None)

            # Map the required columns, aborting if any are missing
            col_map = {
                'queried': find_col('Queried_Device_Name'),
                'neighbor_id': find_col('Neighbor_Device_ID'),
                'neighbor_platform': find_col('Neighbor_Platform'),
                'local_if': find_col('local_interface'),
                'remote_if': find_col('Remote_Interface')
            }
            
            if not all([col_map['queried'], col_map['neighbor_id'], col_map['local_if'], col_map['remote_if']]):
                print("Error: Required columns not found in CSV file.", file=sys.stderr)
                print("Required columns: Queried_Device_Name, Neighbor_Device_ID, Local_Interface, Remote_Interface", file=sys.stderr)
                print(f"Found columns: {reader.fieldnames}", file=sys.stderr)
                return None

            # Helper function to intelligently add or update nodes
            def add_or_update_node(name, platform=""):
                # Normalize the device name to lowercase for consistent tracking
                node_key = name.lower()
                
                # If the node is new, add it
                if node_key not in nodes:
                    nodes[node_key] = {"display_name": name, "platform": platform or "Unknown"}
                # If the node exists but has a generic platform, update it with a specific one
                elif nodes[node_key]["platform"] == "Unknown" and platform:
                    nodes[node_key]["platform"] = platform

            for row in reader:
                queried_device_name = row[col_map['queried']].strip()
                neighbor_device_name = row[col_map['neighbor_id']].strip()
                platform = row.get(col_map['neighbor_platform'], "").strip()

                # Skip rows with empty device names
                if not queried_device_name or not neighbor_device_name:
                    continue

                # Add or update both devices found in the row
                add_or_update_node(queried_device_name)
                add_or_update_node(neighbor_device_name, platform)

                # Deduplication: Create a sorted tuple to identify unique connections
                link_signature = tuple(sorted([queried_device_name.lower(), neighbor_device_name.lower()]))

                # Skip if we've already processed this connection
                if link_signature in processed_links:
                    continue
                
                # Mark this pair as processed
                processed_links.add(link_signature)

                edges.append({
                    "from": queried_device_name.lower(),
                    "to": neighbor_device_name.lower(),
                    "label": f"{row[col_map['local_if']].strip()} -- {row[col_map['remote_if']].strip()}"
                })

    except FileNotFoundError:
        print(f"Error: File not found at {csv_filepath}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return None

    # Generate Mermaid script
    mermaid_script = "graph TD;\n\n"
    mermaid_script += "    %% Node Definitions\n"
    for node_key, data in nodes.items():
        node_id = sanitize_for_mermaid_id(node_key)
        display_name = data['display_name']
        platform_text = data.get('platform', 'Unknown')
        
        # Only show platform if it's specific
        display_platform = f"<br/><i>{platform_text}</i>" if platform_text and platform_text != "Unknown" else ""
        mermaid_script += f'    {node_id}["{display_name}{display_platform}"];\n'

    mermaid_script += "\n    %% Edge Definitions (Connections)\n"
    for edge in edges:
        from_id = sanitize_for_mermaid_id(edge['from'])
        to_id = sanitize_for_mermaid_id(edge['to'])
        label = edge['label'].replace('"', '#quot;')
        mermaid_script += f'    {from_id} ---|"{label}"| {to_id};\n'

    # Save to file if output path specified
    if output_file:
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                f.write(mermaid_script)
            print(f"✅ Mermaid script saved to {output_file}")
        except Exception as e:
            print(f"Error writing to file: {e}", file=sys.stderr)

    return mermaid_script

def main():
    parser = argparse.ArgumentParser(
        description='Generate Mermaid network diagrams from CSV files containing network device connections.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  python csv_to_mermaid.py network_data.csv
  python csv_to_mermaid.py network_data.csv -o diagram.md
  python csv_to_mermaid.py network_data.csv --no-save

View the generated diagram at: https://mermaid.live
        '''
    )
    
    parser.add_argument('csv_file', help='Path to the input CSV file')
    parser.add_argument('-o', '--output', default='network_diagram.md', 
                        help='Output file path (default: network_diagram.md)')
    parser.add_argument('--no-save', action='store_true', 
                        help='Only print to console, do not save to file')
    
    args = parser.parse_args()
    
    output_file = None if args.no_save else args.output
    mermaid_output = generate_mermaid_from_csv(args.csv_file, output_file)
    
    if mermaid_output:
        print("\n✅ Successfully generated Mermaid diagram script:\n")
        print("```mermaid")
        print(mermaid_output)
        print("```")
        print("\n💡 Paste the content into a Mermaid live editor: https://mermaid.live")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
