from app.domain import equivalence,volts
from decimal import Decimal
def test_missing_isolated(ctx): # TRAP-07
    assert any(q['原因码']=='MISSING' for q in ctx['quarantine'])
def test_device_code_preserved(ctx): # TRAP-08
    assert ctx['measurements'][1]['device']=='D0001'
def test_conflict_certificate_flag(ctx): # TRAP-14
    assert ctx['certs']['C0002']['conflicted'] is True
def test_alias_order_independent(): # TRAP-22
    rows=[{'device':'B','alias':'A'},{'device':'C','alias':'B'}];assert equivalence(rows)==equivalence(list(reversed(rows)))
def test_duplicate_not_add(ctx):assert ctx['duplicates']==1
def test_millivolt_conversion():assert volts('5000','mV')==Decimal('5')
def test_canonical_alias(ctx):assert ctx['measurements'][1]['canonical']=='D0001'


def test_invalid_measurement_alias_cannot_pollute_good_device(raw):
    import csv,io
    from app.pipeline import calculate
    records=list(csv.DictReader(io.StringIO(raw)));bad={**records[1],'alias':'D0003','value':'N/A'}
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(bad));writer.writeheader();writer.writerows(records+[bad])
    result=calculate(out.getvalue())
    assert result['certs']['C0003']['canonical']=='D0003'
    assert next(r['结论'] for r in result['verdicts'] if r['证书']=='C0003')=='可采用'

HEADER='cert,device,alias,parent,valid_from,valid_to,minimum,maximum,unit,revoked,measured_at,value,measure_unit,version\n'
ROOT='ROOT,REF-001,标准源,,2025-01-01,2028-01-01,0,1000,V,no,2026-06-01,100,V,1\n'
def test_corrected_code_intercepts_overlap_by_merged_identity(): # TRAP-26
    from app.pipeline import calculate
    text=HEADER+ROOT+ \
        'CA,D300,,ROOT,2026-01-01,2026-09-01,0,10,V,no,2026-03-01,5,V,1\n' \
        'CB,D300X,D300,ROOT,2026-07-01,2027-01-01,0,10,V,no,2026-10-01,5,V,1\n'
    result=calculate(text)
    ca=next(m for m in result['measurements'] if m['cert']=='CA');cb=next(m for m in result['measurements'] if m['cert']=='CB')
    assert ca['device']=='D300' and ca['canonical']=='D300' and ca['attribution']=='原始'
    assert cb['device']=='D300X' and cb['canonical']=='D300' and cb['attribution']=='合并'
    assert ca['device']!=cb['device'] # 沿用原编码查不出同机重叠
    assert ca['window_valid'] is False and cb['window_valid'] is False # 按合并归属拦截
    row=next(r for r in result['stages']['2']['rows'] if r['证书']=='CB')
    assert row['原始设备']=='D300X' and row['合并归属']=='D300' and row['归属状态']=='合并'

def test_switch_failure_rolls_back_to_original(): # TRAP-27
    from app.pipeline import calculate
    text=HEADER+ROOT+ \
        'CX,D100,,ROOT,2026-01-01,2027-01-01,0,10,V,no,2026-06-01,5,V,1\n' \
        'CX,D100,,ROOT,2026-01-01,2027-06-01,0,10,V,no,2026-06-01,5,V,1\n' \
        'CY,D200,D100,ROOT,2026-01-01,2027-01-01,0,10,V,no,2026-06-01,5,V,1\n'
    result=calculate(text)
    cy=next(m for m in result['measurements'] if m['cert']=='CY')
    assert cy['canonical']=='D200' and cy['attribution']=='回滚'
    assert cy['window_valid'] is True # 回滚后不被冲突身份拦截
    row=next(r for r in result['stages']['2']['rows'] if r['证书']=='CY')
    assert row['原始设备']=='D200' and row['合并归属']=='D200' and row['归属状态']=='回滚'
    assert next(m[1] for m in result['stages']['2']['metrics'] if m[0]=='回滚归属')==1

def test_sample_attribution_is_original(ctx):
    assert all(m['attribution']=='原始' for m in ctx['measurements'])
    assert next(m[1] for m in ctx['stages']['2']['metrics'] if m[0]=='回滚归属')==0
