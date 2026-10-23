#!/usr/bin/env python3
"""Genera el arte centrado de la demo web de Totonia (TV centrada, sin logo de fondo).

Entrada: los assets ORIGINALES aprobados (master 1672x941 con la TV en x=665).
Salida (en assets/): desktop-master.png, desktop-overlay-screen-hole.png, screen-poster.png
centrados (vidrio en x=457). Los personajes conservan sus pixeles y posicion.
Las mascaras de TV y personajes van embebidas (se obtuvieron con GrabCut y retoques a mano
en el mockup aprobado) para que el resultado sea reproducible sin GrabCut.

Uso: python3 scripts/build-centered-art.py [--src DIR_ASSETS_ORIGINALES] [--out DIR]
Requiere: numpy, pillow, opencv-python-headless.
"""
import argparse, base64, os, sys, zlib
import cv2, numpy as np
from PIL import Image, ImageFilter
ap=argparse.ArgumentParser(); here=os.path.dirname(os.path.abspath(__file__))
ap.add_argument('--src',default=os.path.join(here,'..','assets'))
ap.add_argument('--out',default=os.path.join(here,'..','assets'))
args=ap.parse_args()
R=args.src.rstrip('/')+'/'
MASK_CHAR="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"
MASK_TV="eNrt3b9u1FgYxmF7LeEtEG5ToPVtgITwrXAJW1Ks1kYpUs4l5FJiaQvKXAJGFCkx2gIjvD7rIckwQ2Ymwfj8mXd+rwQFKOAn9vnOd46dcRQRQgghhBA/SXshTFFFURYeKG+mfmVZj79MeN/nbupXmnb8FR6oHCaDuigNETT5kEZMFiSomgyq8iBBdVSYaaC6CBLUJMY0k0BNafoAQe04tNtJoNYECerGod1NAn0KD5T3IyifAsrG0/MlPFAx5KYvpoDyrgwQNJaDczOepJ8HxWYoAgSN5WA8JjMJdJ0uLFB2c1g/X7bTmy9ssyEkUDkZdPutaPOgptZbz9gtbL2s7gd9mjYpW0q8AlXbS8b9oH+nTcr2itxN7vzNcmTke/rW1egzJqBBlO48pnRJLLZfiT+CAhpEq6Pq7/5Nc92I339yzeT1h4XGx+yaTbJxZMRmDyheA4VTFYrbQ2rvgoblSagfUCBDqgrlHpBZjrCHgbrwQHeGwQiqsr2g718bUD93fVAXW4bBEpPvBRV763ZWeRxDF1uuuRHUFPtAudkLymu/ReHOMBhBbbkPVOwHFX4KRbpzGCxX5ftA69PQNlDpB5TtPKb0eplU3/+t2AHyU/nyne1Lcg2qHtL5bKlysafKV+xsX25AD6sJz7Yt0P0uh+5cXMnmecs2TmRcbdaEk1BAu/ux/KvZmT6K6/VpdVunkPhpwX8EFeah6cof/uAuyMfMmppfzK7W6eX+vtZyxZ4lm4dfpu5b8JlBm0PQLA4e9Gl9LCXm0v2aYmaQ2QR9lAHVq0lMBPRtNGmBVlNV4rYu2AcVbtsf6yDXO5BOQC43UFyBnNUHlyAnu6uuQdZJgAABAgTooEC5GqgQAyVGDJSqgbJ3gMIG5WqX3EtAgYMKQGGDajFQ3IiBklYMlPZqoEEMlBk5kAEECBAgQAcDMkYLlKmBCjVQqQYyYqBYDZSogVJvoKdSVdveacrVQIUayAACtDutGqgDFHiV69XmISvP1Y7/7KAG0jpD4wLvqxQoUztDueAlZygKAYNiQIGDEjVQCgiQ227ba6PQqTUKNs6Q1wWejXPkGdQDCro3NRY+CsOzZ/6PwvANatRAnRpo7qoQ+wYNgAIHGTlQpQaq1UANoHtA52Ktgsk9g+a+z/rKN2j23qcABMgtqFQDsSACtDcf1UBvxTYVmkgONP9N4yulTm4Jeit2Q8Wo3fL6Ww30wivIwkdrniRiIL1HL/zORBUgQIcP8rpmrS2AvO4qNICOEJQPpRYoUwOlaqCkz7VAcZdqgaLW2wriwg7olbcVxMLWz4T7GkRntl5M5GtuPbX16ihfdbuyBTKA5skbW2+I8QU6VQMtbFU5qd16v6BODdSrgQY1kJEDVWqgWg3UAAoc1EqBLmzNrIBC730AAQIEKAzQUIh1CkOu1pyK7foYtY1Go7eN1aiBLO3LlWqgQg2Uq4H8fRhODwgQIECADgd0DgiQ2yzUQGdqoFM10Bu1bruSAxW2nl4qfYEaMVBWi4HSSgyURGKgCBAgQIAAAQI0WyIx0AAocFCvBurUQK0aqAEECBBFwc28CggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAjQdR6rgfz8UCEgQIAAAQIECBCgOZKqgRJAgAD9UmJAgABRFKQ7BZpTQIAAAQIECBAgQIAAAQIUJqhQA5VqICMGigEBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAAdFYj3KQUPKtRAPKcACBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAOAHSbWg10pQYygEIH1WqgBhAgt2kBBQ7q1EA9ZwgQZZvWZy1naqCk0gLZWIlnWrMQoNBnIc+gRg1Uq4FsbDTmYlXb02eS2CtygLjkXIO8FYUuyiIx0KNI6pLrot+sgEpAs4ESQA+JUbvkjFqVkwN5HEMRIEAKoEILlA25GMionSGtTUavoB7QUYIuxcZQbMRAiRooVQNlgAABOti7XYAYQ1xygAAd1A1WQEfZbcuB5BZ4PgeRHVCuBmLnFBBjiCoXxk19toKPtFMAxCYJS3BA7CkAAqTwbJktkBEDxYAAuQQ9eaoGKlMp0FiyF1Ign5MqoKMElYAAAQIUytIBECBAgAABAgQI0K+CLgABYgwBAsSeAiDKNvMQIECAWA8BAsQYAgQIECBA2ivW5Y+m/CcFemTq52pniDEECBDzECBWrL5AX7jkAAFiYl1PoQaKK7EfWVMEJZyhoFeskdgZigTfxZoDChzkdW7t1UCDmAdQ6DXBxhjyuxfcAQIECBCgw1kNjWnmBqWeQa3aPtagBjJyoFoN1KiBWjVQBwgQIKqc9DxU0csdWbfN8oHlw5EVBZYPtD6Hfv/BO2gABMj1PtaJGKh6oQZ6qQYq1UBXlRbozVWtBTq9FAOdzduf+gct5l21el+xZpkYKEq1LrkhSoxWUagiozUP1Xqgz2KgWGwMzb2tEAJIq1PokoXYJZecy42hWe9BAAIESAHUAQIECJA0SK5sN2qgGhAgxhBl29K+DyBARwka1EAGECBAgAABAgQIECBAgAABAgQIECBAgAAB+on8/u33124/CbDLbv/vcnbQdf5w+1GAzYvNS2R+UOb2nRbR69v/OLcESiu3oNXDMKklULJwO4ZWN/ITW6Bzp6DePujCKWhYgWJbIMcTjzLoHSAuOeegKy3QlbmcneMB9GoF+mDy2Ruf2jkobleg98PsoKxxDkq6Faj9a35Q6xyUroGeZbODOuegbA10ks4O6p2D8jVQZAF06hp0vg56MjvI/OMY9N6sgx7PD/rgGPRhAxQJgUaSBVDuAfT9wdk/5wcV5rNj0GcbL4fyu38K6JhBfj4BubUH8vOKm8YeqPQCMoAAyYD83Je0WLdzL6DeHsjPm9Y6JtbjBcldcnJVTm4e8uOZ/R0W0eY9J/epAQECBMgJSK5ss8Bjged6gScHotum23ZctgEBAgQIEN0294fo5bg/xP2hYG6nyD144WcfqwYESAbkp5mrAAHSAXlpty16eCoYECA6BUIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEI/5H+qs8aM="
def unpack(b): return np.unpackbits(np.frombuffer(zlib.decompress(base64.b64decode(b)),np.uint8))[:941*1672].reshape(941,1672).astype(bool)
orig_img=Image.open(R+'desktop-master.png').convert('RGB')
if orig_img.size!=(1672,941): sys.exit('desktop-master.png debe ser el master original de 1672x941')
orig=np.array(orig_img).astype(np.int16)
H,W,_=orig.shape
YS=792; DXC=0; DXT=-208
CHAR_FULL=unpack(MASK_CHAR)
char=CHAR_FULL.copy()
char[YS:,:]=False
def is_sky(a): return (a[...,2]>200)&(a[...,0]<140)&(a[...,1]>60)&(a[...,1]<215)
sky=is_sky(orig)
# per-row sky color (median of sky pixels in row)
skyrow=np.zeros((H,3),np.int16); last=np.array([0,105,243])
for y in range(H):
    px=orig[y][sky[y]&(orig[y][:,2]>235)&(orig[y][:,0]<40)]
    if len(px)>30: last=np.median(px,axis=0).astype(np.int16)
    skyrow[y]=last
# smooth row colors
for c in range(3): skyrow[:,c]=np.convolve(np.pad(skyrow[:,c],5,mode='edge'),np.ones(11)/11,'valid').astype(np.int16)

# ---- 1. remove logo ----
src=orig.copy()
logo=np.zeros((H,W),bool)
y0,y1,x0,x1=180,357,84,584
logo[y0:y1,x0:x1]=~sky[y0:y1,x0:x1]
# whites (clouds) inside logo bbox are logo highlights? keep clouds only where outside logo core -> treat light pixels next to blue as cloud
green=(orig[...,1]>orig[...,0]+20)&(orig[...,1]>orig[...,2])
dark=orig.sum(-1)<120
for (a,b) in [(205,290),(390,455),(530,585)]:
    reg=np.zeros((H,W),bool); reg[357:372,a:b]=True
    logo|=reg&(green|dark)&~sky
# exclude existing clouds above logo bbox not attached: compute components of logo mask touching core
n,lab=cv2.connectedComponents(logo.astype(np.uint8))
core=lab[260,300]; keepl=set(np.unique(lab[230:330,120:560]))-{0}
logo=np.isin(lab,list(keepl))
logo=cv2.dilate(logo.astype(np.uint8),np.ones((3,3),np.uint8))>0
logo[:, :84]=False; logo[:, 590:]=False
ys,xs=np.nonzero(logo)
src[ys,xs]=skyrow[ys]
# add a cloud: copy cloud patch from orig sky (x 145..255, y 150..195) into logo area
def paste_cloud(dst,sx0,sy0,sx1,sy1,dx,dy):
    p=orig[sy0:sy1,sx0:sx1]
    m=(p.sum(-1)>560)  # whites
    m=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8))>0
    m&=~is_sky(p)|(p.sum(-1)>560)
    reg=dst[dy:dy+(sy1-sy0),dx:dx+(sx1-sx0)]
    reg[m]=p[m]
paste_cloud(src,140,145,262,197,150,265)
paste_cloud(src,140,145,262,197,400,215)

# ---- 2. TV mask (orig coords) ----
poly=np.array([(580,48),(1000,44),(1490,60),(1490,100),(1530,100),(1530,455),(1548,455),(1548,700),(1466,700),(1466,YS),(580,YS)],np.int32)
pm=np.zeros((H,W),np.uint8); cv2.fillPoly(pm,[poly],1)
tv=unpack(MASK_TV)  # mascara final de la TV (orig coords)

# TV pixels with characters substituted
tvimg=src.copy()
# bottom-left quadrant: rebuild as mirror of bottom-right for a consistent bezel corner
RY0,RX0,RX1=600,530,800
tv[600:,:530]=False
for y in range(RY0,YS):
    for x in range(RX0,RX1):
        mx=2088-x
        tv[y,x]=tv[y,mx]
        if tv[y,mx]: tvimg[y,x]=src[y,mx]
charD=cv2.dilate(char.astype(np.uint8),np.ones((5,5),np.uint8))>0
charD[YS:]=False
cy,cx=np.nonzero(charD&tv)
mx=2088-cx
inR=(cy>=600)&(cx>=530)&(cx<800)
ok=~charD[cy,mx]&tv[cy,mx]&~inR
ok2=inR&~charD[cy,mx]
tvimg[cy[ok],cx[ok]]=src[cy[ok],mx[ok]]
# fallback: tile patch from row neighbours (search horizontally nearest clean pixel within tv)
bad=~ok&~ok2
bad_y,bad_x=cy[bad],cx[bad]
clean=tv&~charD
clean[600:,530:800]=False
clean[600:,1288:1558]&=~charD[600:,530:800][:,::-1]
for y,x in zip(bad_y,bad_x):
    for d in range(1,400):
        for xx in (x+d,x-d):
            if 0<=xx<W and clean[y,xx]:
                tvimg[y,x]=src[y,xx]; break
        else: continue
        break

def shift(a,dx,fill_edge=True):
    out=np.zeros_like(a)
    if dx<0:
        out[:, :W+dx]=a[:, -dx:]
        if fill_edge: out[:, W+dx:]=a[:, W+dx:] if a.ndim==2 else a[:, W+dx:]
    else:
        out[:, dx:]=a[:, :W-dx]
    return out

# ---- 3. background ----
bg=src.copy()
oldtv=cv2.dilate(tv.astype(np.uint8),np.ones((5,5),np.uint8))>0
oldtv[600:]=False; oldtv[:,1550:]=False
ys,xs=np.nonzero(oldtv); bg[ys,xs]=skyrow[ys]
# right side rebuild (x 1300..1672, rows < 698)
XA=1300
rows=np.arange(H)
oldd=cv2.dilate(tv.astype(np.uint8),np.ones((9,9),np.uint8))>0
# L0 sky: orig where not old TV, else flat
bg[:698,XA:]=src[:698,XA:]
m=oldd[:290,XA:]; ys,xs=np.nonzero(m); bg[ys,xs+XA]=skyrow[ys]
bg[:698,XA:1550]=skyrow[:698,None,:]
# L1 stadium: extend the stand following its perspective slope; no extra towers/flags
P0=1564
top=lambda x: 330-0.232*(x-1530)
bg[205:462,XA:P0]=skyrow[205:462,None,:]
for x in range(XA,P0):
    sx=P0+((x-P0)%98)
    dy=int(round(top(x)-top(sx)))
    y0=int(top(sx))-8
    for y in range(y0,462):
        p=src[y,sx]; ty=y+dy
        if ty<462 and not is_sky(p[None,None])[0,0] and p.sum()<500: bg[ty,x]=p
# old-TV leaf stubs over stand right of P0: same rule
for x in range(P0,1600):
    m=oldd[205:462,x]
    if m.any():
        sx=P0+((x-P0)%98) if x>=P0+98 else x
        pass
# bushes in front (unshifted tile, green pixels only)
for x in range(XA,1600):
    sx=P0+((x-P0)%98)
    col=src[372:462,sx]
    gr=(col[:,1]>col[:,0]+15)&(col[:,1]>col[:,2]+15)|((col.sum(-1)<170)&(np.arange(90)>12))
    if x>=P0: gr&=oldd[372:462,x]
    bg[372:462,x][gr]=col[gr]
    if x<P0:
        for y in range(415,495 if x<1545 else 462):
            q=bg[y,x]
            if is_sky(q[None,None])[0,0] or q.sum()>500: bg[y,x]=src[y if y<462 else y-45,sx]
# L3 mirrored wall/fence/pots rows>=495 for x<1545
for x in range(XA,1545):
    sx=528-(x-1342)
    col=src[495:698,sx]; ns=~is_sky(col[None])[0]
    bg[495:698,x][ns]=col[ns]
# L4 lamp
LM=np.zeros((H,W),np.uint8)
for x in range(1462,1540):
    sx=528-(x-1342)
    for y in range(360,540):
        if (y<432 and 335<=sx<=402) or (y>=432 and 361<=sx<=378):
            p=src[y,sx]
            if not is_sky(p[None,None])[0,0] and not (p.sum()>420 and p[2]>=p[0]-5): bg[y,x]=p; LM[y,x]=1
LC=cv2.morphologyEx(LM,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
ys,xs=np.nonzero((LC>0)&(LM==0))
bg[ys,xs]=src[ys,528-(xs-1342)]
paste_cloud(bg,1555,138,1665,197,1555,138)
paste_cloud(bg,140,145,262,197,1370,150)
bg[:130,1150:1300]=skyrow[:130,None,:]
paste_cloud(bg,1555,50,1672,105,1290,30)
d=(bg[:205,1300:1600].sum(-1)<250)
ys,xs=np.nonzero(d); bg[ys,xs+1300]=skyrow[ys]
for y in range(455,700):
    for x in range(1549,1530,-1):
        if is_sky(bg[y:y+1,x:x+1])[0,0] or np.abs(bg[y,x]-skyrow[y]).sum()<30: bg[y,x]=bg[y,x+1]
# stairs under old base
for x in range(1236,1475):
    bg[698:YS,x]=src[698:YS,1475+((x-1475)%112)]
# ---- 4. paste TV ----
out=bg.copy()
ys,xs=np.nonzero(tv); nx=xs+DXT; v=(nx>=0)&(nx<W)
out[ys[v],nx[v]]=tvimg[ys[v],xs[v]]
# ---- 5. characters ----
ys,xs=np.nonzero(char); out[ys,xs]=orig[ys,xs]
new=out.clip(0,255).astype(np.uint8)

# ---- overlay y poster ----
ov=np.array(Image.open(R+'desktop-overlay-screen-hole.png').convert('RGBA'))
char=CHAR_FULL
H,W=new.shape[:2]
pa=np.array(Image.open(R+'screen-poster.png').convert('RGB'))
pm=char[162:162+527,665:665+758]
pm=np.array(Image.fromarray(pm.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(7)))>0
pa[pm]=pa[:,::-1][pm]
poster=Image.fromarray(pa)
hole=ov[...,3]<128
sx,sy,sw,sh=665,162,758,527
glass=hole.copy()
box=np.zeros_like(hole); box[sy:sy+sh,sx:sx+sw]=True
glass|=char&box
# fill concavities under Toto: rows in box, between hole columns
for y in range(sy,sy+sh):
    xs=np.nonzero(hole[y])[0]
    if len(xs): glass[y,xs.min():xs.max()+1]=True
DX=-208
g2=np.zeros_like(glass); g2[:, :W+DX]=glass[:, -DX:]
g2&=~char
ovn=np.dstack([new,np.where(g2,0,255).astype(np.uint8)])
O=args.out.rstrip('/')+'/'
os.makedirs(O,exist_ok=True)
Image.fromarray(new).save(O+'desktop-master.png')
Image.fromarray(ovn,'RGBA').save(O+'desktop-overlay-screen-hole.png')
poster.save(O+'screen-poster.png')
print('OK: screen x=457 y=162 w=758 h=527 -> --screen-left: 27.3325358852%')
