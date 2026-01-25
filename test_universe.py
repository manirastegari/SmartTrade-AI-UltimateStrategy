
try:
    from premium_quality_universe import get_premium_universe
    print("✅ Successfully imported premium_quality_universe")
    
    full_list = get_premium_universe()
    print(f"✅ Total stocks: {len(full_list)}")
    
    new_stocks = ['MNST', 'KDP', 'INGR', 'BJ', 'CHKP', 'WTRG', 'MSI', 'COLM']
    found = 0
    for stock in new_stocks:
        if stock in full_list:
            print(f"  ✅ Found {stock}")
            found += 1
        else:
            print(f"  ❌ Missing {stock}")
            
    if found == len(new_stocks):
        print("✅ All new stocks verified.")
    else:
        print("❌ Some stocks missing.")
        
except Exception as e:
    print(f"❌ Import failed: {e}")
