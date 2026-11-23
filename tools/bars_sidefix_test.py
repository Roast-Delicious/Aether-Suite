from lupa import LuaRuntime
L=LuaRuntime(unpack_returned_tuples=True)
L.execute(open('/mnt/user-data/uploads/54619117#1--SavedVariables/AetherBars.lua').read())
src=open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a=src.index('        -- 1.13.4: an older Align'); b=src.index('        AetherBarsDB, AetherBarsCharDB = db, db')
L.execute('db=AetherBarsDB\n'+src[a:b])
print("before had MultiBarRight: True")
print("after align keys:", sorted(L.eval('db.align').keys()), "flag:", L.eval('db.sideFix1134'))
L.execute('db.align.MultiBarRight={1,2}\n'+src[a:b]); print("second load keeps a new spot:", L.eval('db.align.MultiBarRight') is not None)
