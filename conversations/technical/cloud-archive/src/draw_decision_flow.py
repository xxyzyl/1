from pathlib import Path
from html import escape
from math import atan2, cos, sin, pi
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import json

OUT = Path('/workspace/scratch/6d107901a9b1/decision-flow')
OUT.mkdir(parents=True, exist_ok=True)
FONT = str(OUT / 'NotoSansSC.ttf')
W,H,S = 2400,4200,1.5
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

rows=[
 dict(title='定义问题',question='到底要解决什么？',
      modules=[1,5,10,13,14,17,23],
      knowledge=['逻辑与认识论｜明确概念，分开事实与价值',
                 '决策理论与伦理｜目标、优先级与不可牺牲的边界',
                 '心理学与沟通｜识别偏差，确认真实诉求',
                 '系统科学｜问题边界、利益相关者与依赖',
                 '调查与矛盾分析｜具体条件与阶段重点'],
      outputs=['一句话决策问题','目标、硬约束、期限','可用资源与允许行动'],
      gate=['目标与关键约束','是否足够明确？'],
      back=['回 S1：澄清会改变选择的问题','不猜预算、偏好或用户授权']),
 dict(title='建立事实',question='我们实际知道什么？',
      modules=[1,3,12,13,15,16,22],
      knowledge=['科学方法与调查研究｜核对原始材料和一线情况',
                 '概率统计｜样本质量、基准率与不确定性',
                 '历史与思想史｜形成过程、历史条件与类比边界',
                 '英语检索、计算机与数据｜检索、清洗、溯源',
                 'AI 辅助阅读｜抽取信息后回查原文'],
      outputs=['带版本的事实与证据记录','事实、假设、未知分开','决定性来源与具体缺口'],
      gate=['关键事实是否足以','开展后续分析？'],
      back=['回 S2：补决定性资料','到达期限：保留缺口，转 S6 说明']),
 dict(title='生成方案',question='有哪些真实行动路径？',
      modules=[4,5,6,7,8,9,11,14],
      knowledge=['决策理论｜维持、暂缓、试行等真实备选',
                 '经济学与博弈论｜需求、激励与他人回应',
                 '社会学、政治学与组织行为｜规则、权力与协作',
                 '马克思主义政治经济学｜劳动、资本与分配',
                 '系统工程与实验设计｜组合方案和验证路径'],
      outputs=['真实备选及行动内容','进入条件、资源需求','可能后果与退出方式'],
      gate=['备选是否真实可选','且有必要的替代路径？'],
      back=['回 S3：补充或重构方案','仅一个方案时，说明原因']),
 dict(title='约束与比较',question='哪些可行，如何取舍？',
      modules=[2,3,5,6,7,8,19,20,21],
      knowledge=['基础数学、概率统计｜数量关系、风险与区间',
                 '决策理论｜取舍、机会成本与敏感性',
                 '运筹学｜预算、时间与资源配置',
                 '博弈论与经济学｜合作条件、激励与外部性',
                 '个人财务、法律、健康｜现实底线与承受能力'],
      outputs=['先筛硬约束，再做比较','数据可靠：概率与效用','数据不足：情景与反转条件'],
      gate=['有满足硬约束的方案','且比较依据足够吗？'],
      back=['依据不足回 S2；不可行回 S3','调整 S1 约束须由用户认可']),
 dict(title='反驳与复核',question='这个结论可能错在哪里？',
      modules=[1,2,3,4,10,14],
      knowledge=['逻辑与科学方法｜反例、论证和竞争解释',
                 '数学与统计｜复算、样本偏差与敏感性',
                 '因果推断｜混杂、反向因果与识别条件',
                 '心理学、系统科学｜确认偏误、遗漏与延迟',
                 '相关领域知识｜核查适用范围；重大建议由 R01 复核'],
      outputs=['最强反对理由与反转条件','本次输入及建议的复核记录','已解决问题与剩余缺口'],
      gate=['关键检查已完成','且无阻断性缺口？'],
      back=['按问题返回 S1 / S2 / S3 / S4','仅重核受影响部分，保留缺口']),
 dict(title='建议与取舍',question='依据支持什么，你选择什么？',
      modules=[5,7,10,17,23],
      knowledge=['决策理论｜推荐理由、成立条件与多目标取舍',
                 '伦理学与心理学｜价值冲突、自主选择与偏差',
                 '语言表达与沟通｜讲清依据、局限和代价',
                 '谈判与博弈论｜需要协商时明确利益与条件',
                 '文学、艺术、音乐与美学｜按需理解生活体验和价值'],
      outputs=['与证据匹配的建议状态','依据、代价与成立条件','用户实际选择及其来源'],
      gate=['拟执行的具体动作','是否已有适用授权？'],
      back=['停在 S6：保留建议与可审阅草案','已有适用授权，不重复询问']),
 dict(title='授权执行',question='如何把选择变成行动？',
      modules=[4,6,10,11,15,16,17,18,19,20,21],
      knowledge=['管理与运筹｜任务、责任、依赖、预算和缓冲',
                 '组织行为、沟通谈判｜协调分工与反馈',
                 '心理与行为科学｜习惯、阻力与执行环境',
                 '计算机、AI 与自动化｜在授权范围内处理任务',
                 '法律、财务、健康与实验设计｜边界、验收和停止条件'],
      outputs=['具体任务与真实执行记录','资源上限、验收标准','观察指标与停止条件'],
      gate=['动作完成或达到','本次反馈检查点？'],
      back=['留 S7：按计划推进，必要时暂停','条件变化或出现问题：提前进 S8']),
 dict(title='反馈更新',question='结果改变了哪些判断？',
      modules=[3,4,13,14,15,16,18],
      knowledge=['概率统计｜更新判断，检查预测与实际差异',
                 '因果推断与实验｜区分行动效果和其他解释',
                 '控制论、系统动力学｜反馈、延迟与长期演化',
                 '调查研究与实践、管理复盘｜修正假设和行动',
                 '数据分析、机器学习评估｜检验工具表现与错误'],
      outputs=['原预期与新结果并列','判断、执行、环境与偶然性','调整事项与下一次复盘点'],
      gate=['目标、事实或方案','发生实质变化吗？'],
      back=['建立新输入版本，保留旧记录','回到受影响的最早阶段']),
]
assert set(sum((r['modules'] for r in rows),[]))==set(range(1,24))

# Header and legend.
text(70,107,'科学决策引擎',66,weight=600)
text(70,168,'详细流程图：每一步调用什么知识，如何检查与修正',36,C['muted'])
rect(2130,54,200,70,C['navy'],r=18)
text(2230,101,'版本 3.0',32,C['white'],600,anchor='middle')
rect(70,205,2260,72,C['navy'],r=16)
text(110,254,'全程贯穿：逻辑与科学方法 · 用户目标与伦理价值 · 证据溯源 · 权限与现实边界',31,C['white'],400,maxwidth=2180)
text(70,326,'23 个模块按需参与；同一学科可跨阶段调用。表中的检查用于推进流程，不能证明结论必然正确。',27,C['muted'],maxwidth=2260)
text(80,389,'按需调用的知识与工具',34,C['blue'],600)
text(1050,389,'决策阶段与必要产物',34,C['navy'],600)
text(1760,389,'检查条件与回退路径',34,C['orange'],600)

for i,row in enumerate(rows):
    y=435+i*375
    # Knowledge lane.
    rect(70,y,860,300,C['bluebg'],C['line'],r=20)
    text(99,y+44,'主要调用',25,C['blue'],600)
    texts(99,y+91,row['knowledge'],28,40,maxwidth=805)
    line([(931,y+151),(1018,y+151)],C['blue'],3,True)
    # Process lane.
    rect(1020,y,600,300,C['white'],C['line'],r=20,sw=2)
    rect(1045,y+23,77,53,C['navy'],r=13)
    text(1083.5,y+60,f'S{i+1}',31,C['white'],600,anchor='middle')
    text(1140,y+63,row['title'],41,C['navy'],600,maxwidth=455)
    text(1050,y+111,row['question'],28,C['muted'],maxwidth=545)
    line([(1050,y+134),(1590,y+134)],C['line'],1.5)
    texts(1050,y+184,row['outputs'],30,41,maxwidth=545)
    # Gate and an explicit return destination.
    line([(1621,y+90),(1780,y+90)],C['navy'],3,True)
    text(1651,y+73,'检查',22,C['muted'])
    polygon([(2025,y+15),(2270,y+90),(2025,y+165),(1780,y+90)],C['greenbg'],C['green'])
    text(2025,y+78,row['gate'][0],28,C['green'],600,anchor='middle')
    text(2025,y+116,row['gate'][1],28,C['green'],600,anchor='middle')
    rect(1760,y+212,570,88,C['orangebg'],r=15)
    texts(1782,y+246,row['back'],27,36,C['orange'],maxwidth=525)
    line([(2270,y+90),(2350,y+90),(2350,y+254),(2330,y+254)],C['orange'],3,True,True)
    text(2310,y+77,'是' if i==7 else '否',25,C['orange'])
    # Passing the gate advances to the next process box.
    route_y=y+337
    line([(2025,y+165),(2025,y+183),(1670,y+183),(1670,route_y),(1320,route_y),(1320,y+375 if i<7 else y+397)],C['navy'],3,True)
    text(2047,y+194,'否' if i==7 else '是',25,C['navy'])

# Final loop/observation state.
rect(1035,3457,570,54,C['greenbg'],C['green'],r=14)
text(1320,3494,'保留当前判断，按复盘点继续观察',27,C['green'],600,anchor='middle')
text(70,3487,'橙色虚线：返回框内标明的阶段',26,C['orange'])

# Three separate states.
text(70,3580,'三个状态独立记录',36,C['navy'],600)
text(570,3580,'建议有依据、用户已选择、动作已完成，分别核实',27,C['muted'])
cards=[
    (70,730,'建议状态',['待补证  /  条件建议  /  建议可供选择','用户同意不会自动提高证据等级']),
    (835,730,'用户选择',['未知  /  未决定  /  已决定  /  暂缓','选择须对应当时的目标、约束与具体方案']),
    (1600,730,'执行状态',['未知  /  未开始  /  执行中  /  已暂停','已完成  /  已停止；没有记录就保持未知']),
]
for x,w,title,body in cards:
    rect(x,3610,w,159,C['white'],C['line'],r=18)
    text(x+26,3653,title,30,C['navy'],600)
    texts(x+26,3700,body,27,38,maxwidth=w-50)

# Persistent rules and division of labor.
rect(70,3802,2260,302,C['bluebg'],r=20)
text(98,3848,'跨阶段规则与协作',31,C['navy'],600)
texts(98,3894,[
    '输入、比较或建议发生变化：重核受影响部分；方案内容改变后，核对旧选择与授权是否仍适用。',
    '补证设期限与资源上限；不为填表延误有依据的必要行动。知识模块随问题调用，不必每次全部启动。',
    '调查研究与实践含毛泽东思想相关方法；系统工程含钱学森相关思想，均结合具体条件与现代证据使用。'
],26,37,C['muted'],maxwidth=2190)
actors=[('主协调者','推进流程，验收产物'),('学科子智能体','处理独立子问题，回传依据'),('复核角色 R01','重大建议核查证据与反例'),('用户','确定目标与取舍，保留决定权')]
for j,(title,body) in enumerate(actors):
    x=98+j*554
    text(x,4037,title,28,C['navy'],600)
    text(x,4075,body,25,C['muted'],maxwidth=540)
text(70,4160,'说明：简单可逆事项可压缩流程；未核实的硬约束不能靠高分抵消。复核与脚本检查不等于事实认证。',25,C['muted'],maxwidth=2260)

# Export vector outlines and the high-resolution image from identical geometry.
title='科学决策引擎3.0详细流程图'
defs_svg=''.join(f'<path id="{gid}" d="{esc(path)}"/>' for gid,path in defs.values())
document=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc"><title id="title">{title}</title><desc id="desc">八阶段流程、二十三个知识模块、阶段检查、回退路径及建议、用户选择、执行三种独立状态。</desc><defs>{defs_svg}</defs><rect width="{W}" height="{H}" fill="{C["bg"]}"/>{"".join(svg)}</svg>'
(OUT/f'{title}.svg').write_text(document,encoding='utf-8')
im.save(OUT/f'{title}.png',optimize=True,dpi=(300,300))
im.resize((1200,2100),Image.Resampling.LANCZOS).save(OUT/'preview.png')
im.crop((0,0,int(W*S),int(1200*S))).resize((1600,800),Image.Resampling.LANCZOS).save(OUT/'preview-top.png')
(OUT/'diagram-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps({'png':str(OUT/f'{title}.png'),'svg':str(OUT/f'{title}.svg'),'pixels':im.size,'knowledge_modules':23,'labels':len(bounds),'vector_glyphs':len(defs)},ensure_ascii=False))
