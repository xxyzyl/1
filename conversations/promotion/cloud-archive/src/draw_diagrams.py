from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from xml.sax.saxutils import escape
import json, subprocess, hashlib, struct, zlib
from PIL import Image

ROOT = Path(__file__).parent
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
FONTS = [TTFont(str(ROOT/'cjk.ttf')), TTFont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
CMAPS = [f.getBestCmap() for f in FONTS]
SETS = [f.getGlyphSet() for f in FONTS]
UPMS = [f['head'].unitsPerEm for f in FONTS]
C = dict(bg='#F4F7FB', ink='#172C43', muted='#5A6D82', blue='#2865C7', pale='#EDF4FF',
         teal='#087C76', mint='#E9F6F2', orange='#B9651F', peach='#FFF3E6',
         purple='#6950A1', lilac='#F0EBF8', line='#CFDAE5', white='#FFFFFF')

class Drawing:
    def __init__(self, title, h=1600):
        self.w, self.h = 2000, h
        self.title=title; self.parts=[]; self.glyphs={}; self.textlog=[]
        self.rect(0,0,self.w,h,C['bg'],r=0)
    def rect(self,x,y,w,h,fill,stroke=None,r=18,sw=1.6):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw}"/>')
    def line(self,points,color=None,sw=2.5,arrow=False,dash=False):
        color=color or C['line']
        p=' '.join(('M' if i==0 else 'L')+f'{x},{y}' for i,(x,y) in enumerate(points))
        marker=f' marker-end="url(#arr-{color[1:]})"' if arrow else ''
        d=' stroke-dasharray="7 6"' if dash else ''
        self.parts.append(f'<path d="{p}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{marker}{d}/>')
    def circle(self,x,y,r,fill):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')
    def font_glyph(self,ch):
        fi = 1 if ord(ch)<128 or ch in '→←↑↓≤≠＋＝×' else 0
        if ord(ch) not in CMAPS[fi]: fi=1-fi
        assert ord(ch) in CMAPS[fi], repr(ch)
        return fi,CMAPS[fi][ord(ch)]
    def width(self,s,size):
        return sum(FONTS[fi]['hmtx'][g][0]/UPMS[fi]*size for fi,g in [self.font_glyph(ch) for ch in s])
    def text(self,x,y,s,size=24,color=None,bold=False,anchor='start',maxw=None):
        color=color or C['ink']
        width=self.width(s,size)
        if maxw and width>maxw:
            size*=maxw/width; width=maxw
        start=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
        assert start>=0 and start+width<=self.w+1,(s,start,width)
        assert y-size>=0 and y<self.h,(s,y)
        self.textlog.append(dict(text=s,x=start,y=y,size=round(size,2),width=round(width,1)))
        textparts=[]; cur=start
        for ch in s:
            fi,g=self.font_glyph(ch); key=f'g{fi}-{ord(ch)}'
            if key not in self.glyphs:
                pen=SVGPathPen(SETS[fi]); SETS[fi][g].draw(pen)
                self.glyphs[key]=pen.getCommands()
            scale=size/UPMS[fi]
            st=f' stroke="{color}" stroke-width="{UPMS[fi]*0.012}" stroke-linejoin="round"' if bold else ''
            textparts.append(f'<use href="#{key}" xlink:href="#{key}" transform="translate({cur:.3f},{y}) scale({scale:.7f},{-scale:.7f})"{st}/>')
            cur+=FONTS[fi]['hmtx'][g][0]*scale
        self.parts.append(f'<g fill="{color}" aria-label="{escape(s)}"><title>{escape(s)}</title>'+''.join(textparts)+'</g>')
    def lines(self,x,y,strings,size=22,leading=34,color=None,bold=False,maxw=None):
        for i,s in enumerate(strings): self.text(x,y+i*leading,s,size,color,bold,maxw=maxw)
    def chip(self,x,y,w,s,fill,color,size=19):
        self.rect(x,y,w,34,fill,r=10)
        self.text(x+w/2,y+24,s,size,color,True,'middle',w-14)
    def header(self,num,title,subtitle):
        self.text(64,59,'LIFE MANAGEMENT SYSTEM  /  4.0',17,C['blue'],True)
        self.text(64,124,title,51,C['ink'],True)
        self.text(64,170,subtitle,24,C['muted'],maxw=1740)
        self.circle(1900,94,36,C['ink'])
        self.text(1900,104,num,28,C['white'],True,'middle')
    def save(self,name):
        defs=[]
        for color in C.values():
            defs.append(f'<marker id="arr-{color[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="{color}"/></marker>')
        for key,path in self.glyphs.items():defs.append(f'<path id="{key}" d="{path}"/>')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="2000" height="{self.h}" viewBox="0 0 2000 {self.h}"><title>{escape(self.title)}</title><desc>人生管理系统4.0精确矢量设计图。文字转为轮廓以确保跨设备显示完整。</desc><defs>'+''.join(defs)+'</defs>'+''.join(self.parts)+'</svg>'
        p=OUT/(name+'.svg');p.write_text(svg)
        png=OUT/(name+'.png')
        subprocess.run(['inkscape',str(p),'--export-type=png',f'--export-filename={png}','--export-width=4800'],check=True,capture_output=True)
        with Image.open(png) as im: im.verify()
        with Image.open(png) as im:
            im.load(); dimensions=im.size
            im.convert('RGB').resize((1600,round(1600*self.h/2000)),Image.Resampling.LANCZOS).save(ROOT/(name+'-preview.png'))
        # Validate every PNG chunk, including the final IEND marker.
        data=png.read_bytes(); assert data[:8]==b'\x89PNG\r\n\x1a\n';off=8;end=False
        while off<len(data):
            n=struct.unpack('>I',data[off:off+4])[0];typ=data[off+4:off+8]
            payload=data[off+8:off+8+n]; crc=struct.unpack('>I',data[off+8+n:off+12+n])[0]
            assert zlib.crc32(typ+payload)&0xffffffff==crc
            off+=n+12
            if typ==b'IEND':end=True;break
        assert end and off==len(data)
        report={'name':name,'dimensions':dimensions,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'text_count':len(self.textlog),'smallest_font':min(t['size'] for t in self.textlog),'complete_png':True}
        (ROOT/(name+'-text.json')).write_text(json.dumps(self.textlog,ensure_ascii=False,indent=2))
        return report

def architecture():
    d=Drawing('人生管理系统4.0｜总体设计图')
    d.header('01','人生管理系统 4.0 · 总体设计','你决定什么值得追求；总控协调生活领域，共享能力提供分析与执行支持。')
    d.rect(64,212,1872,106,C['lilac'])
    d.text(94,253,'你：价值、方向与最终取舍',31,C['purple'],True)
    d.text(94,291,'目标  ·  不可牺牲的底线  ·  已有承诺  ·  授权范围',23,C['purple'])
    d.text(1904,255,'保留多元价值',26,C['purple'],True,'end')
    d.text(1904,291,'尊重他人自主选择，不设单一人生总分',21,C['purple'],False,'end')
    d.line([(720,318),(720,363)],C['purple'],arrow=True)
    d.text(739,348,'目标与边界',18,C['purple'])
    d.line([(1320,363),(1320,318)],C['purple'],arrow=True)
    d.text(1339,348,'呈现重要取舍',18,C['purple'])

    # Central coordinator: eight functions are duties, not eight new agents.
    d.rect(370,365,1260,280,C['ink'])
    d.text(401,411,'人生总控',34,C['white'],True)
    d.text(1600,410,'主协调者承担  ·  8 项职能',22,'#C9D8EA',False,'end')
    funcs=['目标与约束维护','观察与状态判断','跨领域影响分析','资源与优先级协调',
           '八阶段决策编排','授权与执行协调','分层反馈与调整','证据、复核与版本']
    for i,s in enumerate(funcs):
        x=400+(i%4)*302;y=440+(i//4)*63
        d.rect(x,y,283,49,'#294158',r=10)
        d.text(x+15,y+32,s,24,C['white'],maxw=254)
    d.line([(402,573),(1598,573)],'#53697F',1.5)
    d.text(403,615,'运行内核：S1—S8 决策引擎  /  全局资源账  /  同版本复核',24,C['white'],True,maxw=1190)

    d.rect(64,365,270,280,C['white'],C['line'])
    d.text(88,410,'资料与观测',29,C['blue'],True)
    d.lines(88,455,['主动输入','已提供的文件','已授权工具结果'],23,36)
    d.line([(88,550),(309,550)],C['line'],1.2)
    d.lines(88,583,['记录来源与时间','事实、假设、未知分开'],19,32,C['muted'],maxw=225)
    d.line([(334,500),(367,500)],C['blue'],arrow=True)

    d.rect(1666,365,270,280,C['white'],C['line'])
    d.text(1690,410,'R01 复核',29,C['orange'],True)
    d.lines(1690,454,['证据与反例','隐藏损害与遗漏','资源、接口与版本'],22,36,maxw=222)
    d.line([(1690,550),(1911,550)],C['line'],1.2)
    d.lines(1690,583,['复核意见返回总控','模型共识不替代证据'],19,32,C['muted'],maxw=222)
    d.line([(1630,480),(1663,480)],C['orange'],arrow=True)
    d.line([(1666,590),(1633,590)],C['orange'],arrow=True)

    d.line([(1000,645),(1000,700)],C['blue'],arrow=True)
    d.text(1020,679,'按需派工 · 在已有授权内协调行动',20,C['blue'])

    d.rect(370,704,1260,398,C['white'],C['line'])
    d.text(397,747,'9 个人生领域',29,C['teal'],True)
    d.text(1602,747,'维护生活结果  ·  相互影响  ·  按需启用',21,C['muted'],False,'end')
    domains=[
      ('D01','身体健康与恢复','身体功能 · 作息 · 恢复'),
      ('D02','心理状态与自我调节','感受 · 压力应对 · 心理功能'),
      ('D03','关系、家庭与照护','陪伴 · 沟通 · 照护承诺'),
      ('D04','职业、劳动与价值创造','工作 · 项目 · 产品与服务'),
      ('D05','学习、能力与探索','学习 · 实践 · 能力迁移'),
      ('D06','财务、资产与保障','收支 · 支付能力 · 风险承受'),
      ('D07','居住、日常与基础设施','居住 · 交通 · 日常与数字工具'),
      ('D08','社群、公共参与与生态责任','社群协作 · 公共贡献 · 环境'),
      ('D09','休闲、审美与生命体验','玩乐 · 艺术 · 自由与体验')]
    for i,(code,title,sub) in enumerate(domains):
        x=396+i%3*405;y=772+i//3*104
        d.rect(x,y,393,92,C['mint'],r=12)
        d.text(x+14,y+30,code,18,C['teal'],True)
        d.text(x+66,y+31,title,22,C['teal'],True,maxw=310)
        d.text(x+15,y+66,sub,20,C['muted'],maxw=363)

    d.rect(64,704,270,398,C['pale'],r=18)
    d.text(88,749,'共同资源账',29,C['blue'],True)
    d.lines(88,793,['时间 · 资金 · 承诺','保留缓冲与负荷边界'],21,34,maxw=223)
    d.line([(88,850),(309,850)],'#B8CFEF',1.4)
    d.lines(88,884,['一件事项','一个全局行动 ID','一个主责领域'],22,36,C['ink'],maxw=223)
    d.chip(88,984,221,'跨域影响可共享','#D8E7FE',C['blue'],20)
    d.lines(88,1052,['时间和费用只计一次'],20,31,C['blue'],True,maxw=223)
    d.line([(334,896),(367,896)],C['blue'],arrow=True)

    d.rect(1666,704,270,398,C['mint'],r=18)
    d.text(1690,749,'实际结果与环境',27,C['teal'],True,maxw=223)
    d.lines(1690,793,['行动结果与个人体验','现实环境、他人反应','比较原预期与新结果'],21,34,maxw=223)
    d.line([(1690,900),(1911,900)],'#AFD6CD',1.4)
    d.lines(1690,938,['指标不等于真实状态','考虑测量误差与延迟','根据反馈更新判断'],20,34,C['teal'],maxw=223)
    d.text(1690,1064,'变化后重核受影响决定',19,C['teal'],True,maxw=223)
    d.line([(1630,870),(1663,870)],C['teal'],arrow=True)
    d.line([(1800,704),(1800,674),(1530,674),(1530,648)],C['teal'],arrow=True)

    # Shared capability pool, grouped by primary purpose: 8 + 10 + 5 = 23.
    d.line([(1000,1144),(1000,1105)],C['purple'],arrow=True)
    d.text(1020,1130,'共享能力供总控与各领域按需调用',18,C['purple'])
    d.rect(64,1144,1872,356,C['white'],C['line'])
    d.text(91,1188,'23 个共享知识、方法与工具模块',29,C['ink'],True)
    d.text(1910,1188,'按主要用途归类；同一模块可跨阶段使用',20,C['muted'],False,'end')
    groups=[
      (91, '决策方法 · 8',C['blue'],C['pale'],[
       'M01 逻辑与科学方法  ·  M03 概率统计',
       'M04 因果与实验  ·  M05 决策理论',
       'M06 运筹学  ·  M07 博弈论',
       'M13 调查与实践  ·  M14 系统与控制']),
      (708,'知识与价值 · 10',C['purple'],C['lilac'],[
       'M02 数学  ·  M08 经济学  ·  M09 政治经济学',
       'M10 心理学  ·  M11 制度与组织  ·  M12 历史',
       'M19 财务  ·  M20 法律  ·  M21 健康',
       'M23 文学、艺术、音乐、美学与伦理']),
      (1325,'信息与执行 · 5',C['teal'],C['mint'],[
       'M15 计算机与数据  ·  M16 AI与自动化',
       'M17 沟通谈判  ·  M18 管理执行',
       'M22 英语与原始资料检索'])]
    for x,title,col,fill,lines in groups:
        d.rect(x,1213,584,226,fill,r=12)
        d.text(x+20,1254,title,27,col,True)
        d.lines(x+20,1297,lines,21,35,C['ink'],maxw=544)
    d.text(91,1476,'贯穿全程：逻辑、科学方法、目标与价值检查；重大建议检查反例和跨领域后果。',21,C['muted'])
    d.text(64,1545,'方案 / Skill 原型',20,C['ink'],True)
    d.text(297,1545,'角色按需运行；尚未部署持续采集或自动后台控制。',20,C['muted'])
    d.text(1936,1580,'系统工程思想的应用设计；九领域分类与运行规则由本项目提出。',18,C['muted'],False,'end')
    return d.save('人生管理系统4.0-总体设计图')

def flow():
    d=Drawing('人生管理系统4.0｜决策与反馈流程图',1760)
    d.header('02','人生管理系统 4.0 · 决策与反馈流程','一个问题进入总控，经过八阶段决策；新结果返回受影响的阶段，形成持续修正的闭环。')
    d.rect(64,208,1872,85,C['ink'])
    d.text(92,243,'触发：新问题 / 新目标 / 资源冲突 / 结果偏差 / 环境变化',25,C['white'],True)
    d.text(92,276,'总控先定位相关人生领域，带入同一版本的目标、底线、已有承诺与全局状态。',21,'#D8E4F2')
    d.chip(1546,232,361,'当前问题涉及哪些 D 领域？','#294158',C['white'],21)
    d.line([(990,293),(990,360)],C['blue'],arrow=True)
    d.text(66,336,'按阶段调用的知识与工具',22,C['purple'],True)
    d.text(694,336,'主流程与必要产物',22,C['blue'],True)
    d.text(1430,336,'检查未满足时，沿标注回退',22,C['orange'],True)

    stages=[
      ('S1','定义问题','目标、期限、硬约束与允许行动','同时定位相关领域，核对全局底线',
       ['逻辑 · 决策理论 · 伦理 · 心理','系统科学：划边界、辨目标'],
       '目标或边界不清','回 S1 澄清；不替用户设定价值'),
      ('S2','建立事实','证据账本、全局快照与关键未知','记录来源、时间、事实 / 假设 / 未知',
       ['科学方法 · 调查研究 · 概率统计','历史 · 英语检索 · 数据与AI'],
       '关键证据不足或相互矛盾','回 S2 补证；设调查预算与期限'),
      ('S3','生成方案','真实备选、资源需求与退出方式','包含现状、暂缓、缩减、替代或试行',
       ['决策理论 · 系统工程 · 经济学','博弈 · 制度组织 · 政治经济学'],
       '只有单一路径或缺乏真实备选','回 S3 扩充、拆分或试行方案'),
      ('S4','约束与比较','可行组合、收益风险与反转条件','先检查整体资源与承诺，再比较取舍',
       ['数学 · 统计 · 运筹 · 决策 · 博弈','按问题加入财务、法律、健康'],
       '超预算、撞时段或触碰底线','回 S3 改方案；高分不能抵消约束'),
      ('S5','反驳与复核','反对理由、证据缺口与复核记录','R01 检查同版本依据和跨领域后果',
       ['逻辑 · 科学方法 · 因果与实验','心理 · 系统科学 · 领域知识'],
       '反例成立、版本过期或遗漏损害','按缺口回 S2 / S3 / S4 重做'),
      ('S6','建议与取舍','条件建议、成立条件与实际选择','呈现收益、放弃什么，以及退出难度',
       ['决策理论 · 伦理 · 心理 · 沟通','涉及协商时调用谈判与博弈'],
       '用户尚未选择或倾向暂缓','保留状态；不默认已经决定'),
      ('S7','授权执行','行动 ID、责任、期限与验收条件','核对已有授权，登记资源上限和停止条件',
       ['项目管理 · 运筹 · 组织行为','沟通 · 行为科学 · 数据与自动化'],
       '行动超出授权或执行条件不成立','补足所需授权或条件后再行动'),
      ('S8','反馈更新','原预期、新结果、差异与新版本','区分测量、执行、机制与环境变化',
       ['统计 · 因果与实验 · 控制方法','调查实践 · 数据分析 · 管理复盘'],
       '变化影响原判断或效果尚未成熟','回受影响阶段；未成熟则继续观察')]
    ys=[]
    for i,(code,title,out,desc,knowledge,cond,action) in enumerate(stages):
        y=367+i*134;ys.append(y)
        d.rect(64,y,532,108,C['lilac'],r=14)
        d.lines(86,y+41,knowledge,23,35,C['purple'],maxw=488)
        d.line([(596,y+54),(658,y+54)],C['purple'],2,True)
        d.rect(663,y,652,108,C['white'],C['line'],r=14)
        d.circle(704,y+35,24,C['blue'])
        d.text(704,y+42,code,18,C['white'],True,'middle')
        d.text(745,y+39,title,29,C['blue'],True)
        d.text(745,y+71,out,23,C['ink'],True,maxw=547)
        d.text(745,y+98,desc,19,C['muted'],maxw=546)
        if i<7:
            d.line([(990,y+109),(990,y+130)],C['blue'],2.5,True)
        d.line([(1315,y+54),(1408,y+54)],C['orange'],2.1,True)
        d.rect(1413,y,523,108,C['peach'],r=14)
        d.text(1437,y+40,cond,24,C['orange'],True,maxw=475)
        d.text(1437,y+79,action,22,C['orange'],maxw=475)
    # Feedback trunk returns to problem/dispatch. Specific affected stage named in the side lane.
    bottom=ys[-1]+108
    d.line([(990,bottom),(990,1441),(31,1441),(31,250),(61,250)],C['teal'],2.7,True)
    d.chip(375,1425,520,'反馈：更新全局快照，重核受影响决定',C['mint'],C['teal'],22)
    d.text(1420,1449,'检查满足时向下推进；回退用 S 编号定位。',18,C['muted'])

    d.rect(64,1481,1872,107,C['white'],C['line'])
    d.text(87,1518,'三个状态独立记录',25,C['ink'],True)
    d.text(1910,1518,'形成建议 ≠ 用户已选择 ≠ 行动已执行',24,C['orange'],True,'end')
    states=[(88,'建议状态','待补证 / 条件建议 / 建议可供选择',C['blue']),
            (707,'用户选择','未知 / 未决定 / 已决定 / 暂缓',C['purple']),
            (1325,'执行状态','未知 / 未开始 / 执行中 / 已暂停 / 已完成 / 已停止',C['teal'])]
    for x,title,items,col in states:
        d.text(x,1557,title,21,col,True)
        d.text(x+100,1557,items,19,C['muted'],maxw=477)
    d.rect(64,1612,1872,80,C['mint'],r=14)
    d.text(89,1645,'分层反馈',25,C['teal'],True)
    d.text(270,1645,'日常看执行  →  周期协调资源  →  项目按观察窗口评价  →  阶段 / 重大事件复盘方向',23,C['teal'],maxw=1630)
    d.text(270,1676,'采集可以频繁；调整要考虑效果延迟。目标改变由用户决定，触碰明确底线时及时处理。',20,C['teal'],maxw=1630)
    d.text(64,1731,'重要决定完整运行；简单、可逆的小事可以压缩。已授权的工作继续推进，不重复索要确认。',20,C['muted'])
    d.text(1936,1731,'方案 / Skill 原型',20,C['muted'],False,'end')
    return d.save('人生管理系统4.0-决策流程图')

if __name__=='__main__':
    reports=[architecture(),flow()]
    (ROOT/'validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
    print(json.dumps(reports,ensure_ascii=False,indent=2))
