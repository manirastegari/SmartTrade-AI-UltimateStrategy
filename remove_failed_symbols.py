#!/usr/bin/env python3
"""
Remove failed symbols from the TFSA/Questrade universe
Based on logs showing 'ALL FREE SOURCES FAILED' or 'No real data'
"""

# Failed symbols extracted from logs (42 total)
FAILED_SYMBOLS = [
    'WOLF', 'ANSS', 'SPLK', 'JNPR', 'C3AI', 'VERV', 'BLUE', 'SAGE', 'BPMC',
    'HES', 'MRO', 'AXNX', 'NARI', 'ATRI', 'SILK', 'AMED', 'ONEM', 'ESTE',
    'CVW.TO', 'RNW.TO', 'INE.TO', 'NEP', 'PEGI', 'FSR', 'RIDE', 'NKLA',
    'ARVL', 'MULN', 'FFIE', 'PACW', 'Y', 'LANC', 'DSKE', 'PTSI', 'HIBB',
    'EMAN', 'RESN', 'NPTN', 'DSPG', 'EMKR', 'GDNP.TO', 'TOI.TO'
]

def remove_failed_symbols_from_file(filepath):
    """Remove failed symbols from universe file"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    removed_count = 0
    
    for symbol in FAILED_SYMBOLS:
        # Handle different quote styles
        patterns = [
            f"'{symbol}'",
            f'"{symbol}"',
        ]
        
        for pattern in patterns:
            if pattern in content:
                # Replace with empty string, but keep comma/formatting
                content = content.replace(f"{pattern}, ", "")
                content = content.replace(f", {pattern}", "")
                content = content.replace(pattern, "")
                removed_count += 1
                print(f"  ✅ Removed: {symbol}")
                break
    
    # Clean up any double commas or extra spaces
    content = content.replace(",,", ",")
    content = content.replace(", ,", ",")
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(content)
    
    return removed_count

if __name__ == "__main__":
    print("=" * 80)
    print("REMOVING FAILED SYMBOLS FROM TFSA/QUESTRADE UNIVERSE")
    print("=" * 80)
    print(f"\nFound {len(FAILED_SYMBOLS)} failed symbols to remove\n")
    
    filepath = "/Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy/tfsa_questrade_750_universe.py"
    
    removed = remove_failed_symbols_from_file(filepath)
    
    print(f"\n✅ Successfully removed {removed} symbols from universe file")
    print(f"📊 New universe size: 779 - {removed} = {779 - removed} stocks")
    print(f"📁 File updated: {filepath}")
    print("\n" + "=" * 80)
