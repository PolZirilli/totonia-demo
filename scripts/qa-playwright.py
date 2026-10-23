import json, subprocess, time, sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server','8765'],cwd='.',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
res=[]
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/home/bondi/.cache/ms-playwright/chromium_headless_shell-1194/chrome-linux/headless_shell',args=['--autoplay-policy=document-user-activation-required'])
    for w,h in [(1440,900),(1920,900),(1024,768),(768,1024)]:
      pg=b.new_page(viewport={'width':w,'height':h}); errs=[]
      pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
      pg.on('pageerror',lambda e:errs.append(str(e)))
      pg.on('requestfailed',lambda r:errs.append('reqfail '+r.url))
      pg.on('response',lambda r:errs.append(f'{r.status} {r.url}') if r.status>=400 else None)
      pg.goto('http://localhost:8765/'); pg.wait_for_timeout(3000)
      before=pg.evaluate('window.GENESIS_AUDIO_CONTEXT&&window.GENESIS_AUDIO_CONTEXT.state')
      hint=pg.evaluate('!document.querySelector(".audio-hint").hidden')
      pg.screenshot(path=f'docs/qa/centered-{w}x{h}-before-click.png')
      pg.mouse.click(w//2,h//2); pg.keyboard.press('Enter'); pg.wait_for_timeout(1000)
      after=pg.evaluate('window.GENESIS_AUDIO_CONTEXT&&window.GENESIS_AUDIO_CONTEXT.state')
      geo=pg.evaluate('''()=>{const r=e=>{const b=document.querySelector(e).getBoundingClientRect();return [b.x,b.y,b.width,b.height].map(v=>+v.toFixed(1))};
        const c=document.querySelector("#game canvas");const cb=c&&c.getBoundingClientRect();
        const z=e=>+getComputedStyle(document.querySelector(e)).zIndex||0;
        return {slot:r(".screen-slot"),canvas:cb&&[cb.x,cb.y,cb.width,cb.height].map(v=>+v.toFixed(1)),overlay:r(".art-overlay"),artboard:r(".desktop-artboard"),order:[...document.querySelector(".desktop-artboard").children].map(e=>e.className)}}''')
      pg.screenshot(path=f'docs/qa/centered-{w}x{h}.png')
      res.append(dict(vp=f'{w}x{h}',audio_before=before,hint_shown=hint,audio_after=after,errors=errs,**geo)); pg.close()
    b.close()
finally: srv.terminate()
print(json.dumps(res,indent=1))
