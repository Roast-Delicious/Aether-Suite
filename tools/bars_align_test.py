from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a = src.index('function AetherBars_PlanAlign'); b = src.index('local function PlaceMover')
L.execute('ALIGN=20; NEAR=14\n' + 'local OUTER_GAP = 18\nlocal FAR = 3\nALIGN=20\n' + src[a:b])
def run(name, rects, gap=2.5, size=54):
    L.execute('U = {}')
    for n,(l,r,b,t,main) in rects.items():
        L.execute(f'U[#U+1] = {{name="{n}", main={str(main).lower()}, rect={{l={l},r={r},b={b},t={t}}}}}')
    L.execute(f'P = AetherBars_PlanAlign(U, {gap}, {size})')
    print("==", name)
    res={}
    for i in range(1, len(L.eval('U'))+1):
        u=L.eval(f'U[{i}]'); d=L.eval(f'P[U[{i}]]')
        r=u.rect; nl,nb=r.l+d.dx, r.b+d.dy
        res[u.name]=(nl, nl+(r.r-r.l), nb, nb+(r.t-r.b))
    for n,(l,r,b,t) in sorted(res.items(), key=lambda x:(-x[1][2],x[1][0])):
        print(f"  {n:5} x {l:7.1f}-{r:7.1f}  y {b:6.1f}-{t:6.1f}")
    return res
# user's layout (rough)
res = run("user layout", {
 "Main":(18,695,12,68,True), "S":(18,695,76,132,False), "TL":(18,500,138,188,False),
 "TR":(705,1385,76,132,False), "Util":(705,1598,8,62,False)})
# sloppy two stacked bars + pet bar
run("sloppy stack", {"Main":(400,1077,10,66,True), "B2":(392,1069,80,136,False), "Pet":(500,820,150,180,False)})
# bar far to the right stays apart
run("far right bar", {"Main":(400,1077,10,66,True), "R":(1500,1556,200,800,False)})
