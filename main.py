import json,os,urllib.request
R=range
S=str
_s=1070372
NCAP=30000
nodes=0
def r64():
 global _s
 _s^=(_s<<13)&0xFFFFFFFFFFFFFFFF
 _s^=(_s>>7)&0xFFFFFFFFFFFFFFFF
 _s^=(_s<<17)&0xFFFFFFFFFFFFFFFF
 return _s&0xFFFFFFFFFFFFFFFF
ZP=[[r64()for _ in R(128)]for _ in R(15)]
ZC=[r64()for _ in R(16)]
ZE=[r64()for _ in R(128)]
ZS=r64()
PC={'.':0,'P':1,'N':2,'B':3,'R':4,'Q':5,'K':6,'p':9,'n':10,'b':11,'r':12,'q':13,'k':14}
def sqs(sq):return chr(97+(sq&7))+S((sq>>4)+1)
def ssq(s):return ord(s[0])-97+(int(s[1])-1)*16

class Position:
 def __init__(self,f="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
  p=f.split();self.b=[0]*128;r=7;c=0
  for x in p[0]:
   if x=='/':r-=1;c=0
   elif x.isdigit():c+=int(x)
   else:self.b[(r<<4)+c]=PC[x];c+=1
  self.t=0 if p[1]=='w'else 8
  self.c=0
  if len(p)>2 and p[2]!='-':
   for ch,mk in zip('KQkq',[1,2,4,8]):
    if ch in p[2]:self.c|=mk
  self.e=ssq(p[3])if len(p)>3 and p[3]!='-'else 0
  self.hm=int(p[4])if len(p)>4 else 0
  self.u=[]
  self.h=0
  for sq in R(128):
   if not(sq&0x88) and self.b[sq]:self.h^=ZP[self.b[sq]][sq]
  if self.t==8:self.h^=ZS
  if self.c:self.h^=ZC[self.c]
  if self.e:self.h^=ZE[self.e]

 def attacked(self,sq,col):
  if col==0:
   for ds in(-15,-17):
    ts=sq+ds
    if not(ts&0x88)and self.b[ts]==1:return True
  else:
   for ds in(15,17):
    ts=sq+ds
    if not(ts&0x88)and self.b[ts]==9:return True
  for ds in(-33,-31,-18,-14,14,18,31,33):
   ts=sq+ds
   if not(ts&0x88)and self.b[ts]==col+2:return True
  for ds in(-17,-16,-15,-1,1,15,16,17):
   ts=sq+ds
   if not(ts&0x88)and self.b[ts]==col+6:return True
  for ds,pt in(((-16,-1,1,16),(4,5)),((-17,-15,15,17),(3,5))):
   for d in ds:
    ts=sq+d
    while not(ts&0x88):
     p=self.b[ts]
     if p:
      if(p&8)==col and((p&7)in pt):return True
      break
     ts+=d
  return False

 def king_sq(self,col):
  k=col+6
  for sq in R(128):
   if not(sq&0x88)and self.b[sq]==k:return sq
  return 0

 def gen_moves(self):
  m=[];ot=8-self.t
  for sq in R(128):
   if sq&0x88:continue
   p=self.b[sq]
   if not p or(p&8)!=self.t:continue
   pt=p&7;rk=sq>>4
   if pt==1:
    d=16 if self.t==0 else -16;sr=1 if self.t==0 else 6;er=6 if self.t==0 else 1
    fr=sq+d
    if not(fr&0x88)and not self.b[fr]:
     if rk==er:
      for pr in(2,3,4,5):m.append(sq|(fr<<7)|(pr<<14))
     else:
      m.append(sq|(fr<<7))
      dr=sq+2*d
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
    for ds in(-33,-31,-18,-14,14,18,31,33):
     ts=sq+ds
     if not(ts&0x88):
      tg=self.b[ts]
      if not tg or(tg&8)==ot:m.append(sq|(ts<<7))
   elif pt in(3,4,5):
    ds=(-17,-15,15,17)if pt!=4 else ()
    os=(-16,-1,1,16)if pt!=3 else ()
    for d in ds+os:
     ts=sq+d
     while not(ts&0x88):
      tg=self.b[ts]
      if not tg:m.append(sq|(ts<<7))
      else:
       if(tg&8)==ot:m.append(sq|(ts<<7))
       break
      ts+=d
   elif pt==6:
    for ds in(-17,-16,-15,-1,1,15,16,17):
     ts=sq+ds
     if not(ts&0x88):
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
  fs=m&0x7F;ts=(m>>7)&0x7F;pr=(m>>14)&7
  p=self.b[fs];cp=self.b[ts];ep=self.e;cc=self.c;hm=self.hm;h=self.h
  self.u.append((cp,cc,ep,hm,h,m))
  if ep and(p&7)==1 and ts==ep:
   cp=9 if self.t==0 else 1
   capsq=ts-16 if self.t==0 else ts+16
   self.b[capsq]=0
   self.h^=ZP[cp][capsq]
  if cp and not(ep and(p&7)==1 and ts==ep):
   self.h^=ZP[cp][ts]
  self.h^=ZP[p][fs]
  if(p&7)==6 and abs(fs-ts)==2:
   if ts==6:
    self.b[5]=self.b[7];self.b[7]=0
    self.h^=ZP[4][7];self.h^=ZP[4][5]
   elif ts==2:
    self.b[3]=self.b[0];self.b[0]=0
    self.h^=ZP[4][0];self.h^=ZP[4][3]
   elif ts==118:
    self.b[117]=self.b[119];self.b[119]=0
    self.h^=ZP[12][119];self.h^=ZP[12][117]
   elif ts==114:
    self.b[115]=self.b[112];self.b[112]=0
    self.h^=ZP[12][112];self.h^=ZP[12][115]
  np=self.t|pr if pr else p
  self.b[fs]=0;self.b[ts]=np
  self.h^=ZP[np][ts]
  self.e=(fs+ts)//2 if((p&7)==1 and abs(fs-ts)==32)else 0
  if fs==4 or ts==4:self.c&=~3
  if fs==116 or ts==116:self.c&=~12
  if fs==0 or ts==0:self.c&=~2
  if fs==7 or ts==7:self.c&=~1
  if fs==112 or ts==112:self.c&=~8
  if fs==119 or ts==119:self.c&=~4
  self.t=8-self.t
  self.h^=ZS
  if cc!=self.c:
   if cc:self.h^=ZC[cc]
   if self.c:self.h^=ZC[self.c]
  if ep!=self.e:
   if ep:self.h^=ZE[ep]
   if self.e:self.h^=ZE[self.e]
  self.hm=0 if((p&7)==1 or cp)else self.hm+1

 def unmake(self,m):
  cp,cc,ep,hm,h,m=self.u.pop()
  fs=m&0x7F;ts=(m>>7)&0x7F;pr=(m>>14)&7
  self.t=8-self.t
  np=self.b[ts];self.b[ts]=0;self.b[fs]=self.t|1 if pr else np
  if ep and(np&7)==1 and ts==ep:
   capsq=ts-16 if self.t==0 else ts+16
   self.b[capsq]=cp
  else:
   self.b[ts]=cp
  if(np&7)==6 and abs(fs-ts)==2:
   if ts==6:self.b[7]=self.b[5];self.b[5]=0
   elif ts==2:self.b[0]=self.b[3];self.b[3]=0
   elif ts==118:self.b[119]=self.b[117];self.b[117]=0
   elif ts==114:self.b[112]=self.b[115];self.b[115]=0
  self.c=cc;self.e=ep;self.h=h;self.hm=hm

 def eval(self):
  mw=ew=mb=eb=0;ph=0;wp=[0]*8;bp=[0]*8;wb=bb=0
  for sq in R(128):
   if sq&0x88:continue
   p=self.b[sq]
   if not p:continue
   f=sq&7;r=sq>>4;c=0 if(p&8)==0 else 8;pt=p&7;mr=7-r if c else r
   if c==0:
    if pt==1:wp[f]+=1
    elif pt==3:wb+=1
   else:
    if pt==1:bp[f]+=1
    elif pt==3:bb+=1
   if pt in(2,3):ph+=1
   elif pt==4:ph+=2
   elif pt==5:ph+=4
  ph=min(24,ph)
  for sq in R(128):
   if sq&0x88:continue
   p=self.b[sq]
   if not p:continue
   f=sq&7;r=sq>>4;c=0 if(p&8)==0 else 8;pt=p&7;mr=7-r if c else r
   if pt==1:
    m,e=100+(mr-1)*6+(5 if f in(3,4) else 0),100+(mr-1)*10+(5 if f in(3,4) else 0)
   elif pt==2:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=320+cent*4,320+cent*3
   elif pt==3:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=330+cent*2,330+cent*2
   elif pt==4:
    m,e=500+(25 if mr==6 else 0)+(12 if wp[f]==0 and bp[f]==0 else 0),500+(25 if mr==6 else 0)+(12 if wp[f]==0 and bp[f]==0 else 0)
   elif pt==5:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=900+cent,900
   elif pt==6:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=cent*-8,cent*6
   else:
    m=e=0
   if c==0:mw+=m;ew+=e
   else:mb+=m;eb+=e
  if wb>=2:mw+=30;ew+=30
  if bb>=2:mb+=30;eb+=30
  sw=(mw*ph+ew*(24-ph))//24
  sb=(mb*ph+eb*(24-ph))//24
  s=sw-sb
  return -s if self.t==8 else s

 def qsearch(self,alpha,beta):
  global nodes
  nodes+=1
  in_chk=self.attacked(self.king_sq(self.t),8-self.t)
  moves=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    moves.append(m)
   self.unmake(m)
  if not moves:
   return(-100000)if in_chk else 0
  sp=self.eval()
  if sp>=beta:return beta
  if alpha<sp:alpha=sp
  for m in self.gen_moves():
   cp=self.b[(m>>7)&0x7F];pr=(m>>14)&7
   if not in_chk and not cp and not pr:continue
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    score=-self.qsearch(-beta,-alpha)
    self.unmake(m)
    if score>=beta:return beta
    if score>alpha:alpha=score
   else:self.unmake(m)
  return alpha

 def negamax(self,depth,alpha,beta,ply):
  global nodes
  if self.hm>=100:return 0
  moves=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    moves.append(m)
   self.unmake(m)
  if not moves:
   in_chk=self.attacked(self.king_sq(self.t),8-self.t)
   return(-100000+ply)if in_chk else 0
  if depth==0:return self.qsearch(alpha,beta)
  for m in moves:
   nodes+=1
   if nodes>NCAP:break
   self.make(m)
   score=-self.negamax(depth-1,-beta,-alpha,ply+1)
   self.unmake(m)
   if nodes>NCAP:break
   if score>=beta:return beta
   if score>alpha:alpha=score
  return alpha

 def search_root(self):
  global nodes
  nodes=0
  best_m=None
  legal_moves=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    legal_moves.append(m)
   self.unmake(m)
  if not legal_moves:return None
  best_m=legal_moves[0]
  for d in R(1,100):
   alpha=-200000;beta=200000;best_score=-200000;current_best=None
   for m in legal_moves:
    nodes+=1
    self.make(m)
    score=-self.negamax(d-1,-beta,-alpha,1)
    self.unmake(m)
    if nodes>NCAP:break
    if score>best_score:
     best_score=score;current_best=m
    if score>alpha:alpha=score
   if nodes>NCAP:break
   if current_best is not None:best_m=current_best
  return best_m

 def lm(self):
  res=[]
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    f=m&0x7F;t=(m>>7)&0x7F;pr=(m>>14)&7
    s=sqs(f)+sqs(t)+('nbrq'[pr-2]if pr else'')
    res.append(s)
   self.unmake(m)
  return res
 legal_moves=lm

 def perft(self,d):
  if d==0:return 1
  c=0
  for m in self.gen_moves():
   self.make(m)
   if not self.attacked(self.king_sq(8-self.t),self.t):
    c+=self.perft(d-1)
   self.unmake(m)
  return c

 def eval(self):
  mw=ew=mb=eb=0;ph=0;wp=[0]*8;bp=[0]*8;wb=bb=0
  for sq in R(128):
   if sq&0x88:continue
   p=self.b[sq]
   if not p:continue
   f=sq&7;r=sq>>4;c=0 if(p&8)==0 else 8;pt=p&7;mr=7-r if c else r
   if c==0:
    if pt==1:wp[f]+=1
    elif pt==3:wb+=1
   else:
    if pt==1:bp[f]+=1
    elif pt==3:bb+=1
   if pt in(2,3):ph+=1
   elif pt==4:ph+=2
   elif pt==5:ph+=4
  ph=min(24,ph)
  for sq in R(128):
   if sq&0x88:continue
   p=self.b[sq]
   if not p:continue
   f=sq&7;r=sq>>4;c=0 if(p&8)==0 else 8;pt=p&7;mr=7-r if c else r
   if pt==1:
    m,e=100+(mr-1)*6+(5 if f in(3,4) else 0),100+(mr-1)*10+(5 if f in(3,4) else 0)
   elif pt==2:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=320+cent*4,320+cent*3
   elif pt==3:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=330+cent*2,330+cent*2
   elif pt==4:
    m,e=500+(25 if mr==6 else 0)+(12 if wp[f]==0 and bp[f]==0 else 0),500+(25 if mr==6 else 0)+(12 if wp[f]==0 and bp[f]==0 else 0)
   elif pt==5:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=900+cent,900
   elif pt==6:
    cent=3.5-abs(f-3.5)+3.5-abs(mr-3.5)
    m,e=cent*-8,cent*6
   else:
    m=e=0
   if c==0:mw+=m;ew+=e
   else:mb+=m;eb+=e
  if wb>=2:mw+=30;ew+=30
  if bb>=2:mb+=30;eb+=30
  sw=(mw*ph+ew*(24-ph))//24
  sb=(mb*ph+eb*(24-ph))//24
  s=sw-sb
  return -s if self.t==8 else s

if"MAKEFUN_ENV_URL"in os.environ:
 u=os.environ["MAKEFUN_ENV_URL"]
 def p(x,b):
  with urllib.request.urlopen(urllib.request.Request(u+x,data=json.dumps(b).encode(),headers={"content-type":"application/json"}))as r:return json.load(r)
 g=p("/game",{})
 while g["status"]!="done":
  m=Position(g["fen"]).lm()
  g=p("/move",{"game":g["game"],"move":m[0]if m else g["legal_moves"][0]})
