import pytest
from harnessproof.cli import main


def test_teacher_generation_requires_explicit_free_route_ack():
    with pytest.raises(SystemExit) as exc:
        main(['augment','--model','provider/possibly-paid-model','--max-seeds','1'])
    assert exc.value.code != 0
