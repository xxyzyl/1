import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const ROOT='/workspace/scratch/d317e6067fb4/ppt-life';
const data=JSON.parse(await fs.readFile(path.join(ROOT,'deck-content.json'),'utf8'));
const deck=Presentation.create({slideSize:{width:1280,height:720}});
const C={ink:'#111111',muted:'#555D66',rule:'#C9CDD1',gray:'#F0F1F2',blue:'#2865C7',pale:'#E9F0FA',white:'#FFFFFF'};
const FONT='Droid Sans Fallback';
const ledger=[];
const minfont=22;
function charUnit(ch){if(/[\u0000-\u007f]/.test(ch))return /[il.,:;'|! ]/.test(ch)?.3:/[MW@%]/.test(ch)?.88:.59;return 1;}
function width(s,sz){return [...s].reduce((a,c)=>a+charUnit(c)*sz,0);}
const segmenter=new Intl.Segmenter('zh',{granularity:'word'});
function wrap(s,max,sz){
 const result=[];
 for(const para of String(s).split('\n')){
  let line='',w=0;const greedy=[];
  for(const ch of para){let cw=charUnit(ch)*sz;if(w+cw>max&&line){greedy.push(line);line='';w=0;}line+=ch;w+=cw;}greedy.push(line);
  const latinBreak=greedy.some((v,i)=>i<greedy.length-1&&/[A-Za-z0-9]$/.test(v)&&/^[A-Za-z0-9]/.test(greedy[i+1]));
  const bad=greedy.length>1&&(greedy.some(v=>/^[。，、；：！？）】》」』”’]/.test(v))||width(greedy.at(-1),sz)<sz*6||latinBreak);
  if(!bad){result.push(...greedy);continue;}
  const chars=[...para],n=chars.length,prefix=[0];chars.forEach(ch=>prefix.push(prefix.at(-1)+charUnit(ch)*sz));
  const boundaries=new Set([0,n]);for(const segment of segmenter.segment(para))boundaries.add(segment.index+segment.segment.length);
  let bestLines=null;
  for(let count=greedy.length;count<=greedy.length+1&&!bestLines;count++){
   const ideal=prefix[n]/count,dp=Array.from({length:count+1},()=>Array(n+1).fill(Infinity));
   const prev=Array.from({length:count+1},()=>Array(n+1).fill(-1));dp[0][0]=0;
   for(let k=1;k<=count;k++)for(let end=1;end<=n;end++){
    if(end<n&&/^[。，、；：！？）】》」』”’]$/.test(chars[end]))continue;
    if(end<n&&/[A-Za-z0-9]/.test(chars[end-1])&&/[A-Za-z0-9]/.test(chars[end]))continue;
    if(/[（【《「『]/.test(chars[end-1]))continue;
    for(let begin=end-1;begin>=0;begin--){
     let len=prefix[end]-prefix[begin];if(len>max)break;if(!Number.isFinite(dp[k-1][begin]))continue;
     let cost=((len-ideal)/sz)**2+(boundaries.has(end)?0:18);
     if(end<n&&/[，。；：、！？]/.test(chars[end-1]))cost-=4;
     const total=dp[k-1][begin]+cost;if(total<dp[k][end]){dp[k][end]=total;prev[k][end]=begin;}
    }
   }
   if(Number.isFinite(dp[count][n])){
    const ls=[];let e=n;for(let k=count;k>0;k--){let b=prev[k][e];ls.unshift(chars.slice(b,e).join(''));e=b;}bestLines=ls;
   }
  }
  result.push(...(bestLines||greedy));
 }return result;
}
let seq=0;
function text(s,str,x,y,w,sz=24,{color=C.ink,bold=false,align='left',maxlines=20,nowrap=false,lh=1.24,name='text'}={}){
 const lines=nowrap?[String(str)]:wrap(str,w-5,sz);
 if(lines.length>maxlines)throw new Error(`page ${s.__page} ${name} too many lines ${lines.length}>${maxlines}: ${str}`);
 if(nowrap&&width(str,sz)>w)throw new Error(`page ${s.__page} one-line overflow: ${str}`);
 const h=sz*lh*lines.length+4;
 if(y+h>679&&name!=='footer')throw new Error(`page ${s.__page} vertical overflow ${y+h}: ${str}`);
 const el=s.shapes.add({geometry:'textbox',name:`${name}-${++seq}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 el.text=lines.join('\n');el.text.style={fontSize:sz,typeface:FONT,color,bold,alignment:align,verticalAlignment:'top',autoFit:'none',wrap:'none',lineSpacing:lh,insets:{left:0,right:0,top:0,bottom:0}};
 ledger.push({page:s.__page,name,x,y,w,h,text:str,fontSize:sz,lines:lines.length});
 return h;
}
function box(s,x,y,w,h,fill=C.gray,line='none'){
 return s.shapes.add({geometry:'rect',name:'box-'+(++seq),position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1}});
}
function rule(s,x,y,w,color=C.rule){box(s,x,y,w,1,color);}
function block(s,items,x,y,w,sz=25,gap=29){
 for(const it of items){
  y+=text(s,it.label,x,y,w,32,{bold:true,maxlines:2,name:'subhead'})+8;
  y+=text(s,it.body,x,y,w,sz,{maxlines:6})+gap;
 }return y-gap;
}
function base(d){
 const s=deck.slides.add();s.__page=d.page;s.background.fill=C.white;
 text(s,d.chapter,64,23,900,18,{color:C.blue,bold:true,nowrap:true,name:'eyebrow'});
 if(!['cover','closing'].includes(d.kind)){
  text(s,d.title,64,67,1152,48,{bold:true,nowrap:true,name:'slide-title'});
  if(d.claim)text(s,d.claim,64,141,1152,26,{color:C.muted,maxlines:2,name:'claim'});
  rule(s,64,202,1152);
 }
 rule(s,64,677,1152);
 text(s,'人生管理系统 4.0  ·  设计说明',64,688,1020,16,{color:C.muted,nowrap:true,name:'footer'});
 text(s,String(d.page).padStart(2,'0')+' / '+data.length,1125,687,91,16,{color:C.muted,align:'right',nowrap:true,name:'footer'});
 let ns=d.notes||'';
 if(d.kind==='proactive')ns=ns.replace('这页要把运行设计与部署状态放在视觉上分开的区域。','运行设计与实际部署状态需要分别理解。');
 if(d.source_paths)ns+='\n设计来源：'+d.source_paths.map(v=>path.basename(v)).join('；');
 const sources=[...new Set((d.sources||[]).map(v=>v.startsWith('/root/')?'本项目设计文件：'+path.basename(v):v))];
 s.speakerNotes.textFrame.setText(ns+'\n\n[Sources]\n'+sources.map(v=>'- '+v).join('\n')+'\n[/Sources]');
 return s;
}
function nativeTable(s,headers,rows,{x=64,y=224,w=1152,h=414,widths=null,font=24}={}){
 const n=headers.length; widths=widths|| (n===2?[345,807]:n===3?[250,420,482]:[258,318,258,318]);
 const vals=[headers,...rows].map((r,ri)=>r.map((str,ci)=>wrap(String(str),widths[ci]-28,ri===0?27:font).join('\n')));
 const heights=vals.map((r,ri)=>Math.max(...r.map(v=>v.split('\n').length))*((ri===0?27:font)*1.2)+24);
 const total=heights.reduce((a,b)=>a+b,0);
 if(total>h+1)throw new Error(`page ${s.__page} table height ${total}>${h}`);
 const table=s.tables.add({rows:vals.length,columns:n,left:x,top:y,width:w,height:Math.max(total,h-25),columnWidths:widths,values:vals});
 table.borders.assign({color:C.rule,fill:C.rule,width:1});
 table.cells.block({row:0,column:0,rowCount:vals.length,columnCount:n}).assign({fill:C.white,textStyle:{fontSize:font,typeface:FONT,color:C.ink,autoFit:'none'},margins:{left:14,right:14,top:12,bottom:12}});
 table.cells.block({row:0,column:0,rowCount:1,columnCount:n}).assign({fill:C.gray,textStyle:{fontSize:27,typeface:FONT,bold:true,color:C.ink}});
 for(let i=0;i<vals.length;i++)table.rows[i].height=heights[i]+Math.max(0,(h-total)/vals.length);
 return table;
}
function lowerExample(s,example,boundary){
 rule(s,64,543,1152);
 text(s,'示例',64,556,90,28,{color:C.blue,bold:true,nowrap:true});
 text(s,example.replace(/^合成示例[:：]/,'合成：'),164,556,1052,22,{maxlines:2});
 text(s,'边界',64,614,90,28,{bold:true,nowrap:true});
 text(s,boundary,164,614,1052,22,{maxlines:2,color:C.muted});
}
function domain(s,d){
 const left=[{label:'维护的结果',body:d.result},{label:'观察与行动',body:d.observations.join('；')+'。\n'+d.actions.join('；')+'。'}];
 block(s,left,64,220,540,24,23);
 const right=[{label:'跨领域协作',body:d.dependencies.join('\n')},{label:'调用能力',body:d.modules.join('；')}];
 block(s,right,657,220,559,23,18);
 lowerExample(s,d.example,d.boundary);
}
function module(s,d){
 const alternating=Number(d.code.slice(1))%2===0;
 if(!alternating){
  text(s,'知识体系',64,219,465,32,{bold:true,nowrap:true});
  let y=267;
  for(const k of d.knowledge)y+=text(s,k,64,y,450,23,{maxlines:2})+6;
  text(s,d.stages,64,478,459,22,{maxlines:2,color:C.blue});
  let yy=219;
  for(const [label,body] of [['输入',d.input],['处理方法',d.method],['交付物',d.output]]){
   text(s,label,568,yy,648,32,{bold:true,nowrap:true});
   yy+=43;yy+=text(s,body,568,yy,648,23,{maxlines:3})+13;
  }
  if(yy>544)throw new Error('module process too tall '+d.page+' '+yy);
 }else{
  text(s,'知识体系',64,218,148,32,{bold:true,nowrap:true});
  text(s,d.knowledge.join('；'),237,220,979,23,{maxlines:3});
  const table=s.tables.add({rows:3,columns:2,left:64,top:302,width:1152,height:195,columnWidths:[174,978],values:[['输入',wrap(d.input,950,23).join('\n')],['处理方法',wrap(d.method,950,23).join('\n')],['交付物',wrap(d.output,950,23).join('\n')]]});
  table.borders.assign({color:C.rule,fill:C.rule,width:1});
  table.cells.block({row:0,column:0,rowCount:3,columnCount:2}).assign({fill:C.white,textStyle:{fontSize:23,typeface:FONT,color:C.ink},margins:{left:16,right:16,top:10,bottom:10}});
  table.cells.block({row:0,column:0,rowCount:3,columnCount:1}).assign({fill:C.gray,textStyle:{fontSize:28,bold:true}});
  text(s,d.stages,64,508,1152,22,{color:C.blue,maxlines:1});
 }
 lowerExample(s,d.example,d.boundary);
}
function three(s,d,start=234){
 const w=345, xs=[64,468,871];
 d.items.forEach((a,i)=>{
  text(s,String(i+1).padStart(2,'0'),xs[i],start,w,52,{bold:true,color:C.blue,nowrap:true});
  rule(s,xs[i],start+82,w);
  text(s,a.label,xs[i],start+113,w,32,{bold:true,maxlines:2});
  text(s,a.body,xs[i],start+205,w,25,{maxlines:6});
 });
}
function plainDiagramNode(s,id,label,detail,x,y,w,h,accent=false){
 // Entity boxes are native editable PowerPoint objects.
 const b=box(s,x,y,w,h,accent?C.pale:C.gray);
 text(s,label,x+17,y+16,w-34,32,{bold:true,align:'center',maxlines:2});
 if(detail)text(s,detail,x+17,y+63,w-34,23,{align:'center',maxlines:2,color:C.muted});
 return {id,b,x,y,w,h};
}
function diagram(s,d){
 let nodes,edges;
 if(d.diagram==='architecture'){
  nodes=[['u','用户价值与目标','底线、承诺与取舍',404,222,472,113,true],['c','人生总控','协调资源、阶段与版本',404,386,472,113,true],['m','23个能力模块','提供知识、方法与工具',64,386,270,113,false],['r','R01复核','查证据、反例与遗漏',946,386,270,113,false],['a','9个人生领域','行动与结果反馈',404,550,472,103,false]];
  edges=[['u','c','bottom','top'],['m','c','right','left'],['c','r','right','left'],['c','a','bottom','top']];
 }else if(d.diagram==='stages'){
  const labels=['S1 定义问题','S2 建立事实','S3 生成方案','S4 约束比较','S8 反馈更新','S7 授权执行','S6 建议取舍','S5 反驳复核'];
  const details=['目标与边界','证据与未知','真实备选','可行组合','新结果与版本','任务与真实状态','条件与用户选择','反例与检查'];
  nodes=labels.map((a,i)=>['n'+i,a,details[i],64+(i%4)*300,250+Math.floor(i/4)*212,252,126,i<4]);
  edges=[['n0','n1','right','left'],['n1','n2','right','left'],['n2','n3','right','left'],['n3','n7','bottom','top'],['n7','n6','left','right'],['n6','n5','left','right'],['n5','n4','left','right']];
  text(s,'证据不足回S2；方案不可行回S3；目标改变回S1。',64,622,1152,24,{color:C.blue,nowrap:true});
 }else{
  nodes=[['t','触发与数据接入','定时 / 事件；已授权来源',64,246,340,141,true],['c','总控与决策引擎','领域、方法与复核按需参与',470,246,340,141,true],['o','通知与行动接口','建议、真实选择与实际执行',876,246,340,141,true],['s','持久个人状态','目标、事实、快照、问题、建议、行动与结果',270,485,740,129,false]];
  edges=[['t','c','right','left'],['c','o','right','left'],['c','s','bottom','top']];
  text(s,'四类基础设施：触发、接入、持久状态、通知；均需实际部署验证。',64,634,1152,22,{color:C.muted,maxlines:1});
 }
 // Create arrow shafts first so the connectors sit behind entity nodes and labels.
 const ns=Object.fromEntries(nodes.map(n=>[n[0],n]));
 for(const [a,b,from,to] of edges){
  const A=ns[a],B=ns[b];
  if(from==='right'){
   const x=A[3]+A[5],xx=B[3],y=A[4]+A[6]/2;
   const ar=s.shapes.add({geometry:'rightArrow',position:{left:x+5,top:y-6,width:xx-x-10,height:12},fill:C.blue,line:{fill:'none',width:0}});
  }else if(from==='left'){
   const x=B[3]+B[5],xx=A[3],y=A[4]+A[6]/2;
   s.shapes.add({geometry:'leftArrow',position:{left:x+5,top:y-6,width:xx-x-10,height:12},fill:C.blue,line:{fill:'none',width:0}});
  }else{
   const x=A[3]+A[5]/2,y=A[4]+A[6],yy=B[4];
   s.shapes.add({geometry:'downArrow',position:{left:x-6,top:y+5,width:12,height:yy-y-10},fill:C.blue,line:{fill:'none',width:0}});
  }
 }
 if(d.diagram==='architecture'){
  s.shapes.add({geometry:'upArrow',position:{left:738,top:504,width:12,height:41},fill:C.blue,line:{fill:'none',width:0}});
 }
 nodes.forEach(n=>plainDiagramNode(s,...n));
}

function proactive(s,d){
 let y=222;
 for(let i=0;i<d.body.length;i++){
  text(s,String(i+1),64,y,40,28,{bold:true,color:C.blue,nowrap:true});
  y+=text(s,d.body[i],118,y,594,24,{maxlines:4})+26;
 }
 let r=222;
 r=block(s,[{label:'产品运行要求',body:d.design_plan.join('\n')},{label:'当前落实范围',body:d.deployed_facts.join('\n')}],772,r,444,23,24);
 if(d.states)text(s,'来源状态：'+d.states.join(' / '),64,563,1152,22,{maxlines:2,color:C.blue});
 rule(s,64,611,1152);
 text(s,d.boundary.replace('不加密催问','不增加催问频率'),64,628,1152,22,{maxlines:2,color:C.muted});
}

for(const d of data){
 const s=base(d);
 switch(d.kind){
  case 'cover':
   text(s,'人生管理系统',64,210,1152,80,{bold:true,nowrap:true,name:'deck-title'});
   text(s,'4.0',64,311,1152,96,{bold:true,color:C.blue,nowrap:true,name:'deck-version'});
   text(s,d.claim,64,469,1152,32,{maxlines:1});
   text(s,d.subtitle,64,540,1050,25,{maxlines:2,color:C.muted});
   break;
  case 'closing':
   text(s,d.title,64,161,1152,56,{bold:true,nowrap:true,name:'deck-close'});
   text(s,d.claim,64,291,1070,34,{maxlines:3});
   text(s,d.items.join('  ·  '),64,538,1152,24,{maxlines:2,color:C.blue});
   break;
  case 'columns':
   block(s,d.left,64,232,537,26,35);block(s,d.right,657,232,559,26,35);
   if(d.bottom){rule(s,64,585,1152);text(s,d.bottom,64,606,1152,23,{color:C.blue,maxlines:2});}
   break;
  case 'three':three(s,d);break;
  case 'table':{
   let widths=null;
   if(d.page===40)widths=[186,640,326];
   if(d.page===43)widths=[264,423,465];
   if(d.page===84)widths=[270,294,294,294];
   nativeTable(s,d.headers,d.rows,{widths,font:d.headers.length===4?23:24,h:423});break;}
  case 'formula':
   text(s,d.formula,64,230,1152,38,{bold:true,color:C.blue,maxlines:1});
   d.items.forEach((a,i)=>{text(s,a.label,64,344+i*97,180,32,{bold:true,nowrap:true});text(s,a.body,278,350+i*97,938,25,{maxlines:2});});
   break;
  case 'domain':domain(s,d);break;
  case 'module':module(s,d);break;
  case 'diagram':diagram(s,d);break;
  case 'proactive':proactive(s,d);break;
  case 'sources':{
   let y=223;
   for(const [title,desc,url] of d.references){
    const titleShape=s.shapes.add({geometry:'textbox',position:{left:64,top:y,width:1152,height:42},fill:'none',line:{fill:'none',width:0}});
    titleShape.text=title;titleShape.text.style={fontSize:29,typeface:FONT,bold:true,color:C.blue,wrap:'none',autoFit:'none',insets:{left:0,right:0,top:0,bottom:0}};
    titleShape.text.get(title).link={uri:url,isExternal:true};
    text(s,desc,64,y+47,1152,24,{maxlines:1,color:C.muted});y+=108;
   }break;}
  default:throw new Error(d.kind);
 }
}

await fs.writeFile(path.join(ROOT,'authored-objects.json'),JSON.stringify(ledger,null,2));
await fs.writeFile(path.join(ROOT,'deck-model.json'),JSON.stringify(deck.toProto()));
const pptx=await PresentationFile.exportPptx(deck);
await pptx.save(path.join(ROOT,'output','人生管理系统4.0-完整设计与模块详解.pptx'));
console.log('PPTX exported',data.length);
const only=process.env.RENDER_PAGES?new Set(process.env.RENDER_PAGES.split(',').map(Number)):null;
for(let i=0;i<deck.slides.items.length;i++){
 if(only&&!only.has(i+1))continue;
 const slide=deck.slides.items[i];
 const stem=`slide-${String(i+1).padStart(3,'0')}`;
 await fs.writeFile(path.join(ROOT,'rendered',stem+'.png'),new Uint8Array(await (await deck.export({slide,format:'png',scale:1})).arrayBuffer()));
 await fs.writeFile(path.join(ROOT,'rendered',stem+'.layout.json'),await (await slide.export({format:'layout'})).text());
 console.log('rendered',i+1);
}
console.log('all requested slides rendered');
