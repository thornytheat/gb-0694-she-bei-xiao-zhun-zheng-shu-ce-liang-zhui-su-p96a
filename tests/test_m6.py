def test_measurement_conservation(ctx):assert ctx['balanced'] is True
def test_bad_certificate_rejected(ctx):assert next(r for r in ctx['verdicts'] if r['证书']=='C0002')['结论']=='拒用'
def test_good_certificate_accepted(ctx):assert next(r for r in ctx['verdicts'] if r['证书']=='C0001')['结论']=='可采用'
def test_out_of_range_reason(ctx):assert 'OUT_OF_RANGE' in next(r for r in ctx['verdicts'] if r['证书']=='C0007')['原因码']
def test_expired_reason(ctx):assert next(r for r in ctx['verdicts'] if r['证书']=='END')['原因码']=='INVALID_WINDOW'
def test_verdict_source_lines(ctx):assert all(r['行号']>=2 for r in ctx['verdicts'])
def test_partition(ctx):assert sum(r['结论']=='可采用' for r in ctx['verdicts'])+sum(r['结论']=='拒用' for r in ctx['verdicts'])==42

def test_verdict_carries_both_identities(ctx):
    row=next(r for r in ctx['verdicts'] if r['证书']=='C0001')
    assert row['原始设备']=='D0001' and row['合并归属']=='D0001'
    assert all('原始设备' in r and '合并归属' in r for r in ctx['verdicts'])
def test_rejection_destination(ctx):
    by_cert={r['证书']:r for r in ctx['verdicts']}
    assert by_cert['C0007']['拒用去向']=='量程复核'
    assert by_cert['END']['拒用去向']=='有效期复核'
    assert by_cert['C0024']['拒用去向']=='通知重测'
    assert '溯源链复核' in by_cert['C0002']['拒用去向'] and '有效期复核' in by_cert['C0002']['拒用去向']
    assert by_cert['C0001']['拒用去向']=='—'

