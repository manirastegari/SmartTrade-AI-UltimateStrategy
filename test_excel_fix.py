
import pandas as pd
import openpyxl
import re
import os

from excel_export import _clean_val

# 2. Verification Test
def test_excel_write():
    print("🧪 Generatng Dangerous Data...")
    
    # Dangerous strings
    bad_data = [
        {"Name": "Null Byte", "Value": "Here is a null: \x00 End"},
        {"Name": "Vertical Tab", "Value": "Vertical: \x0B Tab"},
        {"Name": "Formula Injection", "Value": "=SUM(A1:A10)"},
        {"Name": "Super Long", "Value": "A" * 35000},
        {"Name": "Normal Newline", "Value": "Line 1\nLine 2"}, # Should stay
        {"Name": "Emoji", "Value": "Rocket 🚀"}, # Should stay
    ]
    
    clean_data = []
    for item in bad_data:
        clean_data.append({
            "Name": _clean_val(item["Name"]),
            "Value": _clean_val(item["Value"])
        })
        
    df = pd.DataFrame(clean_data)
    fname = "test_sanitized.xlsx"
    
    print("💾 Saving to Excel...")
    try:
        with pd.ExcelWriter(fname, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        print("✅ Save Successful.")
    except Exception as e:
        print(f"❌ Save Failed: {e}")
        return

    print("📖 Reading back...")
    try:
        df2 = pd.read_excel(fname)
        print("✅ Read Successful.")
        print(df2)
    except Exception as e:
        print(f"❌ Read Failed: {e}")

    # Verify content
    v_tab = df2[df2["Name"] == "Vertical Tab"]["Value"].iloc[0]
    if "\x0B" in v_tab:
        print("❌ Vertical Tab NOT removed!")
    else:
        print("✅ Vertical Tab removed.")

    formula = df2[df2["Name"] == "Formula Injection"]["Value"].iloc[0]
    if formula.startswith("="):
        print("❌ Formula NOT escaped!")
    else:
        print("✅ Formula escaped.")
        
    long_str = df2[df2["Name"] == "Super Long"]["Value"].iloc[0]
    if len(long_str) > 31000:
         print("❌ String NOT truncated!")
    else:
         print(f"✅ String truncated to {len(long_str)}")

if __name__ == "__main__":
    test_excel_write()
