CHAIN_BREAKS=('CYCLE','MISSING_REFERENCE','REFERENCE_EXPIRED','REFERENCE_CONFLICT')
def destination(reasons):
    stops=[]
    if 'REVOKED' in reasons:stops.append('通知重测')
    if any(code in reasons for code in CHAIN_BREAKS):stops.append('溯源链复核')
    if 'INVALID_WINDOW' in reasons:stops.append('有效期复核')
    if 'OUT_OF_RANGE' in reasons:stops.append('量程复核')
    return '/'.join(stops) or '退回复核'
def apply(ctx):
     rows=[]
     for r in ctx['measurements']:
         chain=ctx['chains'][r['cert']];reasons=[]
         if not r['window_valid']:reasons.append('INVALID_WINDOW')
         if not r['range_valid']:reasons.append('OUT_OF_RANGE')
         if not chain['valid']:reasons.append(chain['code'])
         rows.append({'证书':r['cert'],'原始设备':r['device'],'合并归属':r['canonical'],'测量值_V':r['value_v'],'测量日':r['measured_at'],'结论':'可采用' if not reasons else '拒用','原因码':','.join(reasons) or 'ACCEPT','拒用去向':'—' if not reasons else destination(reasons),'行号':r['行号']})
     ctx['verdicts']=rows;ctx['balanced']=ctx['input_count']==len(ctx['measurements'])+ctx['duplicates']+len(ctx['quarantine'])
     return {'rows':rows,'metrics':[['可采用',sum(r['结论']=='可采用' for r in rows),'条'],['拒用',sum(r['结论']=='拒用' for r in rows),'条'],['行数守恒','相符' if ctx['balanced'] else '差异','']]}
