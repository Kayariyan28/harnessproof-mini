---
name: Cloud Fine-tune
 description: Run and compare full, LoRA and QLoRA student-model fine-tuning on free browser Colab or Kaggle NVIDIA GPUs with fixed datasets and logged metrics.
---

# Cloud Fine-tune

1. Verify browser free GPU and its quota; do not switch to paid accelerator or enable billing. Open `notebooks/cloud_gpu_lab.ipynb` in Colab/Kaggle.
2. Execute CPU data gates before training. Use identical `train.jsonl`, `valid.jsonl`, held-out `test.meta.jsonl`, model ID, random seed and evaluation count for every run.
3. Default base `Qwen/Qwen2.5-0.5B-Instruct` (small enough for a free T4 in common configurations, but check actual memory). Install `requirements-cloud.txt` only on cloud GPU runtime.
4. Run baseline+QLoRA: `python -m scripts.cloud_train --mode qlora --steps 40 --eval-max 18`; run baseline+LoRA: `--mode lora` separately if time remains. Full-layer `--mode full` is optional and stores no giant checkpoint by default.
5. Do NOT mislabel adapter tuning as full model; QLoRA is frozen 4-bit model plus trainable LoRA adapters, and full is non-adapter weight tuning.
6. Compare `runs/cloud/*/summary.json` outputs; inspect invalid JSON and tool/route mistakes, not just loss.
7. Stop on OOM, package incompatibility, exhausted quota, or degraded results. Document exact crash and minimal tested repair; do not assume accelerator availability.
8. Do not publish `runs/` artifacts to GitHub. If adapter release is approved, review base license and upload only adapter + model card to user-controlled Hugging Face repo, with provenance and test results.

Important: `scripts/cloud_train.py` is a real script but GPU execution is not proven until notebook logs and metrics are captured. Inference uses `scripts/cloud_harness.py` with the adapter.
