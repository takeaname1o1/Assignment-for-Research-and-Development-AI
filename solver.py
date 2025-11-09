import numpy as np, pandas as pd, heapq, sys

# --- Load data ---
try:
    d = pd.read_csv('xy_data.csv')
    x, y = d['x'].values, d['y'].values
except Exception:
    try:
        d = pd.read_csv('xy_data.csv', header=None)
        x, y = d.iloc[:,0].values, d.iloc[:,1].values
    except Exception as e:
        print(f"Error loading 'xy_data.csv': {e}"); sys.exit()
print(f"Loaded {len(x)} points.")

# --- Core functions ---
def get_pts(t, th, m, xo):
    th = np.radians(th); e = np.exp(m * np.abs(t)) * np.sin(0.3 * t)
    return t*np.cos(th) - e*np.sin(th) + xo, 42 + t*np.sin(th) + e*np.cos(th)

t_dense = np.linspace(6, 66, 1500)
def loss(th, m, xo):
    xc, yc = get_pts(t_dense, th, m, xo)
    d = np.abs(x[:, None]-xc) + np.abs(y[:, None]-yc)
    return np.mean(np.min(d, axis=1))

# --- Hill Climbing ---
class HillClimb:
    def __init__(s, start, steps, bounds, loss, K=5):
        s.start, s.steps, s.bounds, s.loss, s.K = start, steps, bounds, loss, K
        s.visited, s.heap, s.topk = set(), [], []; s.best = (float('inf'), None)
        s.keys = ['th', 'm', 'xo']
    def _nbrs(s, p):
        for i, k in enumerate(s.keys):
            for sgn in [-1,1]:
                v = round(p[i]+sgn*s.steps[k],5) if k=='m' else p[i]+sgn*s.steps[k]
                if s.bounds[k][0]<=v<=s.bounds[k][1]:
                    q = list(p); q[i]=v; yield tuple(q)
    def _topk(s, l, p):
        heapq.heappush(s.topk, (-l,p)); 
        if len(s.topk)>s.K: heapq.heappop(s.topk)
    def search(s, max_iter=5e4, patience=10):
        l0 = s.loss(*s.start); heapq.heappush(s.heap,(l0,s.start))
        print(f"Start {s.start} (Loss:{l0:.4f})"); n=0; noimp=0
        while s.heap and n<max_iter:
            l,p=heapq.heappop(s.heap)
            if p in s.visited: continue
            s.visited.add(p); s._topk(l,p); n+=1
            if l<s.best[0]:
                s.best=(l,p); print(f"[{n}] New Best! L:{l:.4f} | Th:{p[0]:.2f} M:{p[1]:.5f} X:{p[2]:.2f}"); noimp=0
            else: noimp+=1
            if noimp>=patience: print(f"\n[!] Early stop. Best:{s.best[0]:.4f}"); break
            for q in s._nbrs(p):
                if q not in s.visited: heapq.heappush(s.heap,(s.loss(*q),q))
        print(f"Done {n} iters."); return sorted(s.topk,key=lambda x:x[0],reverse=True)

# --- Run ---
bounds={'th':(0,50),'m':(-.05,.05),'xo':(0,100)}
steps={'th':1,'m':.001,'xo':1}
hc=HillClimb((25,0,50),steps,bounds,loss,K=5)
res=hc.search(patience=10)
if not res: sys.exit("No results")

print(f"\n--- Top {len(res)} Results ---")
for negl,(th,m,xo) in res:
    print(f"Th:{th:.4f}, M:{m:.5f}, X:{xo:.4f} | Loss:{-negl:.4f}")
best=-res[0][0]; th,m,xo=res[0][1]
print(f"Best Th:{th:.4f}, M:{m:.5f}, X:{xo:.4f} | Loss:{best:.4f}")
