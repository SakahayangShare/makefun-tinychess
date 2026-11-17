import json,os,urllib.request
R=range;S=str;N=30000;n=0;P=".PNBRQK..pnbrqk"
K=(-33,-31,-18,-14,14,18,31,33);L=(-17,-16,-15,-1,1,15,16,17);D=(-17,-15,15,17);O=(-16,-1,1,16)
q=lambda s:chr(97+(s&7))+S((s>>4)+1)
ss=lambda s:ord(s[0])-97+(int(s[1])-1)*16
class Position:
 def __init__(self,f="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
  p=f.split();b=[0]*128;r=7;c=0;k=[0,0]
  for x in p[0]:
   if x=='/':r-=1;c=0
   elif x.isdigit():c+=int(x)
   else:
    v=P.index(x);s=(r<<4)+c;b[s]=v
    if v&7==6:k[v>>3]=s
    c+=1
  self.b=b;self.t=8*(p[1]=='b');self.c=sum(m for h,m in zip('KQkq',[1,2,4,8])if len(p)>2 and h in p[2]);self.e=ss(p[3])if len(p)>3 and p[3]!='-'else 0;self.u=[];self.k=k
 def attacked(self,s,c):
  if c==0:
   for d in(-15,-17):
    if not((t:=s+d)&136)and self.b[t]==1:return 1
  else:
   for d in(15,17):
    if not((t:=s+d)&136)and self.b[t]==9:return 1
  for d in K:
   if not((t:=s+d)&136)and self.b[t]==c+2:return 1
  for d in L:
   if not((t:=s+d)&136)and self.b[t]==c+6:return 1
  for d,t in((O,(4,5)),(D,(3,5))):
   for x in d:
    z=s+x
    while not(z&136):
     if(p:=self.b[z]):
      if(p&8)==c and(p&7)in t:return 1
      break
     z+=x
  return 0
 def king_sq(self,c):return self.k[c>>3]
 def gen_moves(self):
  m=[];o=8-self.t
  for s in R(128):
   if s&136 or not(p:=self.b[s])or p&8!=self.t:continue
   t,r=p&7,s>>4
   if t==1:
    d=16 if self.t==0 else -16;sr=1 if self.t==0 else 6;er=6 if self.t==0 else 1;f=s+d
    if not(f&136)and not self.b[f]:
     if r==er:
      for pr in(2,3,4,5):m.append(s|(f<<7)|(pr<<14))
     else:
      m.append(s|(f<<7));dr=s+2*d
      if r==sr and not self.b[dr]:m.append(s|(dr<<7))
    for x in(-1,1):
     f=s+d+x
     if not(f&136)and((self.b[f]and(self.b[f]&8)==o)or f==self.e):
      if r==er:
       for pr in(2,3,4,5):m.append(s|(f<<7)|(pr<<14))
      else:m.append(s|(f<<7))
   elif t==2 or t==6:
    for d in(K if t==2 else L):
     if not((f:=s+d)&136)and(not self.b[f] or(self.b[f]&8)==o):m.append(s|(f<<7))
    if t==6:
     if self.t==0 and s==4:
      if self.c&1 and not any(self.b[5:7])and not any(self.attacked(x,8)for x in(4,5,6)):m.append(4|768)
      if self.c&2 and not any(self.b[1:4])and not any(self.attacked(x,8)for x in(4,3,2)):m.append(4|256)
     elif self.t==8 and s==116:
      if self.c&4 and not any(self.b[117:119])and not any(self.attacked(x,0)for x in(116,117,118)):m.append(116|15104)
      if self.c&8 and not any(self.b[113:116])and not any(self.attacked(x,0)for x in(116,115,114)):m.append(116|14592)
   else:
    for d in(D,O,D+O)[t-3]:
     z=s+d
     while not(z&136):
      if not self.b[z]:m.append(s|(z<<7))
      else:
       if self.b[z]&8==o:m.append(s|(z<<7))
       break
      z+=d
  return m
 def make(self,m):
  f,t,pr=m&127,m>>7&127,m>>14&7;p=self.b[f];cp=self.b[t];e,c,k=self.e,self.c,self.k[:]
  if e and(p&7)==1 and t==e:cp=9-self.t;self.b[t-(16 if self.t==0 else -16)]=0
  self.u.append((cp,c,e,m,k))
  if(p&7)==6:
   if abs(f-t)==2:
    if t==6:self.b[5]=self.b[7];self.b[7]=0
    elif t==2:self.b[3]=self.b[0];self.b[0]=0
    elif t==118:self.b[117]=self.b[119];self.b[119]=0
    elif t==114:self.b[115]=self.b[112];self.b[112]=0
   self.k[self.t>>3]=t
  self.b[f]=0;self.b[t]=self.t|pr if pr else p
  self.e=(f+t)//2 if(p&7==1 and abs(f-t)==32)else 0
  if f==4 or t==4:self.c&=~3
  if f==116 or t==116:self.c&=~12
  if f==0 or t==0:self.c&=~2
  if f==7 or t==7:self.c&=~1
  if f==112 or t==112:self.c&=~8
  if f==119 or t==119:self.c&=~4
  self.t=8-self.t
 def unmake(self,m):
  cp,c,e,m,k=self.u.pop();f,t=m&127,m>>7&127;self.t=8-self.t;p=self.b[t];self.b[t]=0;self.b[f]=self.t|1 if m>>14&7 else p
  if e and(p&7)==1 and t==e:self.b[t-(16 if self.t==0 else -16)]=cp
  else:self.b[t]=cp
  if(p&7)==6 and abs(f-t)==2:
   if t==6:self.b[7]=self.b[5];self.b[5]=0
   elif t==2:self.b[0]=self.b[3];self.b[3]=0
   elif t==118:self.b[119]=self.b[117];self.b[117]=0
   elif t==114:self.b[112]=self.b[115];self.b[115]=0
  self.c,self.e,self.k=c,e,k
 def eval(self):
  V=[0,100,320,330,500,900,0];b=self.b;w=[any(not(s&136)and(s&7)==f and b[s]==1 for s in R(128))for f in R(8)];l=[any(not(s&136)and(s&7)==f and b[s]==9 for s in R(128))for f in R(8)]
  h=min(24,sum(4 if(p:=b[s]&7)==5 else(2 if p==4 else(1 if p in(2,3)else 0))for s in R(128)if not(s&136)and b[s]))
  W=E=B=O=0
  for s in R(128):
   if s&136 or not(p:=b[s]):continue
   f,r,c,t=s&7,s>>4,p&8,p&7;m=7-r if c else r;z=7-abs(2*f-7)+7-abs(2*m-7)
   if t==1:x,y=100+(m-1)*6+(5 if 2<f<5 else 0),100+(m-1)*10+(5 if 2<f<5 else 0)
   elif t==6:x,y=z*-4,z*3
   else:x,y=V[t]+z,V[t]+(z//2 if t==5 else(z if t!=4 else 0))
   if t==4:
    if m==6:x+=25;y+=25
    if not w[f]and not l[f]:x+=12;y+=12
   if c:B+=x;O+=y
   else:W+=x;E+=y
  if sum(1 for s in R(128)if not(s&136)and b[s]==3)>=2:W+=30;E+=30
  if sum(1 for s in R(128)if not(s&136)and b[s]==11)>=2:B+=30;O+=30
  s=(W*h+E*(24-h))//24-(B*h+O*(24-h))//24
  return-s if self.t else s
 def q(self,a,b):
  global n;n+=1;ic=self.attacked(self.k[self.t>>3],8-self.t);v=self.eval()
  if v>=b:return b
  if a<v:a=v
  for m in self.gen_moves():
   p=self.b[m>>7&127]
   if not ic and not p and not(m>>14&7):continue
   self.make(m)
   if not self.attacked(self.k[1-self.t//8],self.t):
    s=-self.q(-b,-a);self.unmake(m)
    if s>=b:return b
    if s>a:a=s
   else:self.unmake(m)
  return a
 def nm(self,d,a,b,p):
  global n
  if n>N:return 0
  ms=[m for m in self.gen_moves()if(self.make(m),not self.attacked(self.k[1-self.t//8],self.t),self.unmake(m))[1]]
  if not ms:return(p-100000)if self.attacked(self.k[self.t>>3],8-self.t)else 0
  if d==0:return self.q(a,b)
  for m in ms:
   n+=1;self.make(m);s=-self.nm(d-1,-b,-a,p+1);self.unmake(m)
   if s>=b:return b
   if s>a:a=s
   if n>N:break
  return a
 def search_root(self):
  global n;n=0;bm=None;lms=[m for m in self.gen_moves()if(self.make(m),not self.attacked(self.k[1-self.t//8],self.t),self.unmake(m))[1]]
  if not lms:return None
  bm=lms[0]
  for d in R(1,100):
   a,bs,cb=-200000,-200000,None
   for m in lms:
    n+=1;self.make(m);s=-self.nm(d-1,-200000,-a,1);self.unmake(m)
    if s>bs:bs=s;cb=m
    if s>a:a=s
    if n>N:break
   if n>N:break
   if cb is not None:bm=cb
  return bm
if"MAKEFUN_ENV_URL"in os.environ:
 u=os.environ["MAKEFUN_ENV_URL"]
 def p(x,b):return json.load(urllib.request.urlopen(urllib.request.Request(u+x,data=json.dumps(b).encode(),headers={"content-type":"application/json"})))
 g=p("/game",{})
 while g["status"]!="done":
  m=Position(g["fen"]).search_root();u_m=q(m&127)+q(m>>7&127)+('nbrq'[(m>>14&7)-2]if(m>>14)&7 else'')if m else g["legal_moves"][0]
  g=p("/move",{"game":g["game"],"move":u_m})
