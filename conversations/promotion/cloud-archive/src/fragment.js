
(() => {
  const root = document.getElementById('life-map-v4');
  const stage = root.querySelector('.lm-stage');
  const edges = root.querySelector('.lm-edges');
  const layer = root.querySelector('.lm-nodes');
  const crumbs = root.querySelector('.lm-crumbs');
  const status = root.querySelector('.lm-announcement');
  const N = {};
  const add = (id,label,children=[],preview=[],subtitle='') => { N[id]={id,label,children,preview,subtitle}; };
  const leaf = (id,label,preview=[]) => add(id,label,[],preview);

  add('home','人生总控',['values','domains','evidence','engine','knowledge','action'],[],'协调时间、资金与承诺');
  add('values','你决定：追求什么',['direction','priority','limits','permission'],['人生方向与优先级','不可牺牲的底线'],'用户保留最终价值取舍');
  leaf('direction','人生方向',['想过怎样的生活','近期目标服务长期方向']);
  leaf('priority','价值与优先级',['收入、自由、关系、体验','冲突时由你作取舍']);
  leaf('limits','不能突破的底线',['身体与生活基本条件','已有责任与资源上限']);
  leaf('permission','授权范围',['哪些行动已经允许','何时停止或重新确认']);

  add('domains','管理什么：9个领域',['D01','D02','D03','D04','D05','D06','D07','D08','D09'],['健康 · 心理 · 关系','职业 · 学习 · 财务','日常 · 社群 · 体验'],'按生活结果划分');
  const domains = [
    ['D01','身体健康与恢复',['身体功能','作息与恢复','照护安排'],['M21','M03']],
    ['D02','心理状态与自我调节',['情绪体验','压力与应对','环境支持'],['M10','M21','M23']],
    ['D03','关系、家庭与照护',['亲密关系与友谊','家庭承诺','照护与协商'],['M17','M10','M20']],
    ['D04','职业、劳动与价值创造',['工作与创业','产品与实际交付','合作及职业路径'],['M08','M11','M18','M17']],
    ['D05','学习、能力与探索',['理解与技能','练习和真实作品','独立解决问题'],['M01','M02','M15','M16','M22']],
    ['D06','财务、资产与保障',['收支与现金流','支付能力','风险承受范围'],['M19','M03','M20']],
    ['D07','居住、日常与基础设施',['居住与交通','家务与证照','数字工具'],['M06','M15','M16','M18']],
    ['D08','社群、公共参与与生态责任',['公共参与','共同责任','社会及生态影响'],['M11','M12','M23']],
    ['D09','休闲、审美与生命体验',['玩乐与自由时间','艺术与审美','体验本身的价值'],['M23','M10']]
  ];
  domains.forEach(([id,label,items,mods]) => {
    leaf(id+'-focus','关注的生活结果',items);
    add(id+'-tools','按需调用能力',mods,mods.map(x=>x).slice(0,4));
    leaf(id+'-shared','交给总控协调',['时间、费用与承诺','对其他领域的影响']);
    add(id,label,[id+'-focus',id+'-tools',id+'-shared'],items.slice(0,2),'各领域共享资源，相互影响');
  });

  add('evidence','依据什么：数据与证据',['sources','quality','state','ask'],['已授权来源 + 用户补充','事实、假设、未知分开'],'先看清现状，再提出建议');
  add('sources','数据从哪里来',['source-user','source-connect','source-public'],['用户提供','授权接入','公开资料']);
  leaf('source-user','用户主动提供',['文字、语音、文件','目标、感受与现实限制']);
  leaf('source-connect','已有授权的数据源',['日历、任务与支出记录','接入能力需实际部署']);
  leaf('source-public','公开信息',['原始资料与可靠来源','相关规则、环境和机会']);
  leaf('quality','数据质量',['来源与时间','缺失、冲突与可信范围']);
  leaf('state','个人状态记录',['事实 ≠ 指标 ≠ 推测','保留历史版本与未知']);
  leaf('ask','主动补问',['只问可能改变选择的信息','已有资料先复用','问题合并，控制打扰']);

  add('engine','怎样决策：8个阶段',['S1','S2','S3','S4','S5','S6','S7','S8'],['定义 → 事实 → 方案 → 比较','复核 → 取舍 → 执行 → 更新'],'阶段有顺序，也允许回退');
  const stages = [
    ['S1','定义问题',['目标、期限、资源','不能突破的边界'],['M01','M05','M10','M14','M23']],
    ['S2','建立事实',['核实来源与实际情况','分清事实、假设与未知'],['M01','M03','M12','M13','M15','M22']],
    ['S3','生成方案',['行动、维持现状、暂缓','小规模试行与分阶段方案'],['M05','M07','M08','M09','M11','M14']],
    ['S4','约束与比较',['先查整个组合能否可行','再比成本、风险与取舍'],['M02','M03','M05','M06','M07','M19','M20','M21']],
    ['S5','反驳与复核',['找反例、复算关键数字','证据不足则返回补证'],['M01','M03','M04','M10','M14']],
    ['S6','建议与取舍',['说明建议成立的条件','记录用户的真实选择'],['M05','M10','M17','M23']],
    ['S7','授权执行',['安排任务、资源与期限','明确验收和停止条件'],['M06','M11','M15','M16','M17','M18']],
    ['S8','反馈更新',['对照预期与实际结果','回到最早受影响阶段'],['M03','M04','M13','M14','M15','M18']]
  ];
  stages.forEach(([id,label,items,mods],i) => {
    leaf(id+'-task','这一阶段做什么',items);
    add(id+'-tools','这一阶段调用什么',mods,[]);
    const next=i<7?'S'+(i+2):'S1';
    leaf(id+'-gate','如何推进或回退',i===3?['硬约束不通过 → 改方案','可行方案 → 复核']:i===4?['复核不通过 → 补证或重比','通过 → 给出条件建议']:i===7?['目标改变 → S1','事实改变 → S2','方案改变 → S3']:['条件具备 → '+next,'信息不足 → 补证或回退']);
    add(id,label,[id+'-task',id+'-tools',id+'-gate'],items,'第'+(i+1)+'阶段 / 共8阶段');
  });

  add('knowledge','调用什么：23个能力',['methods','fields','tools'],['决策方法：8个','领域知识与价值：10个','信息与执行：5个'],'按任务调用，可跨领域、跨阶段');
  add('methods','决策方法 · 8个',['M01','M03','M04','M05','M06','M07','M13','M14'],['判断、比较与检验'],'帮助形成和修正选择');
  add('fields','知识与价值 · 10个',['M02','M08','M09','M10','M11','M12','M19','M20','M21','M23'],['理解现实与价值边界'],'提供内容、背景和限制');
  add('tools','信息与执行 · 5个',['M15','M16','M17','M18','M22'],['获取资料、完成行动'],'把分析落实到具体工作');
  const modules = [
    ['M01','逻辑、认识论与科学方法',['前提与推理','科学证据与反例'],['检查说法是否有依据','交付：证据与反驳清单']],
    ['M02','基础数学',['数量关系与公式','函数、矩阵与变化'],['把资源和关系写清','交付：可复算模型']],
    ['M03','概率论与统计学',['概率与不确定性','抽样、估计与检验'],['判断数据支持到哪里','交付：区间与不确定性']],
    ['M04','因果推断与实验设计',['因果关系与混杂','对照和实验设计'],['检验行动是否有效','交付：试验与评价方案']],
    ['M05','决策理论',['收益、成本与可逆性','多目标取舍与信息价值'],['比较真正可选的方案','交付：条件建议']],
    ['M06','运筹学',['约束与资源分配','调度和优化'],['安排时间、预算和任务','交付：可行安排']],
    ['M07','博弈论',['利益、策略与回应','合作和激励'],['考虑他人的自主选择','交付：合作与谈判方案']],
    ['M08','微观经济学与宏观经济学',['需求、成本与激励','就业、周期与外部环境'],['分析经济条件','交付：成本与需求依据']],
    ['M09','马克思主义政治经济学',['生产、劳动与资源控制','利益结构与分配'],['分析结构性条件','交付：生产分配关系图']],
    ['M10','心理学与行为科学',['认知偏差与动机','情绪、习惯与环境'],['理解判断和行动阻力','交付：行为试行方案']],
    ['M11','社会学、政治学、制度与组织',['规则、权力与组织','角色、协作与制度'],['定位现实的权限和阻碍','交付：角色与流程分析']],
    ['M12','历史与思想史',['历史背景与路径依赖','史料、类比与差异'],['理解事情如何形成','交付：背景与适用边界']],
    ['M13','毛泽东思想中的调查与实践方法',['调查研究与实践检验','矛盾分析与阶段重点'],['了解具体条件再行动','交付：调查与试行记录']],
    ['M14','系统科学、控制论与钱学森系统工程',['整体、层次与接口','反馈、延迟与测量'],['检查跨域影响与调整','交付：系统及反馈模型']],
    ['M15','计算机、数据处理与信息安全',['数据整理、编程与可视化','权限、备份与可复现'],['把资料变成可核对结果','交付：数据与工具']],
    ['M16','机器学习、大模型与自动化',['AI推理与工具流程','效果评价与错误处理'],['让合适的任务自动完成','交付：已验证的工作流']],
    ['M17','语言表达、沟通与谈判',['表达、倾听与理解','协商、冲突与约定'],['让各方理解并达成约定','交付：沟通与谈判方案']],
    ['M18','管理与执行',['项目拆解与任务依赖','验收、复盘与协作'],['把选择变成实际交付','交付：行动计划与记录']],
    ['M19','个人财务',['收支、资产与负债','流动性与保障'],['核实资金能否承受','交付：现金流与风险边界']],
    ['M20','法律基础',['权利、义务与合同','程序、责任与证据'],['识别适用规则和限制','交付：待核实的法律问题']],
    ['M21','健康基础',['身体功能与恢复','健康信息和照护'],['检查负荷与健康边界','交付：需核实的健康条件']],
    ['M22','英语与原始资料检索',['英语理解与检索','原始来源和交叉核验'],['获取所需一手资料','交付：可追溯资料']],
    ['M23','文学、艺术、音乐、美学与伦理',['审美、意义与体验','伦理、价值与冲突'],['帮助理解什么值得追求','交付：价值与体验选项']]
  ];
  modules.forEach(([id,label,study,work])=>{
    leaf(id+'-study','包含的知识',study);
    leaf(id+'-work','怎样帮助决策',work);
    add(id,label,[id+'-study',id+'-work'],[study[0]],'共享能力模块 · 按需参与');
  });

  add('action','怎样行动与反馈',['dispatch','resources','three-states','feedback','proactive'],['派工 → 行动 → 观察','结果反馈到总控'],'建议、选择和执行分别记录');
  leaf('dispatch','派工与交付',['独立任务并行；依赖任务顺序','按交付物验收','重要建议安排复核']);
  leaf('resources','共同资源核算',['时间、资金、承诺统一检查','同一行动只记账一次','局部改善要检查整体影响']);
  add('three-states','分开记录3种状态',['advice-state','choice-state','execution-state'],['建议依据','用户选择','实际执行']);
  leaf('advice-state','建议是否成立',['待补证 / 条件建议','建议可供选择']);
  leaf('choice-state','用户是否选择',['未知 / 未决定','已决定 / 暂缓']);
  leaf('execution-state','行动是否发生',['未知 / 未开始 / 执行中','已暂停 / 已完成 / 已停止']);
  leaf('feedback','反馈回到总控',['对照预测与真实结果','考虑测量误差和效果延迟','条件改变 → 重新评估']);
  leaf('proactive','主动服务设计',['授权取数 → 必要补问','识别变化 → 提出建议','后台采集与提醒仍需部署']);
  add('controller','总控具体做什么',['control-goals','control-state','control-impact','resources','control-decision','dispatch','feedback','control-history'],[],'跨领域协调，不替你决定人生价值');
  leaf('control-goals','维护目标与底线',['把新任务放回人生方向','检查是否触碰不可接受边界']);
  leaf('control-state','判断当前状态',['汇总各领域证据','事实与推测分开']);
  leaf('control-impact','检查跨领域影响',['职业计划会否挤压恢复','资源与承诺是否互相冲突']);
  leaf('control-decision','组织具体决策',['调用8阶段引擎','选择需要的知识模块']);
  leaf('control-history','保存证据与版本',['保留依据、选择和执行记录','条件变化后重核旧结论']);

  let route=['home'];
  let resizeTimer;
  const shortId = id => /^[DM]\d\d$/.test(id) || /^S\d$/.test(id) ? id : '';
  function go(id){ route.push(id); render(true); }
  function createNode(node,center=false){
    const wrap=document.createElement('div');wrap.className='lm-node'+(center?' center':'');wrap.dataset.id=node.id;
    const head=document.createElement('div');head.className='lm-node-head';wrap.appendChild(head);
    const target=center?(node.id==='home'?'controller':null):(node.children.length?node.id:null);
    const el=document.createElement(target?'button':'div');
    if(target){el.type='button';el.className='btn '+(center?'btn-primary':'btn-ghost');el.addEventListener('click',()=>go(target));el.setAttribute('aria-label',node.label+'，展开');}
    else el.className='lm-static';
    const title=document.createElement('span');title.className='lm-node-title';
    if(shortId(node.id)){const code=document.createElement('span');code.className='lm-code';code.textContent=shortId(node.id);title.appendChild(code);}
    title.appendChild(document.createTextNode(node.label+(target&&!center?' ›':'')));el.appendChild(title);head.appendChild(el);
    if(center&&node.subtitle){const sub=document.createElement('div');sub.className='lm-subtitle text-small text-muted';sub.textContent=node.subtitle;wrap.appendChild(sub);}
    if(!center&&node.preview.length){const previews=document.createElement('div');previews.className='lm-previews text-small';node.preview.forEach(p=>{const line=document.createElement('div');line.className='lm-preview';line.textContent=p;previews.appendChild(line);});wrap.appendChild(previews);}
    layer.appendChild(wrap);return wrap;
  }
  function path(d){const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',d);edges.appendChild(p);}
  function headMid(el){return el.offsetTop+el.querySelector('.lm-node-head').offsetHeight/2;}
  function render(announce=false){
    const id=route.at(-1),node=N[id];
    crumbs.replaceChildren();
    route.forEach((rid,i)=>{if(i){const sep=document.createElement('span');sep.className='text-muted';sep.textContent='›';crumbs.appendChild(sep);}const label=rid==='home'?'系统全景':N[rid].label;
      if(i<route.length-1){const b=document.createElement('button');b.type='button';b.className='btn btn-ghost';b.textContent=label;b.onclick=()=>{route=route.slice(0,i+1);render(true);};crumbs.appendChild(b);}
      else {const span=document.createElement('span');span.textContent=label;span.setAttribute('aria-current','page');crumbs.appendChild(span);}
    });
    layer.replaceChildren();edges.replaceChildren();
    const w=stage.getBoundingClientRect().width;
    const center=createNode(node,true);
    const children=node.children.map(cid=>createNode(N[cid]));
    const mobile=w<620;
    if(mobile){
      center.style.width=(w-36)+'px';center.style.left='18px';center.style.top='0px';
      let y=center.offsetHeight+30;
      children.forEach(el=>{el.style.width=(w-62)+'px';el.style.left='48px';el.style.top=y+'px';y+=el.offsetHeight+23;});
      const h=Math.max(y-10,center.offsetHeight+15);stage.style.height=h+'px';edges.setAttribute('viewBox',`0 0 ${w} ${h}`);
      const start=center.offsetTop+center.offsetHeight;
      if(children.length){const last=headMid(children.at(-1));path(`M ${w/2} ${start} V ${start+14} H 27 V ${last}`);children.forEach(el=>path(`M 27 ${headMid(el)} H 48`));}
    } else {
      const sideW=Math.min(220,(w-202)/2),centerW=156;
      const split=Math.ceil(children.length/2),left=children.slice(0,split),right=children.slice(split);
      for(const el of children)el.style.width=sideW+'px';center.style.width=centerW+'px';
      const heights=arr=>arr.reduce((sum,e)=>sum+e.offsetHeight,0)+Math.max(0,arr.length-1)*34;
      const h=Math.max(heights(left),heights(right),center.offsetHeight+80)+20;
      center.style.left=((w-centerW)/2)+'px';center.style.top=((h-center.offsetHeight)/2)+'px';
      const place=(arr,x)=>{let y=(h-heights(arr))/2;arr.forEach(el=>{el.style.left=x+'px';el.style.top=y+'px';y+=el.offsetHeight+34;});};place(left,0);place(right,w-sideW);
      stage.style.height=h+'px';edges.setAttribute('viewBox',`0 0 ${w} ${h}`);
      const cy=headMid(center),cx=(w-centerW)/2;
      left.forEach(el=>{const y=headMid(el);path(`M ${cx} ${cy} C ${cx-30} ${cy}, ${sideW+28} ${y}, ${sideW} ${y}`);});
      right.forEach(el=>{const y=headMid(el);path(`M ${cx+centerW} ${cy} C ${cx+centerW+30} ${cy}, ${w-sideW-28} ${y}, ${w-sideW} ${y}`);});
    }
    if(announce)status.textContent='已展开'+node.label+'，'+node.children.length+'个分支。';
  }
  const observer=new ResizeObserver(()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>render(),40);});observer.observe(stage);
  render();
})();
