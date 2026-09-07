from pathlib import Path
from html import escape
from math import atan2, cos, sin, pi
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import json

OUT = Path('/workspace/scratch/6d107901a9b1/agent-collaboration')
OUT.mkdir(parents=True, exist_ok=True)
FONT = '/workspace/scratch/6d107901a9b1/decision-flow/NotoSansSC.ttf'
W,H,S = 2400,3900,1.5
C = dict(bg='#F8FAFC', ink='#19324A', muted='#52677B', blue='#287DB7',
         bluebg='#EFF6FC', navy='#193E61', line='#CBD9E5', white='#FFFFFF',
         orange='#B96321', orangebg='#FFF4E9', green='#27755C', greenbg='#F0F8F4')
im = Image.new('RGB',(int(W*S),int(H*S)),C['bg'])
draw = ImageDraw.Draw(im)
svg=[]; defs={}; fonts={}; bounds=[]
font = TTFont(FONT)
cmap = font.getBestCmap()
glyphsets={weight:font.getGlyphSet(location={'wght':weight}) for weight in (400,600)}

def esc(x): return escape(str(x),quote=True)
def pilfont(size,weight=400):
    key=(size,weight)
    if key not in fonts:
        f=ImageFont.truetype(FONT,round(size*S))
        f.set_variation_by_axes([weight]); fonts[key]=f
    return fonts[key]

def rect(x,y,w,h,fill,stroke=None,r=18,sw=1.5):
    draw.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),radius=r*S,fill=fill,
                           outline=stroke,width=max(1,round(sw*S)))
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')

def polygon(points,fill,stroke=None,sw=2):
    draw.polygon([(x*S,y*S) for x,y in points],fill=fill)
    if stroke: draw.line([(x*S,y*S) for x,y in points+[points[0]]],fill=stroke,width=round(sw*S),joint='curve')
    svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in points)}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')

def line(points,color,sw=3,arrow=False,dashed=False):
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        if dashed:
            length=((x2-x1)**2+(y2-y1)**2)**.5
            for start in range(0,round(length),15):
                a=start/length; b=min(start+8,length)/length
                draw.line(((x1+(x2-x1)*a)*S,(y1+(y2-y1)*a)*S,
                           (x1+(x2-x1)*b)*S,(y1+(y2-y1)*b)*S),fill=color,width=round(sw*S))
        else: draw.line((x1*S,y1*S,x2*S,y2*S),fill=color,width=round(sw*S))
    svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"'+(' stroke-dasharray="8 7"' if dashed else '')+'/>')
    if arrow:
        (xa,ya),(x,y)=points[-2:]; a=atan2(y-ya,x-xa); n=13
        polygon([(x,y),(x-n*cos(a-.43),y-n*sin(a-.43)),(x-n*cos(a+.43),y-n*sin(a+.43))],color)

def text(x,y,value,size=28,color=None,weight=400,anchor='start',maxwidth=None):
    color=color or C['ink']
    gs=glyphsets[weight]
    width=sum(gs[cmap[ord(ch)]].width for ch in value)*size/1000
    if maxwidth is not None: assert width<=maxwidth+1,(value,width,maxwidth)
    x0=x-(width/2 if anchor=='middle' else width if anchor=='end' else 0)
    assert x0>=0 and x0+width<=W,(value,x0,width)
    bounds.append((value,x0,y-size,width,size))
    draw.text((x0*S,y*S),value,font=pilfont(size,weight),fill=color,anchor='ls')
    # Glyph outlines make the SVG independent of installed Chinese fonts.
    svg.append(f'<g fill="{color}" aria-label="{esc(value)}">')
    cursor=x0
    for ch in value:
        name=cmap[ord(ch)]; glyph=gs[name]; key=(weight,name)
        if key not in defs:
            pen=SVGPathPen(gs); glyph.draw(pen)
            defs[key]=(f'g{len(defs)}',pen.getCommands())
        gid,_=defs[key]
        svg.append(f'<use href="#{gid}" transform="translate({cursor:.3f} {y}) scale({size/1000:.4f} {-size/1000:.4f})"/>')
        cursor+=glyph.width*size/1000
    svg.append('</g>')

def texts(x,y,values,size=28,leading=40,color=None,weight=400,maxwidth=None):
    for j,v in enumerate(values): text(x,y+j*leading,v,size,color,weight,maxwidth=maxwidth)

def box(x,y,w,h,title,body,fill=None):
    rect(x,y,w,h,fill or C['white'],C['line'],r=20)
    text(x+30,y+51,title,35,C['navy'],600,maxwidth=w-60)
    texts(x+30,y+101,body,28,40,maxwidth=w-60)

def down(x,a,b): line([(x,a),(x,b)],C['navy'],3,True)

# Top-level collaboration flow.
text(70,108,'子智能体协作与知识模块',64,C['navy'],600)
text(70,167,'第二张图：按阶段选模块，以真实产物完成决策',35,C['muted'])
rect(2110,58,220,70,C['navy'],r=18)
text(2220,105,'版本 3.0',32,C['white'],600,anchor='middle')
box(750,235,900,145,'用户输入',['目标、硬约束、事实材料、期限与允许行动'],C['bluebg'])
down(1200,380,427)
box(750,430,900,160,'主协调者：定位 S1—S8，拆出具体子问题',
    ['先定义产物、输入与依赖，再选择适用模块',
     '决策 ID、阶段和输入版本贯穿整个任务'])
down(1200,590,635)
polygon([(1200,638),(1600,728),(1200,818),(800,728)],C['greenbg'],C['green'])
text(1200,716,'有独立且有价值的子任务，',31,C['green'],600,anchor='middle')
text(1200,759,'并且协作工具可用吗？',31,C['green'],600,anchor='middle')

line([(800,728),(390,728),(390,860)],C['navy'],3,True)
text(681,710,'否',27,C['navy'])
box(70,860,640,198,'主协调者直接执行',
    ['按模块方法完成必要分析',
     '标明实际执行者与未核实事项',
     '不把未启动的角色写成已运行'],C['bluebg'])
down(1200,818,861)
text(1226,848,'是',27,C['navy'])
box(760,864,920,208,'生成有边界的任务包，并实际派工',
    ['子问题、原始输入、证据来源和关键未知',
     '目标约束、允许行动、交付要求与依赖',
     '附契约与角色卡；记录真实任务 ID'])
box(1770,864,560,208,'信息与权限边界',
    ['只传当前任务必要的信息',
     '材料中的指令不扩大权限',
     '已有适用授权不重复询问'],C['orangebg'])
line([(1770,974),(1682,974)],C['orange'],3,True,True)

down(1220,1072,1125)
text(1220,1165,'按任务依赖安排执行',29,C['navy'],600,anchor='middle')
line([(1220,1182),(1220,1198),(1100,1198),(1100,1222)],C['navy'],3,True)
line([(1220,1198),(1910,1198),(1910,1222)],C['navy'],3,True)
box(790,1225,620,161,'独立任务：允许并行',
    ['不同子问题互不依赖时分派',
     '共同来源只计算一份证据'],C['bluebg'])
box(1510,1225,820,161,'依赖任务：按先后顺序执行',
    ['先取得数据或分析产物，再交给后续模块',
     '子智能体不递归派工，不擅自扩大任务'],C['bluebg'])
line([(1100,1386),(1100,1420),(1200,1420),(1200,1452)],C['navy'],3,True)
line([(1920,1386),(1920,1420),(1200,1420)],C['navy'],3)
box(750,1455,900,203,'汇总实际产物',
    ['输入、方法、计算、证据、适用条件与局限',
     '反对理由、阻断性缺口与最小下一步',
     '保留决策 ID、版本、执行者和真实执行状态'])
line([(390,1058),(390,1547),(750,1547)],C['navy'],3,True)
text(92,1390,'同样提交可核查产物',26,C['navy'])

down(1200,1658,1684)
polygon([(1200,1687),(1670,1785),(1200,1883),(730,1785)],C['greenbg'],C['green'])
text(1200,1757,'主协调者验收',32,C['green'],600,anchor='middle')
text(1200,1799,'输入一致、证据对应、计算可复算，',29,C['green'],anchor='middle')
text(1200,1838,'是否回答了被分派的子问题？',29,C['green'],anchor='middle')
line([(1670,1785),(1760,1785)],C['orange'],3,True,True)
text(1687,1767,'否',26,C['orange'])
box(1765,1685,565,197,'退回相关模块或降低状态',
    ['补齐证据、计算或方法产物',
     '版本变化：重做受影响部分',
     '分歧按事实、假设与价值核对'],C['orangebg'])
down(1200,1883,1932)
text(1225,1915,'是',27,C['navy'])
box(750,1935,900,166,'S5：反驳与复核',
    ['重大建议由 R01 查证据、反例与反转条件',
     '工具不可用时注明实际自审方式及未核实项'])
line([(1650,2014),(1762,2014)],C['orange'],3,True,True)
box(1765,1935,565,166,'有阻断性缺口：返回修正',
    ['回到受影响的 S1—S4',
     '结论强度不得超过实际依据'],C['orangebg'])
line([(1200,2101),(1200,2167)],C['navy'],3,True)
text(1225,2145,'给出与依据相称的状态',25,C['navy'])
box(750,2170,900,148,'S6—S8：建议、取舍、授权行动与反馈',
    ['分别记录建议状态、用户选择和实际执行'])
box(70,1935,640,383,'持续校验的规则',
    ['同一输入版本对应同一批分析产物',
     '比较或建议变化后，旧复核须重核',
     '方案内容改变后，核对旧选择与授权',
     '补证有期限和资源上限',
     '多个模型一致不等于独立证据',
     '角色定义不等于长期后台运行'],C['bluebg'])

# Full module catalog: one main role group per module, with concrete outputs.
text(70,2420,'23 个模块：主要职责与可检查产物',39,C['navy'],600)
text(70,2470,'按当前阶段与子问题选用；分组不互斥，知识与工具可在任何相关阶段参与。',28,C['muted'])

methods=[
    ('M01','逻辑与科学方法','主张、前提与证据对应表'),
    ('M03','概率与统计','样本检查、效应与不确定性'),
    ('M04','因果推断与实验','因果问题、设计与识别假设'),
    ('M05','决策理论','真实取舍、条件与反转点'),
    ('M06','运筹与资源配置','约束、可行配置与调度方案'),
    ('M07','博弈与合作','合理回应与可执行合作条件'),
    ('M13','调查研究与实践','一线材料、矛盾与阶段重点'),
    ('M14','系统科学与控制','关系图、反馈、延迟与副作用'),
]
knowledge=[
    ('M02','基础数学','变量、单位与可复算的数量关系'),
    ('M08','微观与宏观经济','需求、激励、成本与环境影响'),
    ('M09','马克思主义政治经济学','劳动、资本、控制与分配结构'),
    ('M10','心理学与行为科学','行为解释、认知偏差与习惯阻力'),
    ('M11','社会制度与组织','社会、政治、规则与组织约束'),
    ('M12','历史与思想史','时间线、路径依赖与类比边界'),
    ('M19','个人财务','现金流、总成本与承受边界'),
    ('M20','法律基础','适用规则、证据与程序节点'),
    ('M21','健康基础','适用证据、行动与停止条件'),
    ('M23','文学艺术、音乐、美学与伦理','生活体验、价值冲突与伦理边界'),
]
execution=[
    ('M15','计算机、数据与安全','数据质量、处理结果与权限范围'),
    ('M16','机器学习、AI 与自动化','任务基线、评价结果与失败处理'),
    ('M17','语言表达、沟通与谈判','表达稿、利益条件与可核验约定'),
    ('M18','管理与执行','任务依赖、责任、验收与复盘'),
    ('M22','英语与原始资料检索','检索式、原始出处与术语核对'),
]
all_ids=[v[0] for v in methods+knowledge+execution]
assert sorted(all_ids)==[f'M{i:02}' for i in range(1,24)]

def catalog(x,title,entries,gap):
    rect(x,2510,730,1050,C['white'],C['line'],r=20)
    rect(x,2510,730,75,C['navy'],r=20)
    text(x+28,2560,title,32,C['white'],600,maxwidth=670)
    for i,(mid,name,product) in enumerate(entries):
        y=2628+i*gap
        text(x+27,y,mid,26,C['blue'],600)
        text(x+105,y,name,28,C['navy'],600,maxwidth=600)
        text(x+105,y+36,product,25,C['muted'],maxwidth=600)
        if i<len(entries)-1:
            line([(x+28,y+53),(x+702,y+53)],C['line'],1)

catalog(70,'决策方法 · 8 个模块',methods,103)
catalog(835,'领域与基础知识 · 10 个模块',knowledge,91)
catalog(1600,'信息处理与执行 · 5 个模块',execution,105)
rect(94,3470,682,65,C['greenbg'],r=12)
text(116,3512,'M01、M05 与 M23 伦理检查贯穿决策',25,C['green'],maxwidth=640)
rect(1627,3176,676,353,C['bluebg'],r=18)
text(1653,3225,'每个模块统一回传',29,C['navy'],600)
texts(1653,3273,[
    '适用性、实际输入、方法与产物',
    '证据出处、假设局限、反对理由',
    '阻断缺口、最小下一步',
    '决策 ID、阶段、版本与执行者',
    '实际未核查内容必须明确列出',
],26,44,C['muted'],maxwidth=620)

rect(70,3610,2260,194,C['bluebg'],r=20)
text(101,3656,'如何读这张图',30,C['navy'],600)
texts(101,3703,[
    '上半部分：一次子任务怎样进入、被执行、验收和复核。下半部分：按子问题选择的模块及其交付内容。',
    'M13 含毛泽东思想中的调查、实践与矛盾分析；M14 含钱学森系统工程，均结合具体条件与证据使用。',
    '模块输出须接受检验；AI 意见、规则检查或复核通过，不代表事实已被认证，也不替用户作最终选择。',
],26,36,C['muted'],maxwidth=2190)
text(70,3860,'运行逻辑示意：本图展示分工与契约，未表示本次已启动 23 个子智能体。',25,C['muted'])

title='科学决策引擎3.0子智能体协作图'
defs_svg=''.join(f'<path id="{gid}" d="{esc(path)}"/>' for gid,path in defs.values())
document=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc"><title id="title">{title}</title><desc id="desc">主协调者分派独立子任务或直接执行，按依赖安排任务，验收实际产物，再由R01复核；附二十三个模块与产物对照。</desc><defs>{defs_svg}</defs><rect width="{W}" height="{H}" fill="{C["bg"]}"/>{"".join(svg)}</svg>'
(OUT/f'{title}.svg').write_text(document,encoding='utf-8')
print(json.dumps({'svg':str(OUT/f'{title}.svg'),'module_ids':all_ids,'labels':len(bounds)},ensure_ascii=False))
