// Fixed public data source only. Never substitute site visits or SNS views for podcast plays.
import {snapshot, sourceUrl} from './lib/goal-snapshot.mjs';
export function parseGoal(csv, now = new Date()) {
  const rows=[];let row=[],field='',quoted=false;
  for(let i=0;i<csv.length;i++) { const c=csv[i];
    if(c==='"'){if(quoted&&csv[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}
    else if(c===','&&!quoted){row.push(field);field='';}
    else if(c==='\n'&&!quoted){row.push(field.replace(/\r$/,''));rows.push(row);row=[];field='';}
    else field+=c;
  }
  if(quoted)throw Error('Malformed CSV');
  if(field||row.length){row.push(field.replace(/\r$/,''));rows.push(row);}
  const header=rows[0]?.map(s=>s.replace(/^\uFEFF/,'').trim()).join(',');
  if(rows.length!==2||rows[1].length!==3||header!=='現在の再生数,目標,最終更新')throw Error('Unexpected sheet');
  const number=s=>{s=s.normalize('NFKC').trim().replaceAll(',','');if(!/^\d+$/.test(s))throw Error('Invalid count');const n=Number(s);if(!Number.isSafeInteger(n)||n>1e12)throw Error('Invalid count');return n;};
  const current=number(rows[1][0]),target=number(rows[1][1]),updated=rows[1][2].trim();
  const date=updated.match(/^(\d{4})[./-](\d{1,2})[./-](\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?$/);
  if(!target||!date)throw Error('Invalid goal');
  const iso=`${date[1]}-${date[2].padStart(2,'0')}-${date[3].padStart(2,'0')}T${(date[4]||'0').padStart(2,'0')}:${date[5]||'00'}:00+09:00`;
  const at=new Date(iso);if(!Number.isFinite(+at)||at>now)throw Error('Invalid measurement date');
  const local=new Date(+at+9*3600000);if(local.getUTCMonth()+1!==Number(date[2])||local.getUTCDate()!==Number(date[3]))throw Error('Invalid calendar date');
  return {current,target,updated,measured_at:iso,source:'公開目標シート',source_type:'sheet_snapshot',metric:'総再生回数',is_stale:(now-at)>14*86400000};
}
export async function getGoal(fetcher=fetch) {
  try {
    const response=await fetcher(sourceUrl,{signal:AbortSignal.timeout(8000)});
    if(!response.ok)throw Error('Sheet unavailable');
    const csv=await response.text();if(csv.length>10000)throw Error('Sheet too large');
    return {...parseGoal(csv),fallback:false};
  } catch {return {...snapshot,is_stale:true,fallback:true};}
}
export default async function(request) {
  if(request.method!=='GET')return new Response('Method not allowed',{status:405,headers:{Allow:'GET'}});
  const data=await getGoal();
  return Response.json(data,{headers:{'Cache-Control':'public, max-age=900, stale-while-revalidate=3600','X-Content-Type-Options':'nosniff'}});
}
