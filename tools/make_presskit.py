# Regenerates presse/FAM-dossier-de-presse.pdf and presse/FAM-press-kit.pdf (needs playwright + Chrome).
import yaml, re, glob, io, os, html
from playwright.sync_api import sync_playwright
R='/home/claude/fam-live'
posts={}
for f in glob.glob(R+'/_posts/gallery/*.markdown'):
    s=io.open(f,encoding='utf-8').read(); fm=yaml.safe_load(s.split('\n---\n')[0].lstrip('-\n'))
    posts[fm.get('preview')]=fm
featured=yaml.safe_load(open(R+'/_data/featured.yml'))
expos=yaml.safe_load(open(R+'/_data/exhibitions.yml'))
pick=featured[:8]
T={
 'fr':dict(title='Dossier de presse',sub='Artiste peintre · Région parisienne',bio_h='Biographie',st_h='Démarche',works_h='Œuvres choisies',ex_h='Expositions récentes',contact_h='Contact',
   bio=["FAM est une artiste plasticienne française née en 1987. Elle vit et travaille près de Paris.","Titulaire d’un master en ingénierie informatique de l’université Panthéon-Sorbonne, où elle a mené deux années de doctorat, elle a choisi de se consacrer entièrement à la peinture.","Ses peintures narratives, centrées sur la représentation de la féminité, sont des constructions imaginaires, souvent provocantes, où des fragments de sa vie deviennent des pastiches surréalistes ou hyperréalistes."],
   st=["Fascinée par l’expression des regards et le mouvement des corps, FAM cherche à restituer l’émotion et la force qu’ils dégagent. Les personnages qu’elle peint sont ses représentants dans notre monde.","Elle explore les états psychologiques, la beauté, l’identité, le corps, le genre, les biais cognitifs et les questions sociales. Son but est de questionner plutôt que de juger."],
   med='medium_fr',dim='dimensions_fr'),
 'en':dict(title='Press kit',sub='Painter · Paris region',bio_h='Biography',st_h='Statement',works_h='Selected works',ex_h='Recent exhibitions',contact_h='Contact',
   bio=["FAM is a French visual artist, born in 1987, who lives and works near Paris.","She holds a master’s degree in computer engineering from Panthéon-Sorbonne University, where she spent two years on a doctorate, before devoting herself entirely to painting.","Her narrative paintings, centred on how femininity is portrayed, are imaginary and often provocative constructions in which parts of her own life become surreal or hyperrealist pastiches."],
   st=["Fascinated by the expression of a gaze and the movement of bodies, FAM tries to convey the emotion and strength they give off. The figures she paints are her representatives in our world.","She explores psychological states, beauty, identity, the body, gender, cognitive biases and social issues. Her aim is to question rather than to judge."],
   med='medium',dim='dimensions'),
}
fonts=f'''@font-face{{font-family:B;src:url(file://{R}/fonts/fam/bodoni-moda-latin-opsz-normal.woff2)}}@font-face{{font-family:B;font-style:italic;src:url(file://{R}/fonts/fam/bodoni-moda-latin-opsz-italic.woff2)}}@font-face{{font-family:S;src:url(file://{R}/fonts/fam/instrument-sans-latin-400-normal.woff2)}}@font-face{{font-family:S;font-weight:600;src:url(file://{R}/fonts/fam/instrument-sans-latin-600-normal.woff2)}}'''
css=fonts+'''@page{size:A4;margin:0}body{margin:0;font:10.5pt/1.55 S,sans-serif;color:#1f1e1c}
.pg{width:210mm;height:297mm;padding:18mm 18mm 16mm;box-sizing:border-box;page-break-after:always;position:relative;overflow:hidden}
.mark{font:500 22pt B,serif;letter-spacing:.32em}.cover{display:flex;flex-direction:column}.cover img{flex:1;min-height:0;object-fit:contain;margin:14mm 0 10mm}
.cover h1{font:400 30pt/1.1 B,serif;margin:0}.cover p{color:#6f6a63;margin:.4em 0 0}
h2{font:400 17pt/1.2 B,serif;margin:0 0 6mm}.lede{font:400 13pt/1.45 B,serif}.cols{display:grid;grid-template-columns:1fr 1fr;gap:12mm}
p{margin:0 0 3.5mm}.grid{display:grid;grid-template-columns:1fr 1fr;gap:8mm 10mm}.w img{width:100%;height:92mm;object-fit:contain;background:#f6f4f1}
.cap{font-size:8.5pt;color:#6f6a63;margin-top:2mm}.cap i{font:italic 10.5pt B,serif;color:#1f1e1c}
.ex{display:grid;grid-template-columns:14mm 1fr;gap:4mm;margin-bottom:3.5mm}.ex b{font:400 11pt B,serif}.ex i{font:italic 10.5pt B,serif}.ex span{color:#6f6a63;font-size:9pt;display:block}
.foot{position:absolute;bottom:12mm;left:18mm;right:18mm;font-size:8pt;color:#6f6a63;display:flex;justify-content:space-between;border-top:1px solid #e7e3dd;padding-top:3mm}'''
def img(src): return 'file://'+R+'/img/web/1600/'+re.sub(r'\.(jpe?g|png)$','.jpg',src[len('/img/'):],flags=re.I)
for L,t in T.items():
    E=lambda x: html.escape(str(x))
    foot=f'<div class="foot"><span>FAM · {t["title"]}</span><span>famvisualarts.github.io · famartwork@gmail.com</span></div>'
    out=[f'<div class="pg cover"><div class="mark">FAM</div><img src="{img(featured[2])}"><h1>{t["title"]}</h1><p>{t["sub"]}</p><p>famvisualarts.github.io</p></div>']
    out.append(f'<div class="pg"><div class="cols"><div><h2>{t["bio_h"]}</h2>'+''.join(f'<p{" class=lede" if i==0 else ""}>{E(x)}</p>' for i,x in enumerate(t['bio']))+f'</div><div><h2>{t["st_h"]}</h2>'+''.join(f'<p>{E(x)}</p>' for x in t['st'])+f'</div></div><div style="margin-top:10mm"><img src="file://{R}/img/web/1600/artist/artist1.jpg" style="width:100%;height:105mm;object-fit:cover"></div>{foot}</div>')
    for chunk in (pick[:4],pick[4:8]):
        cells=''
        for src in chunk:
            w=posts[src]; cells+=f'<div class="w"><img src="{img(src)}"><div class="cap"><i>{E(w["title"])}</i>, {w.get("year","")}<br>{E(w.get(t["med"]) or w.get("medium",""))}, {E(w.get(t["dim"]) or w.get("dimensions",""))}</div></div>'
        out.append(f'<div class="pg"><h2>{t["works_h"]}</h2><div class="grid">{cells}</div>{foot}</div>')
    exs=''.join(f'<div class="ex"><b>{e["year"]}</b><div><i>{E(e["title"][L])}</i><span>{E(e["venue"][L])}</span></div></div>' for e in expos)
    out.append(f'<div class="pg"><div class="cols"><div><h2>{t["ex_h"]}</h2>{exs}</div><div><h2>{t["contact_h"]}</h2><p class="lede">famartwork@gmail.com<br>+33 7 82 73 62 86</p><p>famvisualarts.github.io<br>Instagram : @famvisualarts</p></div></div>{foot}</div>')
    doc=f'<!doctype html><html lang="{L}"><meta charset="utf-8"><style>{css}</style>'+''.join(out)
    io.open(f'/home/claude/presskit/{L}.html','w',encoding='utf-8').write(doc)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files'])
    for L,name in (('fr','FAM-dossier-de-presse.pdf'),('en','FAM-press-kit.pdf')):
        pg=b.new_page(); pg.goto(f'file:///home/claude/presskit/{L}.html'); pg.wait_for_timeout(1500)
        os.makedirs(R+'/presse',exist_ok=True); pg.pdf(path=R+'/presse/'+name, format='A4', print_background=True)
        print(name, os.path.getsize(R+'/presse/'+name)//1024,'KB')
    b.close()
