from pathlib import Path


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"


def test_build_uploads_one_verified_candidate_wheel() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "id: candidate" in workflow
    assert 'candidate_wheels=("$RUNNER_TEMP"/compas-occ-dist/*.whl)' in workflow
    assert "${#candidate_wheels[@]} -ne 1" in workflow
    assert "*-py3-none-any.whl" in workflow
    assert "name: candidate-linux-py312" in workflow
    assert workflow.count("name: candidate-linux-py312") == 1
    assert "path: ${{ steps.candidate.outputs.wheel }}" in workflow
    assert "if-no-files-found: error" in workflow
    assert "retention-days: 7" in workflow


def test_candidate_upload_uses_an_immutable_action() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1" in workflow
    assert workflow.count("uses: actions/upload-artifact@") == 1
    assert "uses: actions/upload-artifact@v" not in workflow
