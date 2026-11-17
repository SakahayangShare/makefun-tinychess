import json,os,urllib.request
R=range;S=str;NCAP=30000;nodes=0
PC={'.':0,'P':1,'N':2,'B':3,'R':4,'Q':5,'K':6,'p':9,'n':10,'b':11,'r':12,'q':13,'k':14}
KN=(-33,-31,-18,-14,14,18,31,33);K8=(-17,-16,-15,-1,1,15,16,17);DG=(-17,-15,15,17);ST=(-16,-1,1,16)
sqs=lambda s:chr(97+(s&7))+S((s>>4)+1)
ssq=lambda s:ord(s[0])-97+(int(s[1])-1)*16
class Position:
 def __init__(self,f="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
  p=f.split();b=[0]*128;r=7;c=0
  for x in p[0]:
   if x=='/':r-=1;c=0
   elif x.isdigit():c+=int(x)
   else:b[(r<<4)+c]=PC[x];c+=1
  self.b=b;self.t=8*(p[1]=='b');self.c=sum(mk for ch,mk in zip('KQkq',[1,2,4,8])if len(p)>2 and ch in p[2]);self.e=ssq(p[3])if len(p)>3 and p[3]!='-'else 0;self.hm=int(p[4])if len(p)>4 else 0;self.u=[]
 def attacked(self,sq,col):
  if col==0:
   for ds in(-15,-17):
    if not((ts:=sq+ds)&0x88)and self.b[ts]==1:return 1
  else:
   for ds in(15,17):
    if not((ts:=sq+ds)&0x88)and self.b[ts]==9:return 1
  for ds in KN:
   if not((ts:=sq+ds)&0x88)and self.b[ts]==col+2:return 1
  for ds in K8:
   if not((ts:=sq+ds)&0x88)and self.b[ts]==col+6:return 1
  for ds,pt in((ST,(4,5)),(DG,(3,5))):
   for d in ds:
    ts=sq+d
    while not(ts&0x88):
     if(p:=self.b[ts]):
      if(p&8)==col and((p&7)in pt):return 1
      break
     ts+=d
  return 0
 def king_sq(self,col):
  for s in R(128):
   if not(s&0x88)and self.b[s]==col+6:return s
 def gen_moves(self):
  m=[];ot=8-self.t
  for sq in R(128):
   if sq&0x88:continue
   p=self.b[sq]
   if not p or(p&8)!=self.t:continue
   pt=p&7;rk=sq>>4
   if pt==1:
    d=16 if self.t==0 else -16;sr=1 if self.t==0 else 6;er=6 if self.t==0 else 1;fr=sq+d
    if not(fr&0x88)and not self.b[fr]:
     if rk==er:
      for pr in(2,3,4,5):m.append(sq|(fr<<7)|(pr<<14))
     else:
      m.append(sq|(fr<<7));dr=sq+2*d
      if rk==sr and not self.b[dr]:m.append(sq|(dr<<7))
    for df in(-1,1):
     ts=sq+d+df
     if not(ts&0x88):
      tg=self.b[ts]
      if(tg and(tg&8)==ot)or ts==self.e:
       if rk==er:
        for pr in(2,3,4,5):m.append(sq|(ts<<7)|(pr<<14))
       else:m.append(sq|(ts<<7))
   elif pt==2:
    for ds in KN:
     if not((ts:=sq+ds)&0x88):
      tg=self.b[ts]
      if not tg or(tg&8)==ot:m.append(sq|(ts<<7))
   elif pt in(3,4,5):
    for d in(DG,ST,DG+ST)[pt-3]:
     ts=sq+d
     while not(ts&0x88):
      tg=self.b[ts]
      if not tg:m.append(sq|(ts<<7))
      else:
       if(tg&8)==ot:m.append(sq|(ts<<7))
       break
      ts+=d
   elif pt==6:
    for ds in K8:
     if not((ts:=sq+ds)&0x88):
      tg=self.b[ts]
      if not tg or(tg&8)==ot:m.append(sq|(ts<<7))
    if self.t==0 and sq==4:
     if(self.c&1)and not self.b[5]and not self.b[6] and not self.attacked(4,8)and not self.attacked(5,8)and not self.attacked(6,8):m.append(4|(6<<7))
     if(self.c&2)and not self.b[3]and not self.b[2]and not self.b[1] and not self.attacked(4,8)and not self.attacked(3,8)and not self.attacked(2,8):m.append(4|(2<<7))
    elif self.t==8 and sq==116:
     if(self.c&4)and not self.b[117]and not self.b[118] and not self.attacked(116,0)and not self.attacked(117,0)and not self.attacked(118,0):m.append(116|(118<<7))
     if(self.c&8)and not self.b[115]and not self.b[114]and not self.b[113] and not self.attacked(116,0)and not self.attacked(115,0)and not self.attacked(114,0):m.append(116|(114<<7))
  return m
 def make(self,m):
  b=self.b;fs=m&0x7F;ts=(m>>7)&0x7F;pr=(m>>14)&7;p=b[fs];cp=b[ts];ep=self.e;cc=self.c;hm=self.hm
  if ep and(p&7)==1 and ts==ep:cp=9 if self.t==0 else 1;b[ts-16 if self.t==0 else ts+16]=0
  self.u.append((cp,cc,ep,hm,m))
  if(p&7)==6 and abs(fs-ts)==2:
   if ts==6:b[5]=b[7];b[7]=0
   elif ts==2:b[3]=b[0];b[0]=0
   elif ts==118:b[117]=b[119];b[119]=0
   elif ts==114:b[115]=b[112];b[112]=0
  b[fs]=0;b[ts]=self.t|pr if pr else p
  self.e=(fs+ts)//2 if((p&7)==1 and abs(fs-ts)==32)else 0
  if fs==4 or ts==4:self.c&=~3
  if fs==116 or ts==116:self.c&=~12
  if fs==0 or ts==0:self.c&=~2
  if fs==7 or ts==7:self.c&=~1
  if fs==112 or ts==112:self.c&=~8
  if fs==119 or ts==119:self.c&=~4
  self.t=8-self.t;self.hm=0 if((p&7)==1 or cp)else self.hm+1
 def unmake(self,m):
  b=self.b;cp,cc,ep,hm,m=self.u.pop();fs=m&0x7F;ts=(m>>7)&0x7F;pr=(m>>14)&7;self.t=8-self.t
  np=b[ts];b[ts]=0;b[fs]=self.t|1 if pr else np
  if ep and(np&7)==1 and ts==ep:b[ts-16 if self.t==0 else ts+16]=cp
  else:b[ts]=cp
  if(np&7)==6 and abs(fs-ts)==2:
   if ts==6:b[7]=b[5];b[5]=0
   elif ts==2:b[0]=b[3];b[3]=0
   elif ts==118:b[119]=b[117];b[117]=0
   elif ts==114:b[112]=b[115];b[115]=0
  self.c=cc;self.e=ep;self.hm=hm
 def eval(self):
  V=[0,100,320,330,500,900,0];wf=[any(not(s&0x88)and(s&7)==f and self.b[s]==1 for s in R(128))for f in R(8)];bf=[any(not(s&0x88)and(s&7)==f and self.b[s]==9 for s in R(128))for f in R(8)]
  ph=min(24,sum(4 if(p:=self.b[s]&7)==5 else(2 if p==4 else(1 if p in(2,3)else 0))for s in R(128)if not(s&0x88)and self.b[s]))
  mw=ew=mb=eb=0
  for s in R(128):
   if s&0x88 or not(p:=self.b[s]):continue
   f=s&7;r=s>>4;c=p&8;t=p&7;mr=7-r if c else r;z=7-abs(2*f-7)+7-abs(2*mr-7)
   if t==1:m,e=100+(mr-1)*6+(5 if 2<f<5 else 0),100+(mr-1)*10+(5 if 2<f<5 else 0)
   elif t==6:m,e=z*-4,z*3
   else:m,e=V[t]+z,V[t]+(z//2 if t==5 else(z if t!=4 else 0))
   if t==4:
    if mr==6:m+=25;e+=25
    if not wf[f]and not bf[f]:m+=12;e+=12
   if c:mb+=m;eb+=e
   else:mw+=m;ew+=e
  if sum(1 for s in R(128)if not(s&0x88)and self.b[s]==3)>=2:mw+=30;ew+=30
  if sum(1 for s in R(128)if not(s&0x88)and self.b[s]==11)>=2:mb+=30;eb+=30
  s=(mw*ph+ew*(24-ph))//24-(mb*ph+eb*(24-ph))//24
  return-s if self.t==8 else s
 def qsearch(self,a,b):
  global nodes;nodes+=1;ic=self.attacked(self.king_sq(self.t),8-self.t);ms=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):ms.append(m)
   self.unmake(m)
  if not ms:return(-100000)if ic else 0
  sp=self.eval()
  if sp>=b:return b
  if a<sp:a=sp
  for m in self.gen_moves():
   cp=self.b[(m>>7)&0x7F];pr=(m>>14)&7
   if not ic and not cp and not pr:continue
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    s=-self.qsearch(-b,-a);self.unmake(m)
    if s>=b:return b
    if s>a:a=s
   else:self.unmake(m)
  return a
 def negamax(self,d,a,b,p):
  global nodes
  if self.hm>=100 or nodes>NCAP:return 0
  ms=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):ms.append(m)
   self.unmake(m)
  if not ms:return(-100000+p)if self.attacked(self.king_sq(self.t),8-self.t)else 0
  if d==0:return self.qsearch(a,b)
  for m in ms:
   nodes+=1
   self.make(m);s=-self.negamax(d-1,-b,-a,p+1);self.unmake(m)
   if s>=b:return b
   if s>a:a=s
   if nodes>NCAP:break
  return a
 def search_root(self):
  global nodes;nodes=0;bm=None;lms=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):lms.append(m)
   self.unmake(m)
  if not lms:return None
  bm=lms[0]
  for d in R(1,100):
   a=-200000;b=200000;bs=-200000;cb=None
   for m in lms:
    nodes+=1;self.make(m);s=-self.negamax(d-1,-b,-a,1);self.unmake(m)
    if s>bs:bs=s;cb=m
    if s>a:a=s
    if nodes>NCAP:break
   if nodes>NCAP:break
   if cb is not None:bm=cb
  return bm
 def perft(self,d):
  if d==0:return 1
  c=0
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):c+=self.perft(d-1)
   self.unmake(m)
  return c
 def lm(self):
  res=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    f=m&0x7F;t=(m>>7)&0x7F;pr=(m>>14)&7;s=sqs(f)+sqs(t)+('nbrq'[pr-2]if pr else'');res.append(s)
   self.unmake(m)
  return res
 legal_moves=lm
if"MAKEFUN_ENV_URL"in os.environ:
 u=os.environ["MAKEFUN_ENV_URL"]
 def p(x,b):return json.load(urllib.request.urlopen(urllib.request.Request(u+x,data=json.dumps(b).encode(),headers={"content-type":"application/json"})))
 g=p("/game",{})
 while g["status"]!="done":m=Position(g["fen"]).lm();g=p("/move",{"game":g["game"],"move":m[0]if m else g["legal_moves"][0]})
