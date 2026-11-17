from harnessproof.quality import quality_report


def test_gate_detects_too_small_training_set():
    rows = {
        'train': [{'prompt':'Create a shot', 'completion':'{}'}],
        'valid': [{'prompt':'Compare results','completion':'{}'}],
        'test': [{'prompt':'Retrieve evidence','completion':'{}'}],
    }
    meta = {
        'train': [{'family':'one', 'action':'answer','taxonomy':'no_tool_needed','prompt':'Create a shot'}],
        'valid': [{'family':'two', 'action':'retrieve','taxonomy':'retrieval','prompt':'Compare results'}],
        'test': [{'family':'three','action':'clarify','taxonomy':'clarification','prompt':'Retrieve evidence'}],
    }
    report=quality_report(rows,meta,mode='publish')
    assert not report['passed']
    assert any('training_size' in failure for failure in report['failures'])


def test_gate_detects_cross_split_family_leakage():
    rows={s:[{'prompt':s,'completion':'{}'}] for s in ('train','valid','test')}
    meta={'train':[{'family':'same','action':'answer','taxonomy':'a','prompt':'hello'}],
          'valid':[{'family':'same','action':'answer','taxonomy':'a','prompt':'world'}],
          'test':[{'family':'different','action':'answer','taxonomy':'a','prompt':'again'}]}
    report=quality_report(rows,meta,mode='pilot')
    assert not report['passed']
    assert 'family_leakage' in report['failures']


def test_pilot_gate_allows_small_but_valid_dataset():
    rows={s:[{'prompt':s,'completion':'{}'}] for s in ('train','valid','test')}
    meta={s:[{'family':s,'action':'answer','taxonomy':'a','prompt':s}] for s in rows}
    assert quality_report(rows,meta,mode='pilot')['passed']
