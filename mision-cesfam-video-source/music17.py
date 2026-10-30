import numpy as np, wave
SR=44100; TOT=58.0; N=int(TOT*SR); D=46.0
rng=np.random.default_rng(21)
M=np.zeros((N,2)); H=np.zeros((N,2)); X=np.zeros((N,2))
def mf(m): return 440*2**((m-69)/12)
def onepole(x,c):
    y=np.empty_like(x); a=0.0
    for k in range(len(x)): a+=c*(x[k]-a); y[k]=a
    return y
def add(sig,t,g=1.0,pan=0.0,buf=None):
    buf=M if buf is None else buf
    i=int(round(t*SR))
    if i>=N or i<0: return
    s=sig[:N-i]*g; buf[i:i+len(s),0]+=s*(1-max(pan,0)); buf[i:i+len(s),1]+=s*(1+min(pan,0))
def T(d): return np.arange(int(d*SR))/SR
# ---------- instruments ----------
def marimba(m,d=0.6):
    t=T(d); f=mf(m); a=np.minimum(1,t/0.002)
    return a*(np.sin(2*np.pi*f*t)*np.exp(-t/0.32)+0.35*np.sin(2*np.pi*4*f*t)*np.exp(-t/0.05)+0.08*np.sin(2*np.pi*9.9*f*t)*np.exp(-t/0.015))
def glock(m,d=1.2):
    t=T(d); f=mf(m)
    return np.sin(2*np.pi*f*t)*np.exp(-t/0.8)+0.35*np.sin(2*np.pi*2.76*f*t)*np.exp(-t/0.22)+0.15*np.sin(2*np.pi*5.4*f*t)*np.exp(-t/0.08)
def pizz(m,d=0.35):
    t=T(d); f=mf(m); s=(2*((f*t)%1)-1)*0.5+np.sin(2*np.pi*f*t)
    return onepole(s,0.22)*np.exp(-t/0.11)*np.minimum(1,t/0.003)
def guitar(m,d=1.0):
    f=mf(m); n=int(d*SR); p=int(SR/f); buf=rng.uniform(-1,1,p); out=np.empty(n)
    for i in range(n):
        out[i]=buf[i%p]; buf[i%p]=0.996*0.5*(buf[i%p]+buf[(i+1)%p])
    return out
def bass(m,d=0.3):
    t=T(d); f=mf(m); tri=2*np.abs(2*((f*t)%1)-1)-1
    return (0.7*tri+np.sin(2*np.pi*f*t))*np.exp(-t/0.14)*np.minimum(1,t/0.004)
def woodblock():
    t=T(0.08); return (np.sin(2*np.pi*880*t)+0.6*np.sin(2*np.pi*1460*t))*np.exp(-t/0.02)
def clap():
    t=T(0.2); x=rng.standard_normal(len(t)); x=x-onepole(x,0.25)
    e=np.exp(-t/0.05)*(1+0.8*np.exp(-((t-0.01)/0.003)**2)+0.6*np.exp(-((t-0.022)/0.003)**2)); return x*e
def shaker():
    t=T(0.06); x=rng.standard_normal(len(t)); x=x-onepole(x,0.6); return x*np.exp(-t/0.018)
def kick(g=1.0):
    t=T(0.35); return np.sin(2*np.pi*np.cumsum(50+80*np.exp(-t/0.03))/SR)*np.exp(-t/0.16)
def tom(f0=150):
    t=T(0.35); return np.sin(2*np.pi*np.cumsum(f0*0.62+f0*0.4*np.exp(-t/0.05))/SR)*np.exp(-t/0.18)
def whistle(m,d):
    t=T(d); f=mf(m)*(1+0.006*np.sin(2*np.pi*5.5*t)*np.minimum(1,t/0.15))
    e=np.minimum(1,t/0.04)*np.minimum(1,np.maximum(0,(d-t))/0.06)
    br=onepole(rng.standard_normal(len(t)),0.3)*0.03
    return (np.sin(2*np.pi*np.cumsum(f)/SR)+0.08*np.sin(4*np.pi*np.cumsum(f)/SR)+br)*e
def slide(m0,m1,d=0.3):
    t=T(d); f=mf(m0)*(mf(m1)/mf(m0))**(t/d); e=np.minimum(1,t/0.02)*np.minimum(1,(d-t)/0.05)
    return np.sin(2*np.pi*np.cumsum(f*(1+0.01*np.sin(2*np.pi*8*t)))/SR)*e
def pad(ms,d,att=0.3):
    t=T(d); s=sum(np.sin(2*np.pi*mf(m)*t)+0.5*np.sin(2*np.pi*mf(m)*1.004*t) for m in ms)
    return s*np.minimum(1,t/att)*np.minimum(1,(d-t)/0.3)
WB,CL,SH=woodblock(),clap(),shaker()
CH={'C':[60,64,67],'G':[55,59,62],'Am':[57,60,64],'F':[53,57,60],'E':[52,56,59],'Dm':[50,53,57]}
ROOT={'C':48,'G':43,'Am':45,'F':41,'E':40,'Dm':38}
def bars(t0,seq):  # seq of (chord, beats)
    out=[]; t=t0
    for c,b in seq: out.append((t,c,b*0.5)); t+=b*0.5
    return out
def chord_at(bl,t):
    for t0,c,d in bl:
        if t0<=t<t0+d: return c
    return bl[-1][1]



_add=add
def _w(t):
    if t<7.5: return t
    if t<41.5: return t+0.5
    if t<44.9: return 42.0+(t-41.5)*0.6
    return t
def add(sig,t,g=1.0,pan=0.0,buf=None): _add(sig,_w(t),g,pan,buf)
# ---------- 0-4.5 intro: waiting ----------
add(pad([57,60,64],4.4,0.6),0.0,0.02)
for i,m_ in enumerate([69,72,76,74,72,69]): add(marimba(m_,0.8),0.1+i*0.5,0.045)
t=T(0.5); x=onepole(rng.standard_normal(len(t)),0.08); add(x*(t/0.5)**2,1.2,0.05)          # push-in
add(glock(64,1.2),1.75,0.06); add(glock(63,1.2),1.75,0.04)                                     # 'en 3 semanas'
t=T(1.0); x=onepole(rng.standard_normal(len(t)),0.05); add((x*0.8+0.25*np.sin(2*np.pi*np.cumsum(200+900*(t/1.0)**2)/SR))*(t/1.0)**2.5,3.5,0.14)
# ---------- 4.5-7.5 sting (calm, clean) ----------
t=T(1.6); add(np.sin(2*np.pi*np.cumsum(32+40*np.exp(-t/0.12))/SR)*np.exp(-t/0.6),4.5,0.6)
for i,m_ in enumerate([72,76,79,84]): add(glock(m_),4.75+i*0.12,0.09,pan=(-0.2+0.13*i))
add(marimba(60,1.2),4.75,0.11); add(marimba(67,1.2),4.75,0.07); add(pad([60,64,67,72],2.9,0.3),4.6,0.03)
add(glock(88,1.0),5.5,0.04); add(glock(91,1.0),5.62,0.03)
LOOP=['C','Am','F','G']
MEL=[[76,79,84,79],[76,72,69,72],[77,81,84,81],[79,74,71,74],[76,79,84,86],[84,81,76,81],[77,81,84,88],[86,83,79,74]]
def theme_bar(t0,chord,mb,mel=True,mel_g=0.075,drums=True,kick4=False,shk=0.022,inst='mar'):
    for i,m in enumerate(MEL[mb]):
        if mel:
            if inst=='mar': add(marimba(m,0.6),t0+i*0.5,mel_g,pan=0.05)
            else: add(glock(m,0.9),t0+i*0.5,mel_g*0.7)
    for i in range(4):
        tb=t0+i*0.5
        if i in (0,2): add(bass(ROOT[chord]+(0 if i==0 else 7),0.45),tb,0.15)
        for mm in CH[chord]: add(marimba(mm+12,0.25),tb+0.25,0.016)
        add(SH,tb+0.25,shk,pan=0.25)
        if drums and i in (1,3): add(CL,tb,0.05)
        if kick4: add(kick(),tb,0.26)


def arp(t0,ms,g=0.05,dt=0.12):
    for i,m_ in enumerate(ms): add(glock(m_),t0+i*dt,g)
# story theme from 7.5 to 31.0 (bars every 2 s)
for k in range(12):
    t0=7.5+2*k; c=LOOP[k%4]; mb=k%8
    if t0<14.5: theme_bar(t0,c,mb)
    elif t0<18.5: theme_bar(t0,c,mb,drums=False,mel_g=0.09,inst='glk',shk=0.015)   # Jorge: softer
    else: theme_bar(t0,c,mb)
# 31.0-31.5: everything stops (short pause) -> 31.5 climax push
M[int(31.5*SR):int(32.0*SR)]*=np.linspace(1,0,int(0.5*SR))[:,None]
t=T(2.0); add(np.sin(2*np.pi*np.cumsum(34+45*np.exp(-t/0.1))/SR)*np.exp(-t/0.7),31.5,0.25)
add(pad([48,55,60,64,67,72],4.0,0.05),31.5,0.022)
for k in range(2):
    t0=31.5+2*k; theme_bar(t0,['C','F'][k],[4,6][k],kick4=True,mel_g=0.08,shk=0.025)
for i,m_ in enumerate([84,88,91,96]): add(glock(m_,1.0),31.5+i*0.1,0.06)
arp(33.5,[79,84,88],0.05,0.16)
# teaser 35.5-41.5: energy
for k in range(3):
    t0=35.5+2*k; theme_bar(t0,LOOP[k%4],(k+2)%8,kick4=True,shk=0.03)
# small musical hits
add(glock(79),10.8,0.05); add(glock(84),11.1,0.05)          # rule checks
arp(12.6,[72,76,79,84])                                      # Atención +5
arp(20.85,[84,88,91],0.045)                                  # LIBRE
arp(26.9,[72,76,79,84],0.05,0.1)                             # ¡Hora aceptada!
arp(29.65,[76,79,84,88],0.05,0.08)                           # Camila fills 9:30
for m_ in [60,64,67,72]: add(marimba(m_,0.8),37.1,0.06)      # urgencia
# ---------- 41.5-46.5 core message: calm ----------
for m_ in [48,60,64,67]: add(marimba(m_,1.0),41.5,0.05)
add(pad([48,55,60,64],5.0,0.4),41.5,0.03)
add(glock(84),41.7,0.05); add(glock(88),43.3,0.05)
# ---------- HYPE 48-53 ----------
def saw(f,tt): return 2*((f*tt)%1)-1
def supersaw(ms,dur,dec=None):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        f=mf(m)
        for d in [-0.012,-0.006,0,0.006,0.012]: s+=saw(f*(1+d),tt+rng.random())/5
    s=onepole(s,0.18); e=np.minimum(1,tt/0.01)*(np.exp(-tt/dec) if dec else np.minimum(1,(dur-tt)/0.03)); return s*e
def snare():
    t=T(0.18); x=rng.standard_normal(len(t)); x=x-onepole(x,0.2); return (x*0.8+0.4*np.sin(2*np.pi*190*t))*np.exp(-t/0.06)
def hkick():
    t=T(0.4); return np.sin(2*np.pi*np.cumsum(48+90*np.exp(-t/0.03))/SR)*np.exp(-t/0.2)
def ohat():
    t=T(0.2); x=rng.standard_normal(len(t)); x=x-onepole(x,0.6); return x*np.exp(-t/0.07)
SN,K,OH=snare(),hkick(),ohat()
t=D-1.0; step=0.125
while t<D-1e-6:
    add(SN,t,0.06+0.10*(t-(D-1.0)),buf=H); t+=step
    if t>=D-0.5: step=0.0625
tt=T(1.0); add(onepole(rng.standard_normal(len(tt)),0.1)*tt**2*0.6+0.25*np.sin(2*np.pi*np.cumsum(300+1500*tt**2)/SR)*tt**2,D-1.0,0.12,buf=H)
chords=[(D,[60,64,67,72]),(D+1,[55,59,62,67]),(D+2,[57,60,64,69]),(D+3,[53,57,60,65]),(D+3.5,[55,59,62,67])]
for (t0,ms),(t1,_) in zip(chords,chords[1:]+[(D+4,None)]):
    add(supersaw(ms,t1-t0),t0,0.10,pan=0.1,buf=H); add(supersaw([ms[0]-12],t1-t0),t0,0.10,buf=H)
for k in range(8):
    tb=D+k*0.5; add(K,tb,0.75,buf=H); add(OH,tb+0.25,0.05,pan=0.3,buf=H)
    if k%2==1: add(SN,tb,0.16,buf=H)
pat=[0,1,2,3,2,1,2,3]
for k in range(int(3.5/0.25)):
    tb=D+k*0.25; ms=[c for c in chords if c[0]<=tb+1e-9][-1][1]; m=ms[pat[k%8]]+12
    add(marimba(m,0.3),tb,0.06,pan=(-0.3 if k%2 else 0.3),buf=H)
for i in range(8): add(SN,D+3.5+i*0.0625,0.08+0.02*i,buf=H)
for tc,g in [(D,1.0),(D+4,1.2)]:
    tt=T(2.2); x=rng.standard_normal(len(tt)); x=x-onepole(x,0.4)
    add(x*np.exp(-tt/0.8),tc,0.10*g,buf=H); add(K,tc,0.9,buf=H)
add(supersaw([48,60,64,67,72,76],2.4,dec=0.9),D+4,0.16,buf=H)
tt=T(1.8); add(np.sin(2*np.pi*np.cumsum(32+40*np.exp(-tt/0.1))/SR)*np.exp(-tt/0.6),D+4,0.7,buf=H)
pump=np.ones(N)
for k in range(8):
    i=int((D+k*0.5)*SR); m=int(0.35*SR); tt=np.arange(m)/SR; pump[i:i+m]=np.minimum(pump[i:i+m],1-0.55*np.exp(-tt/0.09))
H*=pump[:,None]


# outro tail (51.5-59.5), steady for scanning
add(pad([60,64,67,72],7.8,0.6),D+4.4,0.028)
for k in range(14): add(glock([72,76,79,76][k%4],0.8),D+5+k*0.5,0.026)
# ---------- SFX (footsteps, doors, heartbeat, siren...) ----------
def step_snd():
    t=T(0.09); x=onepole(rng.standard_normal(len(t)),0.12); return (x*1.5+np.sin(2*np.pi*95*t))*np.exp(-t/0.03)
def pop_snd():
    t=T(0.09); return np.sin(2*np.pi*np.cumsum(520+700*t/0.09)/SR)*np.exp(-t/0.035)
def click_snd():
    t=T(0.03); return np.sin(2*np.pi*2400*t)*np.exp(-t/0.006)
def flick_snd():
    t=T(0.18); x=rng.standard_normal(len(t)); x=x-onepole(x,0.3); return x*np.exp(-((t-0.05)/0.04)**2)
def hiss(d):
    t=T(d); x=rng.standard_normal(len(t)); x=x-onepole(x,0.25); x=onepole(x,0.5); return x*np.sin(np.pi*t/d)
def door(d=0.8):
    t=T(d); n=len(t); x=rng.standard_normal(n); x=x-onepole(x,0.35); x=onepole(x,0.6)
    env=np.minimum(1,t/0.05)*np.exp(-np.maximum(0,t-0.1)/0.35)
    rumble=np.sin(2*np.pi*np.cumsum(70+30*np.sin(2*np.pi*3*t))/SR)*np.sin(np.pi*t/d)
    m=int(0.06*SR); th=np.zeros(n); th[n-m:]=np.sin(2*np.pi*110*np.arange(m)/SR)*np.exp(-np.arange(m)/SR/0.02)
    return x*env*1.4+rumble*0.5+th*1.2
def heart():
    t=T(0.5)
    def b(t0):
        u=np.maximum(0,t-t0); return (t>=t0)*(np.sin(2*np.pi*65*u)+0.6*np.sin(2*np.pi*130*u)+0.25*np.sin(2*np.pi*260*u))*np.exp(-u/0.07)
    return b(0)+0.75*b(0.2)
def siren(d):
    t=T(d); f=np.where((t//0.38)%2==0,740.0,980.0)*(1+0.01*np.sin(2*np.pi*6*t)); tri=2*np.abs(2*((np.cumsum(f)/SR)%1)-1)-1
    return onepole(tri,0.25)*np.minimum(1,t/0.3)*np.minimum(1,(d-t)/0.4)
def rattle(d):
    n=int(d*SR); x=np.zeros(n)
    for k in range(int(d/0.045)):
        i=int(k*0.045*SR+rng.integers(0,200)); m=int(0.012*SR)
        if i+m<n: x[i:i+m]+=rng.standard_normal(m)*np.exp(-np.arange(m)/SR/0.003)
    return x
def swipe():
    t=T(0.22); x=rng.standard_normal(len(t)); x=x-onepole(x,0.4); return x*np.sin(np.pi*t/0.22)**2
def whoosh(d=0.45):
    t=T(d); x=onepole(rng.standard_normal(len(t)),0.08); return x*(t/d)**2
ST,PO,CK,FL,HB=step_snd(),pop_snd()*0.6,click_snd(),flick_snd(),heart()
def steps(t0,t1,dt=0.35,g=0.07,pan=0.0):
    t=t0
    while t<t1: add(ST,t,g*0.6,pan=pan,buf=X); t+=dt

def buzz(d):
    t=T(d); return np.sin(2*np.pi*150*t)*(0.5+0.5*np.sign(np.sin(2*np.pi*4*t)))*np.minimum(1,t/0.02)

def buzz(d):
    t=T(d); return np.sin(2*np.pi*150*t)*(0.5+0.5*np.sign(np.sin(2*np.pi*4*t)))*np.minimum(1,t/0.02)
add(PO,1.75,0.04,buf=X)
for i in range(6): add(PO,2.8+i*0.13+(0.27 if i>=3 else 0),0.025,buf=X)
add(whoosh(0.5),5.7,0.02,buf=X)
steps(9.5,10.5,0.25,0.06,-0.3); add(PO,10.0,0.05,buf=X); add(PO,10.4,0.05,buf=X)
add(CK,11.6,0.12,buf=X); add(whoosh(0.6),11.75,0.03,buf=X); add(door(0.8),12.5,0.14,0.3,buf=X); add(PO,12.6,0.05,buf=X)
add(PO,14.8,0.05,buf=X); add(swipe(),16.0,0.05,buf=X); add(PO,16.05,0.04,buf=X); add(whoosh(0.5),17.85,0.04,buf=X)
add(whoosh(0.4),18.45,0.03,buf=X); add(CK,19.7,0.13,buf=X); add(whoosh(0.5),20.15,0.035,buf=X); add(PO,21.1,0.05,buf=X)
add(whoosh(0.5),21.9,0.035,buf=X); add(CK,22.8,0.13,buf=X); add(PO,23.1,0.05,buf=X); add(whoosh(0.5),23.9,0.04,buf=X)
add(whoosh(0.4),24.45,0.03,buf=X); add(buzz(0.7),25.1,0.05,0.3,buf=X); add(PO,25.0,0.05,buf=X); add(CK,26.45,0.13,buf=X); add(whoosh(0.5),27.9,0.04,buf=X)
add(whoosh(0.4),28.45,0.03,buf=X); add(PO,29.4,0.05,buf=X); add(PO,29.95,0.05,buf=X); add(whoosh(0.5),30.9,0.03,buf=X)
add(CK,37.0,0.12,buf=X); add(PO,37.1,0.05,buf=X); add(door(0.8),37.5,0.12,0.3,buf=X); add(whoosh(0.4),38.3,0.04,buf=X); add(siren(1.8),38.7,0.035,0.3,buf=X)
for tb in [D+1,D+2,D+3]: add(swipe(),tb-0.05,0.04,buf=X)
for tb in [7.5,14.5,35.5,41.5]: add(whoosh(0.4),tb-0.4,0.035,buf=X)
g=np.ones(N); a,b=int(8.0*SR),int(45.0*SR); g[a:b]=2.3; g[a-int(0.3*SR):a]=np.linspace(1,2.3,int(0.3*SR)); g[b:b+int(0.5*SR)]=np.linspace(2.3,1,int(0.5*SR))
g[:int(4.5*SR)]=1.8
M*=g[:,None]; X*=1.6
L=M+H*1.0+X
L[-int(1.5*SR):]*=np.linspace(1,0,int(1.5*SR))[:,None]
L=np.tanh(L*1.3)/np.tanh(1.3); L/=np.max(np.abs(L))/0.9
with wave.open('music17.wav','wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((L*32767).astype(np.int16).tobytes())
for s0 in [1,5,10,16,20,27,31,32,37,43,48,55]:
    seg=L[int(s0*SR):int((s0+1)*SR)]; print(s0, round(20*np.log10(np.sqrt((seg**2).mean())+1e-9),1))
