# AetherCoins (AetherPack, AetherItemID): money text with coin icons whichever
# money function the client has, and our own when it has none.
import re, sys
import lupa.lua51 as l
fails = []
def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
for path in ('/home/claude/aether-suite/AetherPack/AetherPack.lua', '/home/claude/aether-suite/AetherItemID/AetherItemID.lua'):
    src = open(path).read()
    a = src.index("local function AetherCoins(amount)"); b = src.index("\nend\n", a) + 5
    fn = src[a:b] + "\nreturn AetherCoins"
    name = path.split('/')[-2]
    for setup, label, want in [
        ("C_CurrencyInfo = { GetCoinTextureString = function(m) return 'NEW' .. m end }", "new function only (modern clients)", "NEW123456"),
        ("GetCoinTextureString = function(m) return 'OLD' .. m end", "old function only", "OLD123456"),
        ("", "no money function at all", None)]:
        L = l.LuaRuntime()
        L.execute(setup)
        f = L.execute(fn)
        out = f(123456)
        if want: check(f"{name}: {label}", out == want)
        else:
            check(f"{name}: {label}: built ourselves", out == "12|TInterface\\MoneyFrame\\UI-GoldIcon:0:0:2:0|t 34|TInterface\\MoneyFrame\\UI-SilverIcon:0:0:2:0|t 56|TInterface\\MoneyFrame\\UI-CopperIcon:0:0:2:0|t")
            check(f"{name}: zero shows 0 copper", f(0) == "0|TInterface\\MoneyFrame\\UI-CopperIcon:0:0:2:0|t")
            check(f"{name}: just gold skips silver and copper", f(50000) == "5|TInterface\\MoneyFrame\\UI-GoldIcon:0:0:2:0|t")
    L = l.LuaRuntime(); L.execute("C_CurrencyInfo = { GetCoinTextureString = function() error('boom') end }; GetMoneyString = function(m) return 'MS' .. m end")
    check(f"{name}: a failing function falls through to the next", L.execute(fn)(7) == "MS7")
    check(f"{name}: no bare GetCoinTextureString( calls left", not re.search(r'(?<![._])GetCoinTextureString\(', src.replace(src[a:b], '')))
print("FAILED:", fails) if fails else print("all passed")
sys.exit(1 if fails else 0)
